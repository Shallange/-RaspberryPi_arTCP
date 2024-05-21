import socket
import struct
import serial 
import threading
import crcmod.predefined
from enum import Enum
from queue import Queue, Empty
import ssl
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Server configuration settings from environment variables
HOST = os.getenv('HOST', '0.0.0.0')  # Network host interface
PORT = int(os.getenv('PORT'))  # Port to listen on
SSL_CERT_PATH = os.getenv('SSL_CERT_PATH')  # Path to the SSL certificate
SSL_KEY_PATH = os.getenv('SSL_KEY_PATH')  # Path to the SSL private key
SERIAL_PORT = os.getenv('SERIAL_PORT')  # Serial port for Arduino connection
SERIAL_BAUD = int(os.getenv('SERIAL_BAUD'))  # Baud rate for serial communication


# Setup SSL context
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile=SSL_CERT_PATH, keyfile=SSL_KEY_PATH)
connections = []

# Define Enums for commands
class LEDColor(Enum):
    """Enumeration for LED colors."""
    GREEN = 'green'
    BLUE = 'blue'

class LEDAction(Enum):
    """Enumeration for LED actions."""
    ON = 'on'
    OFF = 'off'

class SystemStatus(Enum):
    """Enumeration for system status identifiers."""
    QUERY_STATUS = 'querystatus'
    ACKNOWLEDGE = 'acknowledge'
    ERROR = 'error'

# Setup CRC calculation
def calculate_crc(data):
    """
    Calculate the CRC16 checksum of the given data.
    
    Args:
        data (str): Data for which the checksum is calculated.
    
    Returns:
        str: CRC16 checksum, represented as a hexadecimal string.
    """
    crc16 = crcmod.predefined.Crc('crc-16')
    crc16.update(data.encode('utf-8'))
    return crc16.hexdigest()

# Function to format commands with appended CRC for integrity checks
def format_command(action, value):
    """
    Format a command string by appending a CRC checksum for integrity.
    
    Args:
        action (str): Action type of the command.
        value (str): Value associated with the action.
    
    Returns:
        bytes: The encoded command with appended CRC checksum.
    """
    base_command = f"{action}-{value}"
    crc_value = calculate_crc(base_command)
    full_command = f"{base_command}-{crc_value}\n"
    return full_command.encode()  # Encoding to bytes since it will be sent over serial

# Message class for packing and unpacking data
class Message:
    """
    Base class for handling messages between the server and Arduino devices.
    """
    def __init__(self, data=''):
        self.data = data

    def create_packet(self):
        """
        Create a packet for transmission. Must be implemented by subclasses.
        """
        data_bytes = self.data.encode('utf-8')
        data_length = len(data_bytes)
        return struct.pack('<B', data_length) + data_bytes

    @staticmethod
    def parse_packet(packet_bytes):
        """
        Parse packet data from bytes to a string.
        
        Args:
            packet_bytes (bytes): The packet data in bytes.
        
        Returns:
            str: The parsed data.
        """
        data_length = struct.unpack('<B', packet_bytes[:1])[0]
        data = packet_bytes[1:1 + data_length].decode('utf-8')
        return data

# Message queue for handling Arduino commands
arduino_queue = Queue()

# Processor thread for sending commands to the Arduino
def arduino_command_processor():
    """
    Process commands intended for the Arduino, sending them over the serial connection.
    """
    while True:
        try:
            # Blocking get with timeout to allow graceful shutdown
            command = arduino_queue.get(timeout=1)
            print(f"command fetched from que:{command}")
            ser.write(command)  # Send command to Arduino via serial
            arduino_queue.task_done()
        except Empty:
            continue

# Thread setup for Arduino command processing
arduino_thread = threading.Thread(target=arduino_command_processor)
arduino_thread.start()

# Lock for managing access to connection list in multi-threaded context
list_lock = threading.Lock()

# Handle client connections, receive data, and respond
def handle_client(conn, addr):
    """
    Manages communications with a connected client, processing incoming data, 
    executing commands, and sending responses.

    Args:
        conn (socket.socket): Socket object representing the client connection.
        addr (tuple): Address tuple containing the host and port of the client.

    This function continuously receives data from the client, parses it,
    and sends a response after processing the command. It handles clean-up
    and removal of the connection upon disconnection or error.
    """
    print(f"Connection from(this is addr-> {addr} established.")
    global connections, list_lock
    with list_lock:
        connections.append((conn,addr))

        print_current_connections("Added")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            command = Message.parse_packet(data)
            print(f"Received command: {command}")
            formatted_command = format_command(command.split('-')[0], command.split('-')[1])
            print(f"formmated command:{formatted_command}")
            arduino_queue.put(formatted_command)  # Enqueue the formatted command

            response_packet = Message(SystemStatus.ACKNOWLEDGE.value).create_packet()
            conn.sendall(response_packet)
    except Exception as e:
        print(f"An error occurred: {e}")
        error_response = Message(SystemStatus.ERROR.value).create_packet()
        conn.sendall(error_response)
    finally:
        with list_lock:
            try:
                remove_connection(conn, addr)
                print_current_connections("Updated after removal")
            except Exception as e:
                print(f"Error removing connection {addr}: {e}")
        try:
            conn.close()
        except Exception as e:
            print(f"Error closing connection {addr}: {e}")

def print_current_connections(action):
    """
    Print the current active connections.
    
    Args:
        action (str): Description of the action prompting this log.
    """
    print(f"{action} connection. Current connections:")
    for conn, addr in connections:
        print(f"Connection from {addr}")

def remove_connection(conn, addr):
    """
    Safely removes a client connection from the active connections list.

    Args:
        conn (socket.socket): Client socket to remove.
        addr (tuple): Client address.
    
    Ensures thread-safe removal and logs the updated connections list.
    """
    global connections, list_lock
    with list_lock:
        try:
            connections.remove((conn, addr))
            print(f"Removed {addr} from the connections list.")
            print_current_connections("Updated after removal")
        except ValueError:
            print(f"Failed to remove {addr}; may already have been removed.")


# Initialize serial communication with Arduino
ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
ser.flush()

# Set up TCP server to listen for incoming connections
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
print(f"TCP Server listening on {HOST}:{PORT}")

# Main loop to accept connections
try:
    while True:
        conn, addr = s.accept()
        secure_conn = context.wrap_socket(conn, server_side=True)
        threading.Thread(target=handle_client, args=(secure_conn, addr)).start()
except KeyboardInterrupt:
    arduino_queue.put(None)  # Signal to stop the Arduino processing thread
    arduino_thread.join()
    s.close()
    print("Server shutdown initiated")
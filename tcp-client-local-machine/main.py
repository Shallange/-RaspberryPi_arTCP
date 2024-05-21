import socket
import struct
import sys
from enum import Enum
import ssl
import os
from dotenv import load_dotenv
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
                             QGridLayout, QGroupBox, QHBoxLayout)

# Load environment variables
load_dotenv()

# Environment variables
SERVER_IP = os.getenv('SERVER_IP')
SERVER_PORT = int(os.getenv('SERVER_PORT'))
SSL_CERT_PATH = os.getenv('SSL_CERT_PATH')

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


# Base class for all message types
class Message:
    def create_packet(self):
        """Should be implemented by subclasses to create specific packets for sending commands."""
        raise NotImplementedError

    @staticmethod
    def parse_command(command):
        """Parse a command string into a specific message type based on defined actions and statuses."""
        if '-' not in command:
            return None
        command_type, arg = command.split('-', 1)
        command_type = command_type.upper()  # Convert to uppercase for enum comparison
        arg = arg.upper()  # Convert to uppercase for enum comparison

        # Determine if the command matches known enums and create the appropriate message
        color = LEDColor[command_type].value if command_type in LEDColor.__members__ else None
        action = LEDAction[arg].value if arg in LEDAction.__members__ else None

        if color and action:
            return LEDMessage(color, action)
        elif command_type == 'SERVO':
            return ServoMessage(arg)
        elif command_type in SystemStatus.__members__:
            return StatusMessage(command_type, arg)
        return None


# Specific message types
class LEDMessage(Message):
    def __init__(self, color, action):
        self.color = color
        self.action = action
    
    def create_packet(self):
        """Create a packet containing the command to control an LED."""
        command = f"{self.color}-{self.action}"
        data = command.encode('utf-8')
        data_length = len(data)
        return struct.pack('<B', data_length) + data
    
class ServoMessage(Message):
    """Create a packet containing the command to control a servo motor."""
    def __init__(self, angle):
        self.angle = angle
    
    def create_packet(self):
        command = f"servo-{self.angle}"
        data = command.encode('utf-8')
        data_length = len(data)
        return struct.pack('<B', data_length) + data
    
class StatusMessage(Message):
    def __init__(self, status_type, info=''):
        self.status_type = status_type
        self.info = info

    def create_packet(self):
        """Create a packet containing a system status update."""
        command = f"{self.status_type}-{self.info}"
        data = command.encode('utf-8')
        data_length = len(data)
        return struct.pack('<B', data_length) + data
    
# Main window class for the GUI
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUi()
        self.setupConnection()

    def initUi(self):
        """Initialize the user interface for the Raspberry Pi controller."""
        self.setWindowTitle("Raspberry Pi Controller")
        self.setGeometry(100, 100, 500, 300)
        layout = QVBoxLayout()

        grid_layout = QGridLayout()

        # Setup groups for different control buttons
        # Green Button Group
        green_group = QGroupBox("Green Button")
        green_layout = QHBoxLayout()
        self.green_on_button = QPushButton('On', self)
        self.green_off_button = QPushButton('Off', self)
        green_layout.addWidget(self.green_on_button)
        green_layout.addWidget(self.green_off_button)
        green_group.setLayout(green_layout)
        # Blue Button Group
        blue_group = QGroupBox("Blue Button")
        blue_layout = QHBoxLayout()
        self.blue_on_button = QPushButton('On', self)
        self.blue_off_button = QPushButton('Off', self)
        blue_layout.addWidget(self.blue_on_button)
        blue_layout.addWidget(self.blue_off_button)
        blue_group.setLayout(blue_layout)

        # Servo Group
        servo_group = QGroupBox("Servo")
        servo_layout = QHBoxLayout()
        self.servo_button_0 = QPushButton('0', self)
        self.servo_button_45 = QPushButton('45', self)
        self.servo_button_90 = QPushButton('90', self)
        self.servo_button_135 = QPushButton('135', self)
        self.servo_button_180 = QPushButton('180', self)
        servo_layout.addWidget(self.servo_button_0)
        servo_layout.addWidget(self.servo_button_45)
        servo_layout.addWidget(self.servo_button_90)
        servo_layout.addWidget(self.servo_button_135)
        servo_layout.addWidget(self.servo_button_180)
        servo_group.setLayout(servo_layout)

        # Layout configuration
        grid_layout.addWidget(green_group, 0, 0)
        grid_layout.addWidget(blue_group, 0, 1)
        grid_layout.addWidget(servo_group, 0, 2)
        central_widget = QWidget()
        central_widget.setLayout(grid_layout)
        self.setCentralWidget(central_widget)

        # Connect buttons to their respective functions
        self.green_on_button.clicked.connect(lambda: self.send_command('green-on'))
        self.green_off_button.clicked.connect(lambda: self.send_command('green-off'))
        self.blue_on_button.clicked.connect(lambda: self.send_command('blue-on'))
        self.blue_off_button.clicked.connect(lambda: self.send_command('blue-off'))
        self.servo_button_0.clicked.connect(lambda: self.send_command('servo-0'))
        self.servo_button_45.clicked.connect(lambda: self.send_command('servo-45'))
        self.servo_button_90.clicked.connect(lambda: self.send_command('servo-90'))
        self.servo_button_135.clicked.connect(lambda: self.send_command('servo-135'))
        self.servo_button_180.clicked.connect(lambda: self.send_command('servo-180'))
    
    def setupConnection(self):
        """Establish a secure SSL connection to the server."""
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations(SSL_CERT_PATH)
        context.check_hostname = True
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.secure_socket = context.wrap_socket(self.client_socket, server_hostname=SERVER_IP)
        self.secure_socket.connect((SERVER_IP, SERVER_PORT))

    def send_command(self, command):
        """Send a command to the server and print the response."""
        message = Message.parse_command(command)
        if message:
            packet = message.create_packet()
            self.secure_socket.sendall(packet)
            response = self.secure_socket.recv(1024)
            print(f"Response: {response.decode('utf-8')}")
        else:
            print("Invalid command.")

    def closeEvent(self, event):
        """Handle the GUI closure event by closing the socket connection."""
        self.secure_socket.close()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
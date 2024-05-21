# Server Module

This server module orchestrates the core operations for our system, managing SSL/TLS encrypted communications, processing client commands, and interfacing with the Arduino device.

## Setup Instructions

### Prerequisites
Ensure that Python 3.x is installed on your system.

### Install Dependencies
Navigate to the server's directory and install the necessary Python libraries:

```bash
pip install -r requirements.txt
```

### Run the Server
Start the server to begin listening for client commands:

```bash
python main.py
```

## Features

- **Secure Communication**: Utilizes SSL/TLS encryption to secure data transmissions between the client and the server.
- **Command Processing**: Intercepts and processes commands from the client, relaying them to the Arduino for hardware interactions.

## Configuration

### SSL Certificate and Key
Ensure the SSL certificate (`cert.crt`) and key (`cert.key`) are stored in the `/etc/ssl/mykeysCert/` directory to facilitate encrypted communications. For detailed instructions on generating and setting up the SSL certificate, see the [SSL Certificate Generation section](../README.md#ssl-certificate-generation) in the root README. Ensure proper permissions are set for these files to maintain security.


### Server README
In the **Serial Port Settings** section, provide guidance on determining the correct serial port if it's not predefined, which can be particularly useful during initial setups or when troubleshooting:


### Serial Port Settings

Configure the serial port settings within the server code to match the connection parameters of the Arduino device. This typically includes setting the correct port and baud rate. If you are unsure of your Arduino's serial port on your Raspberry Pi or server machine, you can discover it by listing all connected serial devices. Run the following command:

```bash
ls /dev/tty*
```

## Important Note

- **SSL Certificate Sharing**: It is crucial to copy the `cert.crt` file from the server's certificate directory to the client's directory to enable the SSL handshake. Ensure this file is securely transferred and stored.

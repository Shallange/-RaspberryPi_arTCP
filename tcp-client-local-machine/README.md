# Client Module

This module handles the user interface and communication with the server to control Arduino-connected devices via a network.

![Client GUI](/images/gui.png "Client GUI")

The GUI shown above is designed for user-friendly interaction with the TCP server to send commands and view responses.

## Setup
- Ensure Python 3.x is installed.
- Install dependencies: `pip install -r requirements.txt`
- Run the client with: `python main.py`

## Features
- Secure SSL/TLS communication with the server.
- User interface for controlling LED and servo motor states.

## Configuration
- Ensure the SSL certificate (`cert.crt`) from the server is placed in the same directory as the client script for proper SSL handshake.

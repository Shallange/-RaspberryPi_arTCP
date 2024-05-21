# ArTCP

## Table of Contents
- [Project Structure](#project-structure)
- [Project Overview](#project-overview)
- [Components List](#components-list)
- [Features](#features)
- [Setup Instructions](#setup-instructions)
  - [Arduino Setup Instructions](./data-source-arduino/README.md)
  - [TCP Server Setup on Raspberry Pi](./tcp-server-raspberrypi/README.md)
  - [TCP Client Interface](./tcp-client-local-machine/README.md)
- [Running the Applications](#running-the-applications)
- [SSL Certificate Generation](#ssl-certificate-generation)
- [Setting Permissions for Certificate Files](#setting-permissions-for-certificate-files)
- [Understanding File Permissions](#understanding-file-permissions)
- [Sources and Tools](#sources-and-tools)
- [Collaborators](#collaborators)


This project enables control of Arduino-connected devices via a network, allowing commands to be sent securely from a client application through a server that processes and forwards these commands to an Arduino device.

## Project Structure

- **Server**: Contains the server application that handles communication and command processing.
- **Client**: Contains the client application with a GUI for sending commands to the server.
- **Arduino**: Contains the Arduino sketch that executes commands received from the server.

# Project Overview

This flowchart illustrates the communication process between the client, server, and Arduino components of our project:

![Project Flowchart](/images/flowchart.jpg "Project Flowchart")

### Components List

Ensure you have all the necessary components before starting the setup:

- **Arduino Uno R3**: The microcontroller board that executes the Arduino sketch.
- **Breadboard**: For temporary prototyping and circuit assembly without soldering.
- **Servo Motor**: Used for precise control of mechanical movement.
- **LEDs (Green and Blue)**: Indicators for system status and outputs.
- **Resistors**:
  - 220 ohm / 560 ohm: For LED current limiting to prevent damage.
- **Jumper Wires**: For making connections between the components on the breadboard.
- **Raspberry Pi 4**: Serves as the TCP server and handles network communications.

## Features

- Secure communication between client and server using SSL/TLS.
- GUI on the client for easy interaction with the hardware.
- Arduino sketch handles direct hardware manipulation based on commands received.
- Command integrity ensured via CRC checks.

## Setup Instructions
Follow the setup instructions in each module's README for detailed steps on configuring and running the components:

- [Arduino Setup Instructions](./data-source-arduino/README.md)
- [TCP Server Setup on Raspberry Pi](./tcp-server-raspberrypi/README.md)
- [TCP Client Interface](./tcp-client-local-machine/README.md)


### Running the Applications
1. **Server**: Navigate to the `Server` directory, install dependencies, and run `main.py`.
2. **Client**: Navigate to the `Client` directory, ensure the SSL certificate is in place(Refer to the [SSL Certificate Generation Guide](#ssl-certificate-generation)), install dependencies, and run `main.py`.
3. **Arduino**: Upload the `main.ino` sketch to an Arduino device using the Arduino IDE.

## SSL Certificate Generation

SSL certificates must be generated to secure communication between the client and server. Refer to the `Server/README.md` for detailed instructions on generating a self-signed certificate.
**Generation of a Self Signed Certificate**

Generation of a self-signed SSL certificate involves a simple 3-step procedure:

**STEP 1**: Create the server private key

```bash
openssl genrsa -out cert.key 2048
```
- **genrsa** = Is used to generate an RSA private key
- **-out cert.key** = This specifies he filename to write the newly created private ket to. in this case the file name is `cert.key`
- **2048** = This specifies the size of the key in bits. `2048 bits` is commonly used and considered secure. Larger keys provide more security but require more computational power to use.

**STEP 2**: Create the certificate signing request (CSR)

```bash
openssl req -new -key cert.key -out cert.csr
```
- **req** =This command primarily deals with `**C**ertificate **S**igning **R**equests` (CSRs). It can also create self-signed certificates if required, which is useful for generating a test certificate.
- **-new** = THis specifies that a new CSR is being generated
- **-key cert.key** = This option specifies the private key to use, Here it uses the ‘cert.key’ file generated earlier
- **-out cert.csr** = This creates the output filename for the CSR, this file will be named cert.csr

**STEP 3**: Sign the certificate using the private key and CSR

```bash
openssl x509 -req -days 3650 -in cert.csr -signkey cert.key -out cert.crt
```
- **x509:** This command is for X.509 Certificate Data Management. Here it is used to create a self-signed certificate.
- **-req:** This tells OpenSSL that a CSR is being input and a certificate is to be output.
- **-days 3650:** This specifies the validity of the certificate. Here, the certificate is set to be valid for 3650 days, which is approximately 10 years.
- **-in cert.csr:** This designates the input file, which is the CSR file created in Step 2.
- **-signkey cert.key:** This specifies the private key to sign the certificate with, using the private key generated in Step 1.
- **-out cert.crt:** This specifies the output filename for the certificate. The certificate will be written to a file named **`cert.crt`**.
>*"Congratulations! You now have a self-signed SSL certificate valid for 10 years."*

## Setting Permissions for Certificate Files

To secure your certificate files, especially when located in a directory accessible by other users or applications, you should set appropriate file permissions. This prevents unauthorized access to these sensitive files. Run the following commands in your terminal:

```bash
sudo chown <YOUR_USERNAME> /etc/ssl/<YOUR_FOLDERr>/cert.crt
sudo chown <YOUR_USERNAME> /etc/ssl/<YOUR_FOLDERr>/cert.key
sudo chmod 600 /etc/ssl/<YOUR_FOLDER>/cert.key
sudo chmod 644 /etc/ssl/<YOUR_FOLDER>/cert.crt
```
## Understanding File Permissions

In Unix-like operating systems, file permissions control the actions that a user can perform on a file. These permissions are represented as three digits in octal format, with each digit representing different user classes:

- **Owner**: The user who owns the file.
- **Group**: Users who are part of the file's group.
- **Others**: All other users.

The permissions are defined as follows:
- `4` stands for "read",
- `2` stands for "write",
- `1` stands for "execute",
- `0` stands for "no permission".

These values are summed for each user class:

### Permission `600`
- **Owner**: `6` (read and write) – The owner can read and write the file.
- **Group**: `0` (no permission) – The group members cannot access the file in any way.
- **Others**: `0` (no permission) – Others cannot access the file in any way.

This setting is commonly used for sensitive files, like private keys, where you want to ensure that only the owner can read and write the file, and no other user can access it.

### Permission `644`
- **Owner**: `6` (read and write) – The owner can read and write the file.
- **Group**: `4` (read) – Group members can only read the file.
- **Others**: `4` (read) – Others can only read the file.

This setting is often used for public files, like server certificates, where the file needs to be widely readable but should only be modifiable by the owner.
## Packaging with PyInstaller

To distribute the client application as a standalone executable, especially when SSL/TLS security is required, you need to package the application along with its SSL certificate. PyInstaller can be used to create a single executable that includes both your Python script and the necessary certificate files.

### Steps to Package Your Application

1. **Prepare Your Application**: Ensure your Python script (`main.py`) and the SSL certificate (`cert.crt`) are in the same directory.

2. **Package with PyInstaller**:
   - Navigate to the directory containing `main.py`.
   - Run the following command to create a single executable:

  ```bash
   pyinstaller --onefile --add-data 'cert.crt:.' main.py
  ```

   This command instructs PyInstaller to bundle `main.py` and `cert.crt` into a single executable file. The `--add-data` option specifies additional files or directories to include, and the `--onefile` flag packages everything into one executable.

### What Happens Next?

- **Build Directory**: Contains temporary files used during the build process.
- **Dist Directory**: Contains the final standalone executable (`main.exe`).

### Distributing the Application

- The executable in the `dist` directory (`main.exe`) is the file you'll distribute. This executable contains all the necessary components, including the Python interpreter and your certificate, allowing it to run as a standalone application on any compatible system without requiring a separate Python installation.

- Ensure that the executable and the SSL certificate are properly configured to maintain SSL/TLS functionality when deployed.

By following these steps, you can create a packaged version of your client application that includes all necessary dependencies and security certificates, ready for distribution and use on other systems without further setup.

## Sources and Tools

This project utilizes a variety of resources and libraries. Below are links to the sources and tools that have been instrumental in the development and operation of this project:

- **CRC Library for Arduino**: [GitHub - RobTillaart/CRC](https://github.com/RobTillaart/CRC)
- **Packaging PyQt Applications for Windows with PyInstaller**: [Python GUIs - Packaging PyQt5/Pyside2 Applications](https://www.pythonguis.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/)
- **Useful Scripts for PyQt Development**: [GitHub Gist - PyQt Related Scripts](https://gist.github.com/taoyuan/39d9bc24bafc8cc45663683eae36eb1a)
- **Digital Certificate Management on Windows**: [DigiCert - Import Intermediate and Root Certificates](https://knowledge.digicert.com/solution/how-to-import-intermediate-and-root-certificates-using-mmc)
- **Python Socket Programming**: [Python Documentation - socket](https://docs.python.org/3/library/socket.html)
- **Python struct Module for Binary Data**: [Python Documentation - struct](https://docs.python.org/3/library/struct.html)
- **Predefined CRC Algorithms**: [crcmod.predefined - Documentation](https://crcmod.sourceforge.net/crcmod.predefined.html)
- **Managing App Security and Permissions on MacOS**: [Der Flounder - Clearing Quarantine from Downloaded Apps](https://derflounder.wordpress.com/2012/11/20/clearing-the-quarantine-extended-attribute-from-downloaded-applications/)
- **Understanding UART for Device Communication**: [Rohde & Schwarz - Digital Oscilloscopes](https://www.rohde-schwarz.com/us/products/test-and-measurement/essentials-test-equipment/digital-oscilloscopes/understanding-uart_254524.html)


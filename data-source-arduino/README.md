# Arduino Module

This module contains the Arduino sketch (`main.ino`) responsible for executing hardware-level commands received from the server.

## Setup Instructions

- **Loading the Sketch:**
  - Open the Arduino IDE.
  - Load the `main.ino` file from the `data-source-arduino` directory.

- **Connecting the Hardware:**
  - Connect the Arduino board to your computer via USB.

- **Uploading the Sketch:**
  - Compile and upload the sketch to your Arduino board using the Arduino IDE.

## Required Libraries

- **Servo Library:** Utilized for controlling servo motors. Ensure this library is installed through the Arduino IDE’s Library Manager.

- **CRC16 Library:** Essential for generating and verifying CRC values to enhance the integrity of commands. This library is crucial for ensuring that commands received and executed by the Arduino match those sent by the server, maintaining data integrity across the communication channel. The CRC parameters used here are specifically configured to align with those defined in the server's CRC calculation, ensuring consistent and reliable verification.

  For a detailed understanding of the CRC algorithms used, particularly how they are predefined in server-side implementations, refer to the [crcmod.predefined documentation on CRC algorithms](https://crcmod.sourceforge.net/crcmod.predefined.html).

## Features

- **Command Execution:** Receives and executes commands to control LEDs and a servo motor.

- **Integrity Checks:** Utilizes CRC checks to verify the integrity of incoming commands, ensuring they have not been tampered with.

## Hardware Setup

![Arduino Setup](/images/arduino.png "Arduino Setup")

The image above displays the setup of the Arduino connections used in this project.


### LED Connections

- **Green LED**: Connect the anode (longer leg) of the Green LED to GPIO pin 4 through a 220-ohm resistor. Connect the cathode (shorter leg) directly to the ground (GND).
- **Blue LED**: Connect the anode of the Blue LED to GPIO pin 5 through a 560-ohm resistor. Connect the cathode directly to the ground.

### Servo Motor Connection

- **Servo Motor**: Attach the servo motor's signal cable to GPIO pin 6. Connect the VCC (power) and GND (ground) cables of the servo motor to a 5V power supply, ensuring the power supply is capable of handling the servo's current requirements.

### Safety and Stability

- **Secure Connections**: Make sure all connections are secure. Loose connections can lead to intermittent issues that are hard to debug.
### Appropriate Powering

- **Power Requirements**: Ensure the Arduino is powered appropriately to handle the connected devices. For this project, the current draw of the servo and LEDs is within the capacity that the Arduino's onboard voltage regulator can handle. Therefore, using an external power supply is not necessary.

Ensure that all wiring and power connections are secure. This avoids any potential issues such as voltage drops or fluctuations that could affect the performance of the connected devices.

### Verifying Device Connection

To check the connection of the Arduino to a Raspberry Pi or similar device, you can list the connected serial devices. This helps in identifying the correct serial port for communication. Run the following command in the terminal:

```bash
ls /dev/tty*
```
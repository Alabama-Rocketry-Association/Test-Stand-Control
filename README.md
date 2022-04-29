# Test-Stand-Control

## General Info
This is the control system for the liquid rocket test stand. It includes functionality for reading sensor data, actuating valves, and adjusting the pressure regulators.

## Setup Overview
In order to operate the test stand, you will need two computers: a local one, for sending I/O, and a controller, which will be connected to I2C and GPIO components on the test stand.

The computers communicate via Ethernet, and need static IP addresses to function. Assign the ip `10.0.0.1/24` to the controller, and `10.0.0.x/24` to the local computer. `x` can be any number between 2 and 255. Connect the two computers directly with an ethernet cable, and you should be able to ping the controller from the local computer:

```
ping 10.0.0.1
```

On the test stand, clone the project to a local directory, and then run main.py:
```
git clone https://github.com/Alabama-Rocketry-Association/Test-Stand-Control
cd Test-Stand-Control
python3 Server/main.py
```
On the local computer, clone the project to a local directory, and then run host.py:
```
git clone https://github.com/Alabama-Rocketry-Association/Test-Stand-Control
cd Test-Stand-Control
python3 GUI\ files/main.py
```

If GUI functionality is not necessary, a cli-only interface can be ran with:
```
python3 GUI\ files/host.py
```

## Usage
The local computer will be able to send commands to the controller. The connection can be tested with `ping`, and a list of all commands can be displayed with `help`

Some commands require parameters, which should be separated with a space. For example, `lox_inc 50` will turn the LOX pressure regulator knob clockwise 50 degrees.

If the connection between the computers is broken, the programs will automatically reconnect when/if the connection is restored, and the current state of the system is saved.

## Controller Configuration
The controller is a Raspberry Pi 4, running Ubuntu Server.

To set up, start by imaging Ubuntu Server on an SD card using the Raspberry Pi Imager App. Preconfigure the hostname and username, and enable SSH.

Next, edit the network-configuration file on the SD partition, and configure the following settings:
```
ethernets:
  eth0:
    addresses:
      - 10.0.0.1/24
wifis:
  wlan0:
    access-points:
      "My-Guest-Wifi": {}
      "My-Home-Wifi":
        password: "myHomeWifiPassword"
      dhcp4: yes
```

After formatting, insert the SD card into the pi and boot it. We will need to connect to the pi over SSH in order to make software configurations. Directly connect an ethernet cable between your personal computer and the Raspberry Pi. In your network configurations, create a new ethernet configuration with a static IP address of `10.0.0.x/24`, where `x` is any number between 2 and 255.

Now connect to the Pi with:
```
ssh ara@10.0.0.1
```

Here, we are using `ara` as our username, as well as the hostname of the Pi.

Upon sucessful connection, you will have shell access to the Raspberry Pi. If wifi is still not functioning, you can reconfigure the network by editing this file:
```
sudo nano /etc/netplan/50-cloud-init.yaml
```

Next, disable auto-updating, and manually updatae and install all the necessary libraries:
```
sudo dpkg-reconfigure unattended-upgrades
sudo apt-get update && sudo apt-get upgrade
```
# biocontrol
## access
- pi@biocontrol.local
- pw: adamchuk
- sudo raspi-config
  - Enable I2C, SPI, Serial (diable for login shell, enable serial)
## Installations
- sudo apt update && sudo apt upgrade
- sudo apt install python3-pip
- sudo apt install git
- sudo apt install i2c-tools
- sudo apt-get -y install hostapd dnsmasq

### python library
- pip install smbus
- pip install pip install RPI-control-center
- pip install astral

### UI(Node-red)
- sudo apt install build-essential git curl
- bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)

# biocontrol
## about
Biocontrol is the realization of the RPi-control-center python library where the various modules are combinec to make powerful RPI powered bio-environmental controllers. This repo serves as a template to be forked and turned into various flavors for specific uses and configurations. Backend is powered by a biocontroller.py script and enabled through the biocontrol service file.

```
sudo systemctl enable /path/to/biocontrol.service
sudo systemctl start biocontrol
```

everything else is frills
- autohotspot mode
- typically a node-red user interface and controls
- mqtt for iot communication


## access
- default hostname: pi@biocontrol.local
- default password: adamchuk
- sudo raspi-config
- Enable I2C, SPI, Serial (diable for login shell, enable serial)

## Installations
```
sudo apt update && sudo apt upgrade
sudo apt install python3-pip
sudo pip install virtualenv
sudo apt-get install -y mosquitto mosquitto-clients
```

### python library
```
pip install pip install RPI-control-center
sudo apt-get install -y mosquitto mosquitto-clients
```
### UI(Node-red)
```
sudo apt install build-essential git curl
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)
```
- Pallets:
  - node-red-dashboard
  - node-red-contrib-ui-led
- default username: admin
- default password: adamchuk
- node-red node console   :1880/admin
- dashboard  :1880/

### Autohotspot
- This aspect of the system was enabled by the work done by [raspberryconnect.com](https://www.raspberryconnect.com/projects/65-raspberrypi-hotspot-accesspoints/157-raspberry-pi-auto-wifi-hotspot-switch-internet)


### MQTT for node-red api communication
- [mosquitto MQTT Brocker](https://mosquitto.org/)
```
sudo systemctl enable mosquitto.service
```

- default port: 1883
- config file: /etc/mosquitto/mosquitto.conf
- python library: paho-mqtt

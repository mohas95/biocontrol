import time
from rpi_control_center import controls
from rpi_sensor_monitors import monitors
import paho.mqtt.client as mqtt
import threading
import json

# MQTT settings
BROKER_ADDRESS = "localhost"
PORT = 1883
KEEP_ALIVE_INTERVAL = 60
MQTT_CO2_TOPIC = "monitors/CO2"
MQTT_TEMP_TOPIC = "monitors/TEMP"
MQTT_RELAY_TOPIC = "monitors/RELAY"

MQTT_SUBSCRIPTION_TOPICS= ['controls/RELAY']


# global objects
relay_config = {
        "relay1":{'pin':26, 'state':False, 'config':'no'},
        "valve":{'pin':20, 'state':False, 'config':'no'},
        "relay3":{'pin':21, 'state':False, 'config':'no'},
}

relay_group = controls.relay_engine( relay_config=relay_config,
                            label='relays', 
                            api_dir='./api/', 
                            log_dir='./log/',
                            refresh_rate=1)

co2_sensor = monitors.K30_CO2( serial_device = "/dev/ttyS0",
                                baudrate=9600, label='k30_CO2',
                                api_dir='./api/',
                                log_dir='./log/',
                                refresh_rate=1)

temp_sensor = monitors.BME680( label='BME680',
                                api_dir='./api/',
                                log_dir='./log/',
                                refresh_rate=1)

# Callbacks
def on_disconnect(client, userdata, rc):
    print("Disconnected with result code " + str(rc))

def on_publish(client, userdata, mid):
    print("Message Published")

def on_message(client, userdata, message):
    global relay_group, co2_sensor, temp_sensor

    message.payload = message.payload.decode("utf-8")

    print(f"Received message '{message.payload}' on topic '{message.topic}'")

    if message.topic == 'controls/RELAY':
        print("got message")
        # relay_group.change_duty_cycle(30 if message.payload=="on" else 0)
        # print(f'{water_pump.label} dutycycle set to {message.payload}')

    else:
        print(f'invalid topic {message.topic}')

def on_connect(client, userdata, flags, rc):
    global MQTT_SUBSCRIPTION_TOPICS
    print(f"Connected with result code {rc}")
    
    for topic in MQTT_SUBSCRIPTION_TOPICS:
        client.subscribe(topic)  # Add this line to subscribe

# Threaded Functions for simultaneous publishing

STOP_FLAG = False


def publish_sensor_to(topic, device, client, rate=10,):
    global STOP_FLAG

    while not STOP_FLAG:
        payload = device.sensor_readings
        client.publish(topic, json.dumps(payload,indent=4))
        time.sleep(rate)

def publish_control_to(topic, device, client, rate=10,):
    global STOP_FLAG


    while not STOP_FLAG:
        payload = device.control_readings
        client.publish(topic, json.dumps(payload,indent=4))
        time.sleep(rate)

# Signal handler 
def signal_handler(signum, frame):
    global STOP_FLAG
    print("Received SIGTERM, preparing to exit...")
    STOP_FLAG = True

signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':

    
    co2_sensor.start()
    temp_sensor.start()          
    relay_group.start()
    
    # Create MQTT client
    client = mqtt.Client(CLIENT_ID)

    # Assign callbacks
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    client.on_message = on_message

    # Connect to broker
    client.connect(BROKER_ADDRESS, PORT, KEEP_ALIVE_INTERVAL)
    client.loop_start()  # Start the loop in the background

    #threads
    t1 = threading.Thread(target=publish_sensor_to, args = (MQTT_CO2_TOPIC, co2_sensor, client, 1))
    t2 = threading.Thread(target=publish_sensor_to, args = (MQTT_TEMP_TOPIC, temp_sensor, client, 1))
    t3 = threading.Thread(target=publish_control_to, args = (MQTT_RELAY_TOPIC, relay_group, client, 1))

    t1.start()
    t2.start()
    t3.start()


    try:
        while not STOP_FLAG:
            time.sleep(1)

    except KeyboardInterrupt:  # Stop the script with Ctrl+C
        print("Disconnecting from broker...")
        STOP_FLAG=True

    finally:
        co2_sensor.stop()
        temp_sensor.stop()
        relay_group.stop()

        t1.join()
        t2.join()
        t3.join()


        client.loop_stop()  # Stop the loop
        client.disconnect()  # Disconnect from the broker
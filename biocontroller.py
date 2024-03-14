import time
from rpi_control_center import controls
from rpi_sensor_monitors import monitors

if __name__ == '__main__':
    relay_config = {
            "relay1":{'pin':26, 'state':False, 'config':'no'},
            "relay2":{'pin':20, 'state':False, 'config':'no'},
            "relay3":{'pin':21, 'state':False, 'config':'no'},
    }

    relay_group1 = controls.relay_engine( relay_config=relay_config,
                                label='test_relays', 
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
    
    co2_sensor.start()
    temp_sensor.start()          
    relay_group1.start()

    ######### You can put any code because this function is non-blocking
    try:
        while True:
            time.sleep(5)
            relay_group1.set_relay_state('relay1',True)
            time.sleep(5)
            relay_group1.set_relay_state('relay2',True)
            time.sleep(5)
            relay_group1.set_relay_state('relay3',True)
            time.sleep(5)
            relay_group1.set_relay_state('relay1',False)
            time.sleep(5)
            relay_group1.set_relay_state('relay2',False)
            time.sleep(5)
            relay_group1.set_relay_state('relay3',False)
    except:
        relay_group1.stop()
        co2_sensor.stop()
        temp_sensor.stop()
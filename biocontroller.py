import time
from rpi_control_center import controls

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
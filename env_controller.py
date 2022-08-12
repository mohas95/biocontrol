import time
from rpi_control_center import GPIO_engine

default_relay_config = {
        "1":{'name':'socket', 'pin':20, 'state':False},
}

control_box = GPIO_engine.BulkUpdater(
                                        config_file = './relay_config.json',
                                        api_dir = './api',
                                        default_config = default_relay_config,
                                        refresh_rate = 1
                                      )
control_box.start()
######### You can put any code because this function is non-blocking
try:
    while True:
        time.sleep(5)
except:
    control_box.stop()

import time
from rpi_control_center import GPIO_engine
from monitors import BME680
import math
import json
import threading
import datetime
import time
import os
import os.path
import sys
import csv
from astral import LocationInfo
from astral.sun import sun
import pytz
from tzwhere import tzwhere



########################################################### Wrapper/decorator & Helper functions
def threaded(func):
	"""start and return a thread of the passed in function. Threadify a function
	 with the @threaded decorator"""
	def wrapper(*args,**kwargs):
		thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=False)
		thread.start()
		return thread
	return wrapper

def push_to_api(api_file,data):
	"""Push data in json format to an api file"""
	last_update = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
	data["last updated"] = last_update
	with open(api_file,"w") as f:
		f.write(json.dumps(data,indent=4))

def delete_file(file):
	"""delete file"""
	if os.path.exists(file):
		os.remove(file)
		print(f'{file} removed')
	else:
		print(f'{file} Does not exist')
		pass

def initiate_file(dir, filename):
	"""This function checks whether a directory exists and if not creates it"""
	try:
		if not os.path.exists(dir):
			os.makedirs(dir)
		file_location = dir+filename
		return file_location
	except:
		print('could not create file path, exiting')
		sys.exit()

######################################################################## Classes
default_params = {'thresholds':{'temp_low':22, 'temp_high':24, 'rh_low':50, 'rh_high':95},
                  'geolocation':{'name':'Montreal', 'region':'Quebec', 'longitude':45.5019, 'latitude':73.5674}
                  }

class Biocontroller():
    """ """

    def __init__(self, label='Biocontroller', params=default_params, relay_pin=20, api_dir='./api/', refresh_rate=1):
        self.label = label
        self.status = None
        self.default_relay_config = {"1":{'name':'Control Socket', 'pin':relay_pin, 'state':False}}
        self.relay_socket = None
        self.env_sensor = None
        self.readings_api = initiate_file(api_dir, label +'_realtime_readings.json')

        self.thresholds = params['thresholds']
        self.geolocation = params['geolocation']
        self.sun_info = get_sun_info()

        self.refresh_rate = refresh_rate
        self.thread = None

    def get_sun_info(self):
        tzwhere = tzwhere.tzwhere()
        timezone_str = tzwhere.tzNameAt(self.geolocation['longitude'], self.geolocation['latitude'])
        location = LocarionInfo(self.geolocation['name'],
                                self.geolocation['region'],
                                timezone_str,
                                self.geolocation['longitude'],
                                self.geolocation['latitude']
                                )
        s = sun(location.obeserver, date = datetime.date.today(),tzinfo=location.timezone)

        self.sun_info = s

        return self.sun_info

    def begin(self):
        self.relay_socket = GPIO_engine.BulkUpdater(
                                                config_file = './relay_config.json',
                                                api_dir = './api',
                                                default_config = self.default_relay_config,
                                                refresh_rate = self.refresh_rate
                                              )
        self.relay_socket.start()

        self.env_sensor = BME680()
        self.env_sensor.start()



if __name__ == '__main__':
    control_box= Biocontroller()
    print(control_box.sun_info)






######### You can put any code because this function is non-blocking
# try:
#     while True:
#         data = env_sensor.sensor_readings
#
#
#         if data['Temperature,C']
#
#         time.sleep(1)
# except:
#     control_box.stop()
#     control_box.stop()

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
import astral
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
default_thresholds_params = {'temp_low':22, 'temp_high':24, 'rh_low':50, 'rh_high':95, 'longitude': 'latitude'}

class Biocontroller():
    """ """

    def __init__(label='Biocontroller', relay_pin=20, api_dir='./api/', refresh_rate=1):
        self.label = label
        self.status = None
        self.default_relay_config = {"1":{'name':'Control Socket', 'pin':relay_pin, 'state':False}}
        self.relay_socket = None
        self.env_sensor = None
        self.readings_api = initiate_file(api_dir, label +'_realtime_readings.json')

        self.temp_thresh_low = None
        self.temp_thresh_high = None
        self.rh_thresh_low = None
        self.rh_thresh_high = None
        self.sunset = None
        self.sunrise = None



        self.refresh_rate = refresh_rate
        self.thread = None

    def begin():
        self.relay_socket = GPIO_engine.BulkUpdater(
                                                config_file = './relay_config.json',
                                                api_dir = './api',
                                                default_config = self.default_relay_config,
                                                refresh_rate = self.refresh_rate
                                              )
        self.relay_socket.start()

        self.env_sensor = BME680()
        self.env_sensor.start()











######### You can put any code because this function is non-blocking
try:
    while True:
        data = env_sensor.sensor_readings


        if data['Temperature,C']

        time.sleep(1)
except:
    control_box.stop()
    control_box.stop()

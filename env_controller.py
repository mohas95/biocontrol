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
				  'geolocation':{'name':'Montreal', 'region':'Quebec', 'latitude':45.5019, 'longitude':-73.561668}
				  }

class Biocontroller():
	""" """

	def __init__(self, label='Biocontroller', params=default_params, relay_pin=20, api_dir='./api/', refresh_rate=1):
		self.label = label
		self.status = None
		self.default_relay_config = {"1":{'name':'Control Socket', 'pin':relay_pin, 'state':False}}
		self.relay_socket = None
		self.env_sensor = None
		self.readings = None

		self.thresholds = params['thresholds']
		self.geolocation = params['geolocation']
		self.sun_info, self.timezone = self.get_sun_info()

		self.readings_api = initiate_file(api_dir, label +'_realtime_readings.json')
		self.refresh_rate = refresh_rate
		self.thread = None

	def set_thread(func):
		"""Decorator Function in order to set the thread property of the object to the output of a function returning  a thread object"""
		def wrapper(self):
			self.thread = func(self)
			print(f'thread object for {self.label} set as {self.thread}')
			return self.thread
		return wrapper

	def get_readings(self):
		""" """
		data = {'label' : self.label +'_realtime_readings.json',
				self.env_sensor.label : {'status':'active' if self.env_sensor.status else 'inactive',
										 'sensor_data': self.env_sensor.sensor_readings
										 },
				'sockets' : {'status': 'active' if self.relay_socket.status else 'inactive'}
				}

		for relay_id, relay in self.relay_socket.relay_dict.items():
			data['sockets'] = { relay_id : {'name':relay.name,
											'pin':relay.pin,
											'state': 'ON' if relay.state else 'OFF'
											}
								}
		self.readings = data

		return self.readings

	def check_conditions(self):
		""" """
	def relay_socket_on(self):
		""" """
		self.relay_socket.update_config_file("1",True)

	def relay_socket_off(self):
		""" """
		self.relay_socket.update_config_file("1",False)


	def get_sun_info(self):
		""" """
		tz= tzwhere.tzwhere()
		timezone_str = tz.tzNameAt(self.geolocation['latitude'], self.geolocation['longitude'])
		location = LocationInfo(self.geolocation['name'],
								self.geolocation['region'],
								timezone_str,
								self.geolocation['latitude'],
								self.geolocation['longitude']
								)
		sun_info = sun(location.observer, date = datetime.date.today(),tzinfo=location.timezone)

		self.sun_info = sun_info
		self.timezone = location.timezone

		return self.sun_info, self.timezone

	def begin(self):
		""" """
		self.relay_socket = GPIO_engine.BulkUpdater(
												config_file = './relay_config.json',
												api_dir = './api',
												default_config = self.default_relay_config,
												refresh_rate = self.refresh_rate
											  )
		self.relay_socket.start()

		self.env_sensor = BME680()
		self.env_sensor.start()

	@set_thread
	@threaded
	def start(self):
		""" """
		self.status = True
		print(f'Starting {self.label} process')
		self.begin()

		while self.status:
			data = self.get_readings()
			push_to_api(self.readings_api,data)
			time.sleep(self.refresh_rate)

		print(f'Stopinf {self.label} process')
		self.relay_socket.stop()
		self.env_sensor.stop()
		print(f'Stopped {self.label} process')

	def stop(self):
		print(f'attempting to stop {self.label} process')
		self.status = None




if __name__ == '__main__':
	control_box= Biocontroller()
	print(control_box.sun_info)
	print(type(control_box.timezone))

	control_box.start()
	time.sleep(100)
	control_box.stop()







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

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
	def __init__(self, label='Biocontroller', default_params=default_params, relay_pin=20, api_dir='./api/', refresh_rate=1):
		self.label = label
		self.status = None
		self.readings_api = initiate_file(api_dir, label +'_realtime_readings.json')
		self.params_config_api = initiate_file(api_dir, label +'_config.json')
		self.refresh_rate = refresh_rate

		self.default_relay_config = {"1":{'name':'Control Socket', 'pin':relay_pin, 'state':False}}
		self.relay_socket = None
		self.env_sensor = None
		self.readings = None
		self.default_params = default_params

		self.thresholds = None
		self.geolocation = None
		self.sun_info = None
		self.timezone = None

		self.thread = None

	def set_thread(func):
		"""Decorator Function in order to set the thread property of the object to the output of a function returning  a thread object"""
		def wrapper(self):
			self.thread = func(self)
			print(f'thread object for {self.label} set as {self.thread}')
			return self.thread
		return wrapper

	def update_conditions(self):
		""" """
		params = self.load_params(self.params_config_api)

		self.thresholds = params['thresholds']
		if params['geolocation']!= self.geolocation: #or params['date']!=:
			print('geolocation has been update, getting sun information')
			self.geolocation = params['geolocation']
			self.get_sun_info()
		else:
			self.geolocation = params['geolocation']


	def check_conditions(self):
		""" """
		self.update_conditions()
		temp_low, temp_high, rh_low, rh_high = self.thresholds['temp_low'], self.thresholds['temp_high'], self.thresholds['rh_low'], self.thresholds['rh_high']

		sunrise = self.sun_info['sunrise']
		sunset = self.sun_info['sunset']
		env_sensor = self.readings[self.env_sensor.label]

		temp = env_sensor['sensor_data']['Temperature,C']
		rh = env_sensor['sensor_data']['Humidity,%RH']

		now = self.timezone.localize(datetime.datetime.now())


		if now > sunrise and now < sunset:
			if temp<temp_low and rh<rh_low:
				self.relay_socket_off()
			elif temp<temp_low and rh>rh_low and rh<rh_high:
				self.relay_socket_off()
			elif temp<temp_low and rh>rh_high:
				self.relay_socket_off()
			elif temp>temp_low and temp<temp_high and rh<rh_low:
				self.relay_socket_on()
			elif temp>temp_low and temp<temp_high and rh>rh_high:
				self.relay_socket_off()
			elif temp>temp_high and rh<rh_low:
				self.relay_socket_on()
			elif temp>temp_high and rh>rh_low and rh<rh_high:
				self.relay_socket_on()
			elif temp>temp_high and rh>rh_high:
				self.relay_socket_off()
			else:
				pass
		else:
			print(f'outside time bounds it is currently {now}, {sunrise} <-> {sunset}')
			self.relay_socket_off()


	def load_params(self, config_file):
		""" """
		if os.path.isfile(config_file):
			# print(f'Loading config file: {config_file}')
			with open(config_file, "r") as f:
				params = json.load(f)
		else:
			print(f'config file not found creating file with default parameters at: {config_file}')
			with open(config_file, "w") as f:
				params = self.default_params
				params['date'] = datetime.date.today().strftime()
				f.write(json.dumps(params,indent=4))

		return params

	def relay_socket_on(self,relay_id="1"):
		""" """
		if self.relay_socket.relay_dict[relay_id].state:
			pass
		else:
			self.relay_socket.update_config_file(relay_id,True)

	def relay_socket_off(self,relay_id="1"):
		""" """
		if self.relay_socket.relay_dict[relay_id].state:
			self.relay_socket.update_config_file(relay_id,False)
		else:
			pass


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
		self.timezone = pytz.timezone(location.timezone)

		return self.sun_info, self.timezone

	def get_readings(self):
		""" """
		data = {'label' : self.label +'_realtime_readings.json',
				self.env_sensor.label : {'status':'active' if self.env_sensor.status else 'inactive',
										 'sensor_data': self.env_sensor.sensor_readings
										 },
				'sockets' : {'status': 'active' if self.relay_socket.status else 'inactive'}
				}
		for relay_id, relay in self.relay_socket.relay_dict.items():
			data['sockets'][relay_id] = { 'name':relay.name,
										  'pin':relay.pin,
										  'state': 'ON' if relay.state else 'OFF'
										  }
		self.readings = data

		return self.readings

	def begin(self):
		""" """
		print('Starting all Processes')
		self.update_conditions()
		self.relay_socket = GPIO_engine.BulkUpdater(
												config_file = './relay_config.json',
												api_dir = './api',
												default_config = self.default_relay_config,
												refresh_rate = self.refresh_rate
											  )
		self.relay_socket.start()
		self.env_sensor = BME680()
		self.env_sensor.start()
		time.sleep(15)
		print('All processes started')

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

		print(f'Stoping {self.label} process')
		self.stop_processes()
		data = self.get_readings()
		push_to_api(self.readings_api, data)
		print(f'Stopped {self.label} process')

	def stop(self):
		print(f'attempting to stop {self.label} process')
		self.status = None

	def stop_processes(self):
		print('Stopping all processes')
		self.relay_socket.stop()
		self.env_sensor.stop()
		time.sleep(15)


if __name__ == '__main__':
	control_box= Biocontroller()

	control_box.start()
	time.sleep(60)
	print('starting condition checker')
	try:
		while True:
			control_box.check_conditions()
			time.sleep(1)

	except:
		print('stopping in 100 seconds')
		time.sleep(100)
		print(control_box.sun_info)
		print(type(control_box.timezone))
		control_box.stop()

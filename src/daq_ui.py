# daq_ui.py

from tkinter import Tk, LEFT, RIGHT, TOP, BOTTOM, BOTH, RAISED, IntVar, font
from tkinter.ttk import Frame, Label, Style
import redis
import time
import threading
import numpy as np

NO_DATA_VALUE = -9999

class DataManager():
	def __init__(self, redis_ip_add="127.0.0.1", redis_port=6379, update_freq=30):
		self.reading = False
		self.update_freq = update_freq
		self.redis_port = redis_port
		self.redis_ip_add = redis_ip_add
		# redis keys and values
		self.hpu_pressure_key = "utec::read::pressure::hpu"
		self.hpu_pressure = IntVar(value=NO_DATA_VALUE)
		self.hpu_pressure_label = "HPU Pressure"
		self.drill_pressure_key = "utec::read::pressure::drill"
		self.drill_pressure = IntVar(value=NO_DATA_VALUE)
		self.drill_pressure_label = "Drill Pressure"
		self.screwjack_pressure_key = "utec::read::pressure::screwjack"
		self.screwjack_pressure = IntVar(value=NO_DATA_VALUE)
		self.screwjack_pressure_label = "ScrewJack Pressure"
		self.fluid_pressure_key = "utec::read::pressure::fluid"
		self.fluid_pressure = IntVar(value=NO_DATA_VALUE)
		self.fluid_pressure_label = "Drill Fluid Pressure"
		self.screwjack_speed_key = "utec::read::linear_speed::screwjack"
		self.screwjack_speed = IntVar(value=NO_DATA_VALUE)
		self.screwjack_speed_label = "ScrewJack Speed"
		self.screwjack_position_key = "utec::read::position::screwjack"
		self.screwjack_position = IntVar(value=NO_DATA_VALUE)
		self.screwjack_position_label = "ScrewJack Position"
		self.screwjack_force_key = "utec::read::force::drill"
		self.screwjack_force = IntVar(value=NO_DATA_VALUE)
		self.screwjack_force_label = "ScrewJack Force"
		self.drill_speed_key = "utec::read::rotary_speed::drill"
		self.drill_speed = IntVar(value=NO_DATA_VALUE)
		self.drill_speed_label = "Drill Speed"
		self.drill_torque_key = "utec::read::torque::drill"
		self.drill_torque = IntVar(value=NO_DATA_VALUE)
		self.drill_torque_label = "Drill Torque"
		self.front_bearing_temp_key = "utec::read::temperature::front_bearing"
		self.front_bearing_temp = IntVar(value=NO_DATA_VALUE)
		self.front_bearing_temp_label = "Front Bearing temperature"
		self.rear_bearing_temp_key = "utec::read::temperature::rear_bearing"
		self.rear_bearing_temp = IntVar(value=NO_DATA_VALUE)
		self.rear_bearing_temp_label = "Rear Bearing temperature"
		# ui variables
		self.screwjack_position_offset = IntVar(value=0)
		# derived variables
		self.max_bearing_temp = IntVar(value=NO_DATA_VALUE)
		# units
		self.pressure_unit = "bar"
		self.linear_speed_unit = "in/min"
		self.rotary_speed_unit = "RPM"
		self.temperature_unit = "deg C"
		self.position_unit = "in"
		self.torque_unit = "Nm"
		self.force_unit = "kN"

		self.initDataDict()

	def startRead(self):
		# connect to redis
		self.reading = True
		# set thread with readThreaded method
		pass

	def stopRead(self):
		self.reading = False
		# stop read thread
		# disconnect from redis
		pass

	def readThreaded(self):
		while(self.reading):
			pass

	def readOnce(self):
		pass

	def initDataDict(self):
		self.dataDict = {
			self.hpu_pressure_key: self.hpu_pressure,
			self.drill_pressure_key: self.drill_pressure,
			self.screwjack_pressure_key: self.screwjack_pressure,
			self.fluid_pressure_key: self.fluid_pressure,
			self.screwjack_speed_key: self.screwjack_speed,
			self.screwjack_position_key: self.screwjack_position,
			self.screwjack_force_key: self.screwjack_force,
			self.drill_speed_key: self.drill_speed,
			self.drill_torque_key: self.drill_torque,
			self.front_bearing_temp_key: self.front_bearing_temp,
			self.rear_bearing_temp_key: self.rear_bearing_temp,
		}
		pass

class UIManager(Frame):
	def __init__(self, window, data_manager):
		super().__init__(window)
		self.data = data_manager
		self.max_temperature = 90 #deg C
		self.max_pressure = 105 #bar
		self.stall_speed = 0 # RPM or in/min
		self.max_screwjack_travel = 10 #in

		self.initUI()

	def initUI(self):
		'''
		ui has 3 frames:
		- critical frame: which has critical sensor readings: speed, pressure
		- sensor frame: which has all other sensors
		- user frame: which has buttons for user inputs
		'''
		self.master.title("UTEC Experiments UI")
		# self.style = Style()
		# self.style.configure("TLabel", foreground="red", background="white")

		# self.initSensorFrame2()
		self.initSensorFrame1()
		self.initCriticalFrame()

		self.pack(fill=BOTH, expand=True)

		# label1 = Label(self, text="Hello")#, style="TLabel")
		# label1.pack(side=TOP)

	def initCriticalFrame(self):
		self.critical_label_font = font.Font(size=48)
		self.critical_frame = Frame(self)

		self.addCriticalReadout(self.critical_frame, self.data.screwjack_speed_label, self.data.linear_speed_unit, self.data.screwjack_speed)
		self.addCriticalReadout(self.critical_frame, self.data.drill_speed_label, self.data.rotary_speed_unit, self.data.drill_speed)
		self.addCriticalReadout(self.critical_frame, self.data.hpu_pressure_label, self.data.pressure_unit, self.data.hpu_pressure)
		self.addCriticalReadout(self.critical_frame, self.data.screwjack_position_label, self.data.position_unit, self.data.screwjack_position)

		self.critical_frame.pack(side=LEFT, fill=BOTH, expand=True)

	def initSensorFrame1(self):
		self.sensor_frame1 = Frame(self)
		self.sensor_label_font = font.Font(size=24)

		self.addSensorReadout(self.sensor_frame1, self.data.drill_torque_label, self.data.torque_unit, self.data.drill_torque)
		self.addSensorReadout(self.sensor_frame1, self.data.screwjack_force_label, self.data.force_unit, self.data.screwjack_force)
		self.addSensorReadout(self.sensor_frame1, self.data.drill_pressure_label, self.data.pressure_unit, self.data.drill_pressure)
		self.addSensorReadout(self.sensor_frame1, self.data.screwjack_pressure_label, self.data.pressure_unit, self.data.screwjack_pressure)
		self.addSensorReadout(self.sensor_frame1, self.data.front_bearing_temp_label, self.data.temperature_unit, self.data.front_bearing_temp)
		self.addSensorReadout(self.sensor_frame1, self.data.rear_bearing_temp_label, self.data.temperature_unit, self.data.rear_bearing_temp)

		self.sensor_frame1.pack(side=BOTTOM, fill=BOTH, expand=True)

	def addCriticalReadout(self, parent_frame, labelstr, unitstr, variable):
		sensor_info_label = Label(
			parent_frame,
			text='%s (%s)'% (labelstr, unitstr),
		)
		sensor_info_label.pack(side=TOP, pady=(10,0))
		sensor_data_label = Label(
			parent_frame,
			textvariable=variable,
			font=self.critical_label_font
		)
		sensor_data_label.pack(side=TOP)

	def initSensorFrame2(self):
		self.sensor_frame2 = Frame(self)
		self.sensor_label_font = font.Font(size=24)

		# self.addSensorReadout(self.sensor_frame2, self.data.fluid_pressure_label, self.data.pressure_unit, self.data.fluid_pressure)

		self.sensor_frame2.pack(side=BOTTOM, fill=BOTH, expand=True)

	def addSensorReadout(self, parent_frame, labelstr, unitstr, variable):
		sensor_frame = Frame(parent_frame)
		sensor_info_label = Label(
			sensor_frame,
			text='%s (%s)'% (labelstr, unitstr),
		)
		sensor_info_label.pack(side=TOP, padx=10)
		sensor_data_label = Label(
			sensor_frame,
			textvariable=variable,
			font=self.sensor_label_font
		)
		sensor_data_label.pack(side=TOP)
		sensor_frame.pack(side=LEFT)

	def alertUser(self, message):
		#TODO: play alert sound
		pass

	def clearAlert(self):
		#TODO: stop playing alert sound
		pass

	def startLogging(self):
		pass

	def stopLogging(self):
		pass

	def zeroScrewjackPosition(self):
		pass

	def displayLogname(self):
		pass

	def updateLabelsThreaded(self):
		pass

	def onClose(self):
		self.data_manager.stopRead()

def main():
	# get arguments
	# start UI
	root = Tk()
	root.geometry("1100x600+100+100")
	data_manager = DataManager()
	data_manager.startRead()
	ui_manager = UIManager(root, data_manager)
	root.mainloop()

if __name__ == "__main__":
	main()


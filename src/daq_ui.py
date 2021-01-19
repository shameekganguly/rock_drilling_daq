# daq_ui.py

from tkinter import Tk, LEFT, RIGHT, TOP, BOTTOM, BOTH, RAISED, IntVar, font, messagebox
from tkinter.ttk import Frame, Label, Button, Style
import tkinter.font as tkFont
from redis import Redis
import time
from threading import Thread
import numpy as np
from playsound import playsound

NO_DATA_VALUE = -9999

class DataManager():
	def __init__(self, redis_ip_add="127.0.0.1", redis_port=6379, update_freq=10):
		self.reading = False
		# self.update_freq = update_freq
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
		self.screwjack_position_raw = IntVar(value=NO_DATA_VALUE)
		self.screwjack_position_comp = IntVar(value=NO_DATA_VALUE)
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
		self.linear_speed_unit = "cm/min"
		self.rotary_speed_unit = "RPM"
		self.temperature_unit = "deg C"
		self.position_unit = "cm"
		self.torque_unit = "Nm"
		self.force_unit = "kN"

		self.initDataDict()

		self.ui_alert_callback = None

	def startRead(self):
		# connect to redis
		self.connection = Redis(host=self.redis_ip_add, port=self.redis_port)
		self.reading = True

		# -- Not using threading --
		# set thread with readThreaded method
		# self.read_thread = Thread(target = self.readThreaded)
		# self.read_thread.start()

	def stopRead(self):
		self.reading = False

		# -- Not using threading --
		# stop read thread
		# self.read_thread.join()

		# disconnect from redis
		self.connection.close()

	def startLogging(self):
		#TODO: redis set start logging key
		pass

	def stopLogging(self):
		#TODO: redis set stop logging key
		pass

	def readThreaded(self):
		pass
		# -- Not using threading --
		# while self.reading:
		# 	time.sleep(1.0/self.update_freq)
		# 	self.readOnce()

	def readOnce(self):
		# pipeget from redis
		read_pipe = self.connection.pipeline()
		all_keys = list(self.dataDict.keys())
		for key in all_keys:
			read_pipe.get(key)
		output = read_pipe.execute()
		for ind in range(len(all_keys)):
			if output[ind] is None:
				self.dataDict[all_keys[ind]].set(NO_DATA_VALUE)
			else:
				try:
					self.dataDict[all_keys[ind]].set(int(output[ind]))
				except Exception:
					print("Warning: Redis read exception for key %s" %(all_keys[ind]))
		self.screwjack_position_comp.set(
			self.screwjack_position_raw.get() - self.screwjack_position_offset.get()
		)
		if self.ui_alert_callback:
			self.ui_alert_callback()

	def initDataDict(self):
		self.dataDict = {
			self.hpu_pressure_key: self.hpu_pressure,
			self.drill_pressure_key: self.drill_pressure,
			self.screwjack_pressure_key: self.screwjack_pressure,
			self.fluid_pressure_key: self.fluid_pressure,
			self.screwjack_speed_key: self.screwjack_speed,
			self.screwjack_position_key: self.screwjack_position_raw,
			self.screwjack_force_key: self.screwjack_force,
			self.drill_speed_key: self.drill_speed,
			self.drill_torque_key: self.drill_torque,
			self.front_bearing_temp_key: self.front_bearing_temp,
			self.rear_bearing_temp_key: self.rear_bearing_temp,
		}

class UIManager(Frame):
	def __init__(self, window, data_manager):
		super().__init__(window)
		self.data = data_manager
		self.max_temperature = 90 #deg C
		self.max_pressure = 105 #bar
		self.stall_speed_threshold = 5 # RPM or cm/min
		self.min_stall_pressure = 60 # bar
		self.max_screwjack_travel = 25 #cm

		self.is_logging = False
		self.did_show_alert = False

		self.initUI()
		self.data.ui_alert_callback = self.alertCallback

	def initUI(self):
		'''
		ui has 3 frames:
		- critical frame: which has critical sensor readings: speed, pressure
		- sensor frame: which has all other sensors
		- user frame: which has buttons for user inputs
		'''
		self.master.title("UTEC Experiments UI")

		self.initSensorFrame2()
		self.initSensorFrame1()
		self.initCriticalFrame()
		self.initUserFrame()

		# increase default font size
		default_font = tkFont.nametofont("TkDefaultFont")
		default_font.configure(size=18)

		self.pack(fill=BOTH, expand=True)

	def initCriticalFrame(self):
		self.critical_label_font = font.Font(size=48)
		self.critical_frame = Frame(self)

		top_frame = Frame(self.critical_frame)
		self.addCriticalReadout(top_frame, self.data.screwjack_speed_label, self.data.linear_speed_unit, self.data.screwjack_speed)
		self.addCriticalReadout(top_frame, self.data.drill_speed_label, self.data.rotary_speed_unit, self.data.drill_speed)
		top_frame.pack(side=TOP, fill=BOTH, expand=True)
		bottom_frame = Frame(self.critical_frame)
		self.addCriticalReadout(bottom_frame, self.data.hpu_pressure_label, self.data.pressure_unit, self.data.hpu_pressure)
		self.addCriticalReadout(bottom_frame, self.data.screwjack_position_label, self.data.position_unit, self.data.screwjack_position_comp)
		bottom_frame.pack(side=TOP, fill=BOTH, expand=True)

		self.critical_frame.pack(side=LEFT, fill=BOTH, expand=True)

	def addCriticalReadout(self, parent_frame, labelstr, unitstr, variable):
		sensor_frame = Frame(parent_frame)
		sensor_info_label = Label(
			sensor_frame,
			text='%s (%s)'% (labelstr, unitstr),
		)
		sensor_info_label.pack(side=TOP, pady=(10,0))
		sensor_data_label = Label(
			sensor_frame,
			textvariable=variable,
			font=self.critical_label_font
		)
		sensor_data_label.pack(side=TOP)
		sensor_frame.pack(side=LEFT, fill=BOTH, expand=True)

	def initSensorFrame1(self):
		self.sensor_frame1 = Frame(self)
		self.sensor_label_font = font.Font(size=24)

		self.addSensorReadout(self.sensor_frame1, self.data.drill_torque_label, self.data.torque_unit, self.data.drill_torque)
		self.addSensorReadout(self.sensor_frame1, self.data.screwjack_force_label, self.data.force_unit, self.data.screwjack_force)
		self.addSensorReadout(self.sensor_frame1, self.data.drill_pressure_label, self.data.pressure_unit, self.data.drill_pressure)
		self.addSensorReadout(self.sensor_frame1, self.data.screwjack_pressure_label, self.data.pressure_unit, self.data.screwjack_pressure)

		self.sensor_frame1.pack(side=BOTTOM, fill=BOTH, expand=True, padx = 50)

	def initSensorFrame2(self):
		self.sensor_frame2 = Frame(self)
		self.sensor_label_font = font.Font(size=24)

		# self.addSensorReadout(self.sensor_frame2, self.data.fluid_pressure_label, self.data.pressure_unit, self.data.fluid_pressure)
		self.addSensorReadout(self.sensor_frame2, self.data.front_bearing_temp_label, self.data.temperature_unit, self.data.front_bearing_temp)
		self.addSensorReadout(self.sensor_frame2, self.data.rear_bearing_temp_label, self.data.temperature_unit, self.data.rear_bearing_temp)

		self.sensor_frame2.pack(side=BOTTOM, fill=BOTH, expand=True, padx = 50)

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

	def initUserFrame(self):
		self.userFrame = Frame(self)
		self.loggingButton = Button(self.userFrame, text="Start logging", command=self.onLoggingButton)
		self.loggingButton.pack(side=TOP, pady = 30, ipadx=30, ipady=30)
		self.screwjackPositionButton = Button(self.userFrame, text="Reset ScrewJack position offset", command=self.zeroScrewjackPosition)
		self.screwjackPositionButton.pack(side=TOP, pady = 30, ipadx=30, ipady=30)
		self.userFrame.pack(side=RIGHT, fill=BOTH, expand=True)

	def alertCallback(self):
		temperature = max(
			self.data.front_bearing_temp.get(),
			self.data.rear_bearing_temp.get()
		)
		speed = min(
			self.data.drill_speed.get(),
			self.data.screwjack_speed.get()
		)
		if temperature > self.max_temperature:
			self.alertUser('TERMINATE: TEMPERATURE LIMIT REACHED!!')

		elif self.data.hpu_pressure.get() > self.max_pressure:
			self.alertUser('TERMINATE: PRESSURE LIMIT REACHED!!')

		elif self.data.hpu_pressure.get() > self.min_stall_pressure and speed > NO_DATA_VALUE and speed < self.stall_speed_threshold:
			self.alertUser('TERMINATE: DRILL OR SCREWJACK STALLED!!')

		elif self.data.screwjack_position_comp.get() > self.max_screwjack_travel:
			self.alertUser('TERMINATE: SCREWJACK TRAVEL LIMIT REACHED!!')
		else:
			self.did_show_alert = False

	def alertUser(self, message):
		if not self.did_show_alert:
			self.did_show_alert = True
			self.should_play_alert_sound = True
			#play alert sound
			sound_thread = Thread(target = self.playAlertSound)
			sound_thread.start()
			msg_thread = Thread(target = self.showAlertMessage, kwargs={"message":message})
			msg_thread.start()

	def showAlertMessage(self, message):
		messagebox.showerror(title="Critical failure", message=message)
		# once messagebox is closed, stop playing sound
		self.should_play_alert_sound = False

	def playAlertSound(self):
		while self.should_play_alert_sound:
			time.sleep(0.2)
			playsound('beep-02.mp3')

	def onLoggingButton(self):
		if self.is_logging:
			self.stopLogging()
			self.loggingButton.config(text="Start logging")
		else:
			self.startLogging()
			self.loggingButton.config(text="Stop logging")

	def startLogging(self):
		self.data.startLogging()
		self.is_logging = True

	def stopLogging(self):
		self.data.stopLogging()
		self.is_logging = False

	def zeroScrewjackPosition(self):
		if self.data.screwjack_position_raw.get() > NO_DATA_VALUE:
			self.data.screwjack_position_offset.set(self.data.screwjack_position_raw.get())

	def displayLogname(self):
		pass

	def onClose(self):
		# check if logging is on
		if self.is_logging:
			messagebox.showerror("Exit DAQ", "Logging is still on. Turn off logging before exiting.")
			return False
		self.data.stopRead()
		return True

def main():
	# TODO: get arguments
	# start UI
	root = Tk()
	root.geometry("1100x600+100+100")
	data_manager = DataManager()
	data_manager.startRead()
	ui_manager = UIManager(root, data_manager)
	def rootOnClose():
		if ui_manager.onClose():
			root.destroy()
	update_interval = int(1000/30) #ms
	def updateUI():
		data_manager.readOnce()
		root.after(update_interval, updateUI)

	root.protocol("WM_DELETE_WINDOW", rootOnClose)
	root.after(update_interval, updateUI)
	root.mainloop()

if __name__ == "__main__":
	main()


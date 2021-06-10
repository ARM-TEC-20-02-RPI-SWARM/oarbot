#!/usr/bin/env python
import rospy
from std_msgs.msg import String

import serial
#import time
#from termcolor import colored

## Just for Windows
#import os
#os.system('color')
try:

	ser = serial.Serial('/dev/ttyACM2', 115200, timeout =2, xonxoff=True)


	pub = rospy.Publisher('oarbot/uwb_serial_front', String, queue_size=10)
	rospy.init_node('uwb_serial_node', anonymous=True, disable_signals=True)



	# Two enter presses puts us into terminal mode
	ser.write('\r')
	ser.write('\r')
	

	# Wait until all the startup stuff is done
	for i in range(15):
		ser_bytes = ser.readline()
		print(ser_bytes)
		if "dwm> " in ser_bytes:
			break

	# Tell UWB tag to give us distance readings

	if not "DIST" in ser_bytes:
		ser.write("lec\r")
	ser_bytes = ser.readline() 
	print(ser_bytes)

	# Throw out first reading (has extra "dwm> "")
	ser_bytes = ser.readline() 
	print(ser_bytes)

	while True:
		ser_bytes = ser.readline()
		if(ser_bytes):
			rospy.loginfo(ser_bytes)
			pub.publish(ser_bytes)

except KeyboardInterrupt:
	print('Interrupt!')

	# Turn off lec
	ser.write('\r')
	# This turns the terminal mode off
	ser.write('quit\r')
	ser_bytes = ser.readline() 
	print(ser_bytes)
	ser_bytes = ser.readline() 
	print(ser_bytes)
	ser_bytes = ser.readline() 
	print(ser_bytes)
	ser_bytes = ser.readline() 
	print(ser_bytes)

	ser.close()
"""
This example demonstrates how to send simple messages to the Pupil Remote plugin
	'R' start recording with auto generated session name
	'R rec_name' start recording and name new session name: rec_name
	'r' stop recording
	'C' start currently selected calibration
	'c' stop currently selected calibration
	'T 1234.56' Timesync: make timestamps count form 1234.56 from now on.
	't' get pupil timestamp
"""
import zmq
from time import sleep, time

context =  zmq.Context()
socket = context.socket(zmq.REQ)

# set your IP here
socket.connect('tcp://127.0.0.1:50020')
t = time()
socket.send('T 0.0') #set timebase to 0.0

print socket.recv()
print 'Round trip command delay:', time()-t

sleep(1)
socket.send('R')
print socket.recv()

sleep(5)
socket.send('r')

print socket.recv()

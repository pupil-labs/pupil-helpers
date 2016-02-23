'''
a script that will replay pupil server messages to serial.

as implemented here only the pupil_norm_pos is relayed.
implementing other messages to be send as well is a matter of renaming the vaiables.


'''

#zmq setup
import zmq
import json
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://127.0.0.1:5000")
#filter by messages by stating string 'STRING'. '' receives all messages
socket.setsockopt(zmq.SUBSCRIBE, 'pupil_positions')

#serial setup
import serial # if you have not already done so
ser = serial.Serial('/dev/tty.usbserial', 9600) #point to arduino

while True:
    topic,msg =  socket.recv_multipart()
    pupil_positions = json.loads(msg)

    for pupil_position in pupil_positions:
        x,y = pupil_position['norm_pos']
        print x,y
        ser.write(x)
        ser.write(y)

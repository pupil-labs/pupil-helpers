'''
a script that will replay pupil server messages to serial.

as implemented here only the pupil_norm_pos is relayed.
implementeing other messages to be send as well is a matter of renaming the vaiables.


'''

#zmq setup
import zmq
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://127.0.0.1:5000")
#filter by messages by stating string 'STRING'. '' receives all messages
socket.setsockopt(zmq.SUBSCRIBE, '')

#serial setup
import serial # if you have not already done so
ser = serial.Serial('/dev/tty.usbserial', 9600) #point to arduino

while True:
    msg = socket.recv()
    print "raw msg:\n", msg

    items = msg.split("\n")
    msg_type = items.pop(0)
    items = dict([i.split(':') for i in items[:-1] ])

    if msg_type == 'Pupil':
        if items.get('norm_pupil', 'None') != "None":
            print 'sending: ',items['norm_pupil']
            norm_pupil = items['norm_pupil'].replace("(",'').replace(")",'')
            x,y = norm_pupil.split(',')
            ser.write(x)
            ser.write(y)
    else:
        # process event msgs from plugins here
        pass
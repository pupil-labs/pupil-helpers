'''
A script that will relay pupil data to serial.

As implemented here only the norm_pos is relayed.
Implementing other messages to be send as well is a matter of renaming the variables.


'''
import zmq
from msgpack import loads
from pupil_remote_control import Requester

context = zmq.Context()
addr = '127.0.0.1' # remote ip or localhost
req_port = 50020   # same as in the pupil remote gui
url = "tcp://%s:%s"%(addr,req_port)

# initialize Pupil Remote utility
req = Requester(context,url)

# ask for the sub port
sub_port = req.send_cmd('SUB_PORT')

# open a sub port to listen to pupil
sub = context.socket(zmq.SUB)
sub.connect("tcp://%s:%s" %(addr,sub_port))
sub.setsockopt(zmq.SUBSCRIBE, 'pupil.')

#serial setup
import serial # if you have not already done so
ser = serial.Serial('/dev/tty.usbserial', 9600) #point to arduino

while True:
    topic,msg =  sub.recv_multipart()
    pupil_position = loads(msg)
    x,y = pupil_position['norm_pos']
    print x,y
    ser.write(x)
    ser.write(y)

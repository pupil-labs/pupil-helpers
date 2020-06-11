'''
A script that will relay pupil data to serial.

As implemented here only the norm_pos is relayed.
Implementing other messages to be send as well is a matter of renaming the variables.


'''
import zmq
import serial
from msgpack import loads

context = zmq.Context()
addr = '127.0.0.1'  # remote ip or localhost
req_port = 50020  # same as in the pupil remote gui
req = context.socket(zmq.REQ)
req.connect("tcp://{}:{}".format(addr, req_port))

# ask for the sub port
req.send_string('SUB_PORT')
sub_port = req.recv_string()

# open a sub port to listen to pupil
sub = context.socket(zmq.SUB)
sub.connect("tcp://{}:{}".format(addr, sub_port))
sub.setsockopt_string(zmq.SUBSCRIBE, 'pupil.')

# serial setup
ser = serial.Serial('/dev/tty.usbserial', 9600)  # point to arduino

while True:
    topic = sub.recv_string()
    msg = sub.recv()  # bytes
    pupil_position = loads(msg, encoding='utf-8')
    x, y = pupil_position['norm_pos']
    print(x, y)
    ser.write(x)
    ser.write(y)

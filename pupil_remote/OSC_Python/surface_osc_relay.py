'''
Small script that redirects basic surface data via udp using the OSC protocol

Requires https://github.com/attwad/python-osc
'''

import zmq
from msgpack import loads

# OSC stuff
from pythonosc.udp_client import SimpleUDPClient
target_addr = 'localhost'
target_port = 47763

context = zmq.Context()
# open a req port to talk to pupil
addr = '127.0.0.1'  # remote ip or localhost
req_port = "50020"  # same as in the pupil remote gui
req = context.socket(zmq.REQ)
req.connect("tcp://{}:{}".format(addr, req_port))
# ask for the sub port
req.send_string('SUB_PORT')
sub_port = req.recv_string()

# open a sub port to listen to pupil
sub = context.socket(zmq.SUB)
sub.connect("tcp://{}:{}".format(addr, sub_port))
sub.setsockopt_string(zmq.SUBSCRIBE, 'surface')

udp_client = SimpleUDPClient(target_addr, target_port)

while True:
    try:
        topic = sub.recv_string()
        msg = sub.recv()  # bytes
        surface = loads(msg, encoding='utf-8')
        try:
            gaze_positions = surface['gaze_on_srf']
            for gaze_pos in gaze_positions:
                data = gaze_pos['norm_pos']
                data.append(gaze_pos['timestamp'])
                data.append(gaze_pos['confidence'])
                udp_client.send_message(surface['name'], data)
        except:
            pass
    except KeyboardInterrupt:
        break

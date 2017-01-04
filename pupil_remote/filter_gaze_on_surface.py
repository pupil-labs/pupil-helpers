"""
Receive data from Pupil server broadcast over TCP
test script to see what the stream looks like
and for debugging
"""
import zmq
from msgpack import loads

context = zmq.Context()
# open a req port to talk to pupil
addr = '127.0.0.1'  # remote ip or localhost
req_port = "65033"  # same as in the pupil remote gui
req = context.socket(zmq.REQ)
req.connect("tcp://{}:{}".format(addr, req_port))
# ask for the sub port
req.send('SUB_PORT')
sub_port = req.recv()

# open a sub port to listen to pupil
sub = context.socket(zmq.SUB)
sub.connect("tcp://{}:{}".format(addr, sub_port))
sub.setsockopt(zmq.SUBSCRIBE, 'surface')

# specify the name of the surface you want to use
surface_name = 'unnamed'

while True:
    topic, msg = sub.recv_multipart()
    surfaces = loads(msg)
    filtered_surface = {k: v for k, v in surfaces.iteritems() if surfaces['name'] == surface_name}
    try:
        # note that we may have more than one gaze position data point (this is expected behavior)
        gaze_positions = filtered_surface['gaze_on_srf']
        for gaze_pos in gaze_positions:
            norm_gp_x, norm_gp_y = gaze_pos['norm_pos']

            # only print normalized gaze positions within the surface bounds
            if (0 <= norm_gp_x <= 1 and 0 <= norm_gp_y <= 1):
                print "gaze on surface: {}\t, normalized coordinates: {},{}".format(surface_name, norm_gp_x, norm_gp_y)
    except:
        pass

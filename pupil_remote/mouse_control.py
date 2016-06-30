"""
Stream Pupil gaze coordinate data using zmq to control a mouse with your eye.
Please note that marker tracking must be enabled, and in this example we have named the surface "screen."
You can name the surface what you like in Pupil capture and then write the name of the surface you'd like to use on line 17.
"""
import zmq
from msgpack import loads
import subprocess as sp
import sys
from platform import system
from pupil_remote_control import Requester

try:
    #not working on MacOS
    from pymouse import PyMouse
    m = PyMouse()
    m.move(0,0) # hack to init PyMouse -- still needed
except ImportError:
    pass

def set_mouse(x=0,y=0,click=0):
    if system() == "Darwin":
        sp.Popen(["./mac_os_helpers/mouse", "-x", "%s" %x, "-y", "%s" %y, "-click", "%s" %click])
    else:
        if click:
            m.click(x,y)
        else:
            m.move(x,y)

def get_screen_size():
    screen_size = None
    if system() == "Darwin":
        screen_size = sp.check_output(["./mac_os_helpers/get_screen_size"]).split(",")
        screen_size = float(screen_size[0]),float(screen_size[1])
    else:
        screen_size = m.screen_size()
    return screen_size

context = zmq.Context()
#open a req port to talk to pupil
addr = '127.0.0.1'                  # remote ip or localhost
req_port = 50020                    # same as in the pupil remote gui
url = "tcp://%s:%s"%(addr,req_port)
req = Requester(context,url)        # initialize Pupil Remote utility
sub_port = req.send_cmd('SUB_PORT') # ask for the sub port

# open a sub port to listen to pupil
sub = context.socket(zmq.SUB)
sub.connect("tcp://%s:%s" %(addr,sub_port))
sub.setsockopt(zmq.SUBSCRIBE, 'gaze')

smooth_x, smooth_y = 0.5, 0.5

# screen size
x_dim, y_dim = get_screen_size()
print "x_dim: %s, y_dim: %s" %(x_dim,y_dim)

# specify the name of the surface you want to use
surface_name = "screen"
while True:
    topic,msg =  sub.recv_multipart()
    gaze_position = loads(msg)
    try:
        gaze_on_screen = gaze_position["realtime gaze on "+surface_name]
        raw_x,raw_y = gaze_on_screen
        # smoothing out the gaze so the mouse has smoother movement
        smooth_x += 0.5 * (raw_x-smooth_x)
        smooth_y += 0.5 * (raw_y-smooth_y)
        x = smooth_x
        y = smooth_y

        y = 1-y # inverting y so it shows up correctly on screen
        x *= int(x_dim)
        y *= int(y_dim)
        # PyMouse or MacOS bugfix - can not go to extreme corners because of hot corners?
        x = min(x_dim-10, max(10,x))
        y = min(y_dim-10, max(10,y))

        print "%s,%s" %(x,y)
        set_mouse(x,y)
    except KeyError:
        pass
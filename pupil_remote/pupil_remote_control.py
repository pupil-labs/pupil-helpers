'''
(*)~----------------------------------------------------------------------------------
 Pupil Helpers
 Copyright (C) 2012-2016  Pupil Labs

 Distributed under the terms of the GNU Lesser General Public License (LGPL v3.0).
 License details are in the file license.txt, distributed as part of this software.
----------------------------------------------------------------------------------~(*)
'''

import zmq
from zmq.utils.monitor import recv_monitor_message
import msgpack as serializer

class Requester(object):
    """Send commands or notifications to Pupil Remote"""
    def __init__(self, ctx, url, block_unitl_connected=True):
        self.socket = zmq.Socket(ctx,zmq.REQ)
        if block_unitl_connected:
            #connect node and block until a connecetion has been made
            monitor = self.socket.get_monitor_socket()
            self.socket.connect(url)
            while True:
                status =  recv_monitor_message(monitor)
                if status['event'] == zmq.EVENT_CONNECTED:
                    break
                elif status['event'] == zmq.EVENT_CONNECT_DELAYED:
                    pass
                else:
                    raise Exception("ZMQ connection failed")
            self.socket.disable_monitor()
        else:
            self.socket.connect(url)

    def send_cmd(self,cmd):
        """Sends simple messages to the Pupil Remote plugin
            'R' start recording with auto generated session name
            'R rec_name' start recording and name new session name: rec_name
            'r' stop recording
            'C' start currently selected calibration
            'c' stop currently selected calibration
            'T 1234.56' Timesync: make timestamps count form 1234.56 from now on.
            't' get pupil timestamp
        """
        self.socket.send(cmd)
        return self.socket.recv()

    def notify(self,notification):
        """Sends ``notification`` to Pupil Remote"""
        topic = 'notify.' + notification['subject']
        payload = serializer.dumps(notification)
        self.socket.send_multipart((topic,payload))
        return self.socket.recv()

    def __del__(self):
        self.socket.close()

if __name__ == '__main__':
    from time import sleep, time

    # Setup zmq context and remote helper
    context =  zmq.Context()
    url = 'tcp://127.0.0.1:50020'
    remote = Requester(context,url)

    # Measure round trip delay
    t = time()
    print remote.send_cmd('T 0.0') #set timebase to 0.0
    print 'Round trip command delay:', time()-t

    # Test recording
    sleep(1)
    print remote.send_cmd('R')

    sleep(5)
    print remote.send_cmd('r')
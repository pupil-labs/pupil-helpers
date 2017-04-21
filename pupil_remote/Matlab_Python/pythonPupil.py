"""
Receive data from Pupil using ZMQ. This script will connect to PupilRemote and start streaming incoming data to Matlab
via UDP
"""
import socket
import timeit

# install via pip or lookup how to install
import numpy as np
import zmq
from msgpack import loads

# this package needs to be installed can be found at (https://pypi.python.org/pypi/numpy_ringbuffer/0.2.0)
from numpy_ringbuffer import RingBuffer

# change this value to the period of UDP Send normally 0.02 = 20 ms
downSampleRate = 0

# Matlab Address for relaying info
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.connect(('127.0.0.1', 8821)) # IP TO MATLAB


# setup ZMQ Context
context = zmq.Context()

# open a req port to talk to pupil
addr = '131.215.27.51'  # IP to machine running pupil software
# addr = '192.168.1.25'
req_port = "50020"  # same as in the pupil remote gui
req = context.socket(zmq.REQ)
req.connect("tcp://{}:{}".format(addr, req_port))
# ask for the sub port
req.send_string('SUB_PORT')
sub_port = req.recv_string()
# open a sub port to listen to pupil
sub = context.socket(zmq.SUB)
sub.connect("tcp://{}:{}".format(addr, sub_port))

# set subscriptions to topics
# recv just pupil/gaze/notifications
# sub.setsockopt_string(zmq.SUBSCRIBE, 'pupil.')
sub.setsockopt_string(zmq.SUBSCRIBE, 'gaze')
# packID tells matlab how to handle the data 0 is for gaze 1 is for surface
packID = np.array([0])
# sub.setsockopt_string(zmq.SUBSCRIBE, 'notify.')
# sub.setsockopt_string(zmq.SUBSCRIBE, 'logging.')
# sub.setsockopt_string(zmq.SUBSCRIBE, 'surface')
# packID = np.array([1])
# or everything:
# sub.setsockopt_string(zmq.SUBSCRIBE, '')


req.send_string('T 0')
# print
print(req.recv_string())

# initialize Timer
start_time = timeit.default_timer()

# intialize timeout counter
TOcounter = 0

# Setup ring buffers
norm_x_RB = RingBuffer(capacity=5, dtype='float32')
norm_y_RB = RingBuffer(capacity=5, dtype='float32')
confRB = RingBuffer(capacity=5, dtype='float32')



while True:

    # timeout will be 0 if nothing was received in the time allotted time is in ms
    timeout = sub.poll(8)

    if not timeout:

        TOsetter = True

        if (TOsetter == True
            and TOcounter < 1):

            TOcounter = 1
            print("timeout...", TOcounter)

        # TOcounter will determine how many ms before it sends the framework an empty message
        # (note: NaNs are made in Framework.EyeTracker.PupilNetwork.m)
        # if sub.poll(8) and TOcounter set to 2 then 16 ms before sending NaNs
        elif TOcounter == 2:

            # payload
            payload = np.zeros(28, dtype='uint8')

            #bytelen 3 includes packID bytelen and checksum
            bytelen = np.array([len(payload) + 3])
            bytelen = bytelen.astype('uint8')

            # checksum
            checksum = np.sum(np.hstack((payload))) % 256
            checksum = checksum.astype('uint8')

            # packID 3 for timeout matlab framework should hard code NaNs w/ this ID
            packID = np.array([3])
            packID = packID.astype('uint8')

            uMsg = np.hstack((bytelen, packID, payload, checksum))
            my_socket.send(uMsg)

            print('.........................................HARD TIMEOUT.........................................')

            # reset TOcounter
            TOcounter = 0

        elif (TOsetter == True and
            TOcounter >= 1):

            TOcounter = TOcounter + 1
            print("timeout...", TOcounter)

    else:
        # Receive ZMQ message
        topic = sub.recv_string()
        msg = sub.recv()
        msg = loads(msg, encoding='utf-8')
        # print("\n{}: {}".format(topic, msg))

        # reset timeout counter
        TOsetter = False
        TOcounter = 0

        # this will pull time from original message
        timestamp = msg["timestamp"]
        # print timestamp
        length = len(msg)

        # pull data: norm_pos, conf, timestamp
        norm_pos = msg["norm_pos"]
        confidence = msg["confidence"]
        timestamp = msg["timestamp"]

        # convert dict values to np.array will be float64
        norm_pos = np.array(norm_pos)
        conf = np.array([confidence])
        timestamp = np.array([timestamp])

        # cast values to float or single
        norm_pos1 = norm_pos.astype('float32')
        conf1 = conf.astype('float32')
        timestamp1 = timestamp.astype('float32')

        # Circular buffer (recent values on the right...old dropped from left) this is left here when dealing with surfaces will update this later
        # my current version that I use in lab uses this
        norm_x_RB.append(norm_pos1[0])
        norm_y_RB.append(norm_pos1[1])
        confRB.append(conf1)

        recent_time = timeit.default_timer()
        if recent_time - start_time >= downSampleRate:
            if len(norm_x_RB) > 1:
                # average the values
                norm_x_avg = np.mean(norm_x_RB, keepdims=1)
                norm_y_avg = np.mean(norm_y_RB, keepdims=1)
                conf_avg = np.mean(confRB, keepdims=1)

                # typecast these values
                norm_x_avg.dtype = 'uint8'
                norm_y_avg.dtype = 'uint8'
                conf_avg.dtype = 'uint8'

                # issue arose where if you pulled timestamp again it would change the shape of timestamp1
                # on the following iteration this avoids the shape change
                # if x == 0:
                timestamp = np.array([timestamp])
                timestamp1 = timestamp.astype('float32')
                timestamp1.dtype = 'uint8'
                timestamp2 = np.squeeze(timestamp1)

                # payload
                payload = np.hstack((norm_x_avg, norm_y_avg, conf_avg, timestamp2))
                # print len(payload)

                # payload length cast and typecasting
                bytelen = np.array([len(payload) + 3])
                bytelen = bytelen.astype('uint8')

                # calculate the checksum ONLY off payload
                checksum = np.sum(np.hstack((payload))) % 256
                checksum = checksum.astype('uint8')

                # packet ID (tells matlab if this is a surface or not) 1 is Surface 0 is gaze
                packID = np.array([0])
                packID = packID.astype('uint8')

                # create final udp msg bytestream and send to MATLAB
                uMsg = np.hstack((bytelen, packID, payload, checksum))
                my_socket.send(uMsg)
                print('Average sent....')

                norm_x_RB = RingBuffer(capacity=5, dtype='float32')
                norm_y_RB = RingBuffer(capacity=5, dtype='float32')
                confRB = RingBuffer(capacity=5, dtype='float32')


            else:
                # typecast all values
                norm_pos1.dtype = 'uint8'
                conf1.dtype = 'uint8'

                # issue arose where if you pulled timestamp again it would change the shape of timestamp1
                # on the following iteration this avoids the shape change
                # if x == 0:
                timestamp = np.array([timestamp])
                timestamp1 = timestamp.astype('float32')
                timestamp1.dtype = 'uint8'
                timestamp2 = np.squeeze(timestamp1)

                # payload
                payload = np.hstack((norm_pos1, conf1, timestamp2))
                # print len(payload)

                # payload length cast and typecasting
                bytelen = np.array([len(payload) + 3])
                bytelen = bytelen.astype('uint8')

                # calculate the checksum ONLY off payload
                checksum = np.sum(np.hstack((payload))) % 256
                checksum = checksum.astype('uint8')

                # packet ID (tells matlab if this is a surface or not) 1 is Surface 0 is gaze
                packID = np.array([0])
                packID = packID.astype('uint8')

                # create final udp msg bytestream and send to MATLAB
                uMsg = np.hstack((bytelen, packID, payload, checksum))
                print(uMsg[1])
                # print len(uMsg)
                # print "great successsss"
                my_socket.send(uMsg)
                start_time = recent_time
                # print str(downSampleRate) + " elapsed...Message Sent"

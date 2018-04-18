# Pupil Matlab Helpers

The scripts were tested on MATLAB 2017a

## Requirements

The provided scripts require the following packages to be installed:
- https://github.com/fagg/matlab-zmq
- https://github.com/bastibe/matlab-msgpack

Make sure that the above packages are included in your Matlab path, as well
as `recv_message.m` and `send_notification.m`.

## How to use

1. Clone/copy the matlab folder to your computer
2. Change the Matlab path to your local copy
3. Start Pupil Capture
4. Run one of the example scripts
    - `pupil_remote_control.m`: Example on how to interact with Pupil Remote
    - `filter_messages.m`: Example on how to subscribe to and receive messages
        of a specific topic

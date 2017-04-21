I currently use 
Python 3.5.2
Matlab 2016b

Necessary packages needed to run python script

run cmd with admin priv

python -m pip install numpy
python -m pip install pyzmq
python -m pip install msgpack-python
python -m pip install numpy_ringbuffer


Instructions:

1. Ensure that pythonPupil.py is pointed to the correct pupil remote location ip and port
2. Note IP and Port for UDP make sure it matches in your PupilNetwork2.m file
3. add pupilRead to your path or change your folder in matlab to this folder
4. start pythonPupil.py and immediately start PupilNetwork2.m
5. matlab is now receiving pupil remote info via udp from pythonPupil.py

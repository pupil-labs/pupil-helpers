function [ ] = send_annotation( socket, annotation )
%NOTIFY Use socket to send annotation
%   Annotations are container.Map objects that contain
%   at least the following keys
%   'topic': String starting with "annotation.", followed by arbitrary string
%   'label': Arbitrary string
%   'timestamp': Pupil time as floating point value
%   'duration': Duration of annoation as floating point value, can be 0.0
payload = dumpmsgpack(annotation);
zmq.core.send(socket, uint8(annotation('topic')), 'ZMQ_SNDMORE');
zmq.core.send(socket, payload);
end
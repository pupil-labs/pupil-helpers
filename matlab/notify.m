function [ ] = notify( socket, notification )
%NOTIFY Use socket to send notification
%   Detailed explanation goes here
topic = strcat('notify.', notification('subject'));
payload = dumpmsgpack(notification);
zmq.core.send(socket, uint8(topic), 'ZMQ_SNDMORE');
zmq.core.send(socket, payload);
end
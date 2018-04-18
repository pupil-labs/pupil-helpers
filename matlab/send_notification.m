function [ ] = send_notification( socket, notification )
%NOTIFY Use socket to send notification
%   Notifications are container.Map objects that contain
%   at least the key 'subject'.
topic = strcat('notify.', notification('subject'));
payload = dumpmsgpack(notification);
zmq.core.send(socket, uint8(topic), 'ZMQ_SNDMORE');
zmq.core.send(socket, payload);
end
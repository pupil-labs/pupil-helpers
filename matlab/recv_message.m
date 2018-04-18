function [ topic, payload ] = recv_message( socket, bufferLength )
%recv_message Use socket to receive topics and their messages
%   Messages are 2-frame zmq messages that include the topic
%   and the message payload as a msgpack encoded string.

% receive the topic
topic = char(zmq.core.recv(socket));

lastwarn('');  % reset last warning
payload = zmq.core.recv(socket, bufferLength);  % receive payload
[~, warnId] = lastwarn;  % fetch possible buffer length warning
if isequal(warnId, 'zmq:core:recv:bufferTooSmall')
    payload = false;  % set payload to false since it is incomplete
else
    payload = parsemsgpack(payload);  % parse payload
end
end

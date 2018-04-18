% pupil_remote_control.m

% (*)~----------------------------------------------------------------------------------
%  Pupil Helpers
%  Copyright (C) 2012-2016  Pupil Labs
% 
%  Distributed under the terms of the GNU Lesser General Public License (LGPL v3.0).
%  License details are in the file license.txt, distributed as part of this software.
% ----------------------------------------------------------------------------------~(*)


% Setup zmq context and remote helper
ctx = zmq.core.ctx_new();
req_socket = zmq.core.socket(ctx, 'ZMQ_REQ');

ip_address = '127.0.0.1';
req_port = '50020';
req_endpoint =  sprintf('tcp://%s:%s', ip_address, req_port);

fprintf('Connecting to REQ: %s\n', req_endpoint);
zmq.core.connect(req_socket, req_endpoint);

% Request sub port
zmq.core.send(req_socket, uint8('SUB_PORT'));
sub_port = char(zmq.core.recv(req_socket));
fprintf('Received sub port: %s\n', sub_port);

% Disconnect req socket
zmq.core.disconnect(req_socket, req_endpoint);
zmq.core.close(req_socket);
fprintf('Disconnected from REQ: %s\n', req_endpoint);

% Create and connect sub socket
sub_endpoint =  sprintf('tcp://%s:%s', ip_address, sub_port);
sub_socket = zmq.core.socket(ctx, 'ZMQ_SUB');

fprintf('Connecting to SUB: %s\n', sub_endpoint);
zmq.core.connect(sub_socket, sub_endpoint);

% set subscriptions to topics
% recv just pupil/gaze/notifications
zmq.core.setsockopt(sub_socket, 'ZMQ_SUBSCRIBE', 'pupil.');
% zmq.core.setsockopt(socket, 'ZMQ_SUBSCRIBE', 'gaze.');
% zmq.core.setsockopt(socket, 'ZMQ_SUBSCRIBE', 'notify.');
% zmq.core.setsockopt(socket, 'ZMQ_SUBSCRIBE', 'logging.');
% or everything else
% zmq.core.setsockopt(socket, 'ZMQ_SUBSCRIBE', '');

for iter = 1:5  % receive the first 5 messages
    % messages that are longer than 1024 bytes will be tuncated
    % and ignored. In this case note is set to false. Increase
    % the buffer size if you experience this issue.
    [topic, note] = recv_message(sub_socket, 1024);
    if ~isequal(note, false)  % test for valid message
        [topic, note('norm_pos')]  % print pupil norm_pos
    end
end

% disconnect sub socket
zmq.core.disconnect(sub_socket, sub_endpoint);
zmq.core.close(sub_socket);
fprintf('Disconnected from SUB: %s\n', sub_endpoint);

zmq.core.ctx_shutdown(ctx);
zmq.core.ctx_term(ctx);

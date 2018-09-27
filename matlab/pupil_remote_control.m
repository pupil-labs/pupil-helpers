% pupil_remote_control.m

% (*)~----------------------------------------------------------------------------------
%  Pupil Helpers
%  Copyright (C) 2012-2016  Pupil Labs
% 
%  Distributed under the terms of the GNU Lesser General Public License (LGPL v3.0).
%  License details are in the file license.txt, distributed as part of this software.
% ----------------------------------------------------------------------------------~(*)

% Pupil Remote address
endpoint =  'tcp://127.0.0.1:50020';

% Setup zmq context and remote helper
ctx = zmq.core.ctx_new();
socket = zmq.core.socket(ctx, 'ZMQ_REQ');

% set timeout to 1000ms in order to not get stuck in a blocking
% mex-call if server is not reachable, see
% http://api.zeromq.org/4-0:zmq-setsockopt#toc19
zmq.core.setsockopt(socket, 'ZMQ_RCVTIMEO', 1000);

fprintf('Connecting to %s\n', endpoint);
zmq.core.connect(socket, endpoint);

tic; % Measure round trip delay
zmq.core.send(socket, uint8('t'));
result = zmq.core.recv(socket);
fprintf('%s\n', char(result));
fprintf('Round trip command delay: %s\n', toc);

% set current Pupil time to 0.0
zmq.core.send(socket, uint8('T 0.0'));
result = zmq.core.recv(socket);
fprintf('%s\n', char(result));

% start recording
pause(1.0);
zmq.core.send(socket, uint8('R'));
result = zmq.core.recv(socket);
fprintf('Recording should start: %s\n', char(result));

pause(5.0);
zmq.core.send(socket, uint8('r'));
result = zmq.core.recv(socket);
fprintf('Recording stopped: %s\n', char(result));

% test notification, note that you need to listen on the IPC to receive notifications!
send_notification(socket, containers.Map({'subject'}, {'calibration.should_start'}))
result = zmq.core.recv(socket);
fprintf('Notification received: %s\n', char(result));

send_notification(socket, containers.Map({'subject'}, {'calibration.should_stop'}))
result = zmq.core.recv(socket);
fprintf('Notification received: %s\n', char(result));

zmq.core.disconnect(socket, endpoint);
zmq.core.close(socket);

zmq.core.ctx_shutdown(ctx);
zmq.core.ctx_term(ctx);

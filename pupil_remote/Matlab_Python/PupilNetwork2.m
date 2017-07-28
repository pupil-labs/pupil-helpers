% construct the pupil UDP
hUDP = udp('127.0.0.1','LocalPort',8821,'Timeout',0.5);
eyeProperties.timerPeriod = 0.05; % in seconds 0.05 = 50 ms

fopen(hUDP);
eyeProperties.isOpen = true;

tic; fread(hUDP); elapsed=toc;
if elapsed>=eyeProperties.timerPeriod
    sprintf('Timeout for PupilNetwork UDP (%.2f sec): Check UDP connection ',elapsed);
    fclose(hUDP);
    eyeProperties.isOpen = false;
else
    eyeProperties.isConnected = true;
end


for i = 1:1000
[pupil_vals] = pupilRead(hUDP, eyeProperties);
end

%%
% if you get errors about the address being open run these two lines
fclose(hUDP);
delete(instrfindall)
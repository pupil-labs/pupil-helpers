#UDP socket setup
import select, socket
import platform

port = 50005  # where do you expect to get a msg?
bufferSize = 1024 # whatever you need

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
if platform.system() == 'Darwin':
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
else:
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind(('', port))
s.setblocking(0)



#zmq setup
import zmq
context = zmq.Context()
z = context.socket(zmq.REQ)
z.connect("tcp://localhost:50020") #configure for localhost on port 50020



while True:
  
  result = select.select([s],[],[])
  #get udp message string
  msg = result[0][0].recv(bufferSize)
  print msg
  #relay to pupil remote.
  z.send(msg)
  #await confirmation
  print z.recv()




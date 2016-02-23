from pyre import Pyre
from pyre import zhelper
import zmq
import logging
import sys
from uuid import UUID

'''
threaded pupil sync script:
Similar to the simple script:
Group is set to 'default group'
Name is set to 'Script'

Catches keyboard input and sends it to all Pupils in the same group.

ctrl+c for exit
'''

SYNC_TIME_MASTER_ANNOUNCE = "SYNC_TIME_MASTER:"
NOTIFICATION = "REMOTE_NOTIFICATION:"
TIMESTAMP_REQ = "TIMESTAMP_REQ"
TIMESTAMP = "TIMESTAMP:"
msg_delimeter  = '::'

def handle_msg(uuid,name,msg,node):
    print UUID(bytes=uuid),name,msg


def thread_loop(context,pipe):
    n = Pyre("Script")
    n.join('default group')
    n.start()

    poller = zmq.Poller()
    poller.register(pipe, zmq.POLLIN)
    logger.debug(n.socket())
    poller.register(n.socket(), zmq.POLLIN)
    while(True):
        try:
            items = dict(poller.poll())
        except zmq.ZMQError:
            logger.warning('Socket fail.')

        if pipe in items and items[pipe] == zmq.POLLIN:
            message = pipe.recv()
            # message to quit
            if message.decode('utf-8') == "EXIT_THREAD":
                break
            else:
                logger.debug("Emitting to '%s'" %message)
                n.shouts('default group', message)

        if n.socket() in items and items[n.socket()] == zmq.POLLIN:
            cmds = n.recv()
            msg_type = cmds.pop(0)
            msg_type = msg_type.decode('utf-8')

            if msg_type == "SHOUT":
                uuid,name,group,msg = cmds
                handle_msg(uuid,name,msg,n)
            elif msg_type == "WHISPER":
                uuid,name,msg = cmds
                handle_msg(uuid,name,msg,n)
            elif msg_type == "JOIN":
                uuid,name,group = cmds
                logger.debug("'%s' joined with uid: %s"%(name,UUID(bytes=uuid)))
            elif msg_type == "EXIT":
                uuid,name = cmds
                logger.debug("'%s' left with uid: %s"%(name,UUID(bytes=uuid)))
            # elif msg_type == "LEAVE":
            #     uid,name,group = cmds
            # elif msg_type == "ENTER":
            #     uid,name,headers,ip = cmds

    logger.debug('thread_loop closing.')
    chat_pipe = None
    n.stop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("pyre")
    logger.setLevel(logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    ctx = zmq.Context()
    chat_pipe = zhelper.zthread_fork(ctx, thread_loop)
    # input in python 2 is different
    if sys.version_info.major < 3:
        input = raw_input

    while True:
        try:
            msg = input()
            chat_pipe.send(msg.encode('utf_8'))
        except (KeyboardInterrupt, SystemExit):
            break
    chat_pipe.send("EXIT_THREAD".encode('utf_8'))
    logger.debug("Done")
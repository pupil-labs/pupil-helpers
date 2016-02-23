from pyre import Pyre
from pyre import zhelper
import zmq
import logging
import sys
from uuid import UUID

'''
simple pupil sync script:
Its a bit stupid but it shows how to control other pupil capture sessions
Group is set to 'default group'
Name is set to 'Script'

All this does is join the group listen to messages and emmit a time sync command every second.
The sync command is a bit useless but it will show up on all pupils in the same group.

ctrl+c for exit

Have a look at the threaded example if you want to build something with this.
'''

SYNC_TIME_MASTER_ANNOUNCE = "SYNC_TIME_MASTER:"
NOTIFICATION = "REMOTE_NOTIFICATION:"
TIMESTAMP_REQ = "TIMESTAMP_REQ"
TIMESTAMP = "TIMESTAMP:"
msg_delimeter  = '::'


def handle_msg(uuid,name,msg,node):
    print UUID(bytes=uuid),name,msg

if __name__ == '__main__':


    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("pyre")
    logger.setLevel(logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    ctx = zmq.Context()
    n = Pyre("Script")
    n.join('default group')
    n.start()

    poller = zmq.Poller()
    poller.register(n.socket(), zmq.POLLIN)
    try:
        while(True):
            items = dict(poller.poll(timeout=1000))
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
                    uid,name,group = cmds
                    logger.debug("'%s' joined with uid: %s"%(name,uid))
                elif msg_type == "EXIT":
                    uid,name = cmds
                    logger.debug("'%s' left with uid: %s"%(name,uid))

    except (KeyboardInterrupt, SystemExit):
        print 'User exit'
    n.stop()
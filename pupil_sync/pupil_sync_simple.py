from pyre import Pyre
from pyre import zhelper
import zmq
import logging
import sys


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

start_rec = "START_REC:"
stop_rec = "STOP_REC:"
start_cal = "START_CAL"
stop_cal = "STOP_CAL"
sync_time = "SYNC:"

def handle_msg(name,msg):
    if start_rec in msg :
        session_name = msg.replace(start_rec,'')
        logger.info('recording start msg received')
    elif stop_rec in msg:
        logger.info('recording stop msg received')
    elif start_cal in msg:
        logger.info('calibration start msg received')
    elif stop_cal in msg:
        logger.info('calibration stop msg received')
    elif sync_time in msg:
        offset = float(msg.replace(sync_time,''))
        logger.info('time sync msg received')


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
                    uid,name,group,msg = cmds
                    logger.debug("'%s' shouts '%s'."%(name,msg))
                    handle_msg(name,msg)
                elif msg_type == "JOIN":
                    uid,name,group = cmds
                    logger.debug("'%s' joinded with uid: %s"%(name,uid))
                elif msg_type == "EXIT":
                    uid,name = cmds
                    logger.debug("'%s' left with uid: %s"%(name,uid))

            n.shouts('default group', sync_time+'0')
    except (KeyboardInterrupt, SystemExit):
        print 'User exit'
    n.stop()
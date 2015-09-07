from pyre import Pyre
from pyre import zhelper
import zmq
import logging
import sys

'''
threaded pupil sync script:
Similar to the simple script:
Group is set to 'default group'
Name is set to 'Script'

Catches keyboard input and sends it to all Pupils in the same group.

ctrl+c for exit
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
                uid,name,group,msg = cmds
                logger.debug("'%s' shouts '%s'."%(name,msg))
                handle_msg(name,msg)
            elif msg_type == "JOIN":
                uid,name,group = cmds
                logger.debug("'%s' joinded with uid: %s"%(name,uid))
            elif msg_type == "EXIT":
                uid,name = cmds
                logger.debug("'%s' left with uid: %s"%(name,uid))
            # elif msg_type == "WHISPER":
                # uid,name,group,msg = cmds
                # logger.debug("'%s' whispers '%s'."%(name,msg))
                # self.handle_msg(name,msg)
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
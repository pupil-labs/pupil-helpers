'''
(*)~----------------------------------------------------------------------------------
 Pupil - eye tracking platform
 Copyright (C) 2012-2016  Pupil Labs

 Distributed under the terms of the GNU Lesser General Public License (LGPL v3.0).
 License details are in the file license.txt, distributed as part of this software.
----------------------------------------------------------------------------------~(*)
'''

from time import time
from heapq import heappush
from pyre import Pyre
from urllib.parse import urlparse
from network_time_sync import Clock_Sync_Follower

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.getLogger('pyre').setLevel(logging.INFO)


class Clock_Service(object):
    """Represents a remote clock service and is sortable by rank."""
    def __init__(self, uuid,name, rank, port):
        super(Clock_Service, self).__init__()
        self.uuid = uuid
        self.rank = rank
        self.port = port
        self.name = name

    def __repr__(self):
        return '{:.2f}:{}'.format(self.rank, self.name)

    def __lt__(self, other):
        # "smallest" object has highest rank
        return (self.rank > other.rank) if isinstance(other, Clock_Service) else False


class Time_Object(object):
    """Utility class that represents the adjustable, local clock"""
    def __init__(self, base_offset=0.):
        super().__init__()
        self.base_offset = base_offset

    def get_time(self):
        """Returns the adjusted time"""
        return time() - self.base_offset

    def jump_time(self, offset):
        """
        This function can be used to test if the clock is currently adjustable,
        Pupil Capture does not allow time adjustments during recordings.

        Return True if time adjustment was successful, else return False
        """
        self.slew_time(offset)
        return True

    def slew_time(self, offset):
        """Function that adjusts the clock"""
        self.base_offset += offset


def run_time_sync(time_fn, jump_fn, slew_fn, pts_group):
    """Main follower logic"""

    # Start Pyre node and find clock services in `pts_group`
    discovery = Pyre('pupil-helper-follower')
    discovery.join(pts_group)
    discovery.start()
    logger.info('Joining "{}" group'.format(pts_group))

    # The leaderboard keeps track of all clock services
    # and is used to determine the clock master
    leaderboard = []
    follower_service = None

    def update_leaderboard(uuid, name, rank, port):
        """Add or update an existing clock service on the leaderboard"""
        for cs in leaderboard:
            if cs.uuid == uuid:
                if (cs.rank != rank) or (cs.port != port):
                    remove_from_leaderboard(cs.uuid)
                    break
                else:
                    # no changes. Just leave as is
                    return

        # clock service was not encountered before or has changed adding it to leaderboard
        cs = Clock_Service(uuid, name, rank, port)
        heappush(leaderboard, cs)
        logger.debug('{} added'.format(cs))

    def remove_from_leaderboard(uuid):
        """Remove an existing clock service from the leaderboard"""
        for cs in leaderboard:
            if cs.uuid == uuid:
                leaderboard.remove(cs)
                logger.debug('{} removed'.format(cs))
                break

    def evaluate_leaderboard(follower_service):
        """
        Starts/changes/stops the time follower service according to
        who the current clock master is.
        """
        if not leaderboard:
            logger.debug("nobody on the leader board.")
            if follower_service is not None:
                follower_service.terminate()
            return None

        current_leader = leaderboard[0]
        leader_ep = discovery.peer_address(current_leader.uuid)
        leader_addr = urlparse(leader_ep).netloc.split(':')[0]
        if follower_service is None:
            # make new follower
            follower_service = Clock_Sync_Follower(leader_addr,
                                                   port=current_leader.port,
                                                   interval=10,
                                                   time_fn=time_fn,
                                                   jump_fn=jump_fn,
                                                   slew_fn=slew_fn)
        else:
            # update follower_service
            follower_service.host = leader_addr
            follower_service.port = current_leader.port

        return follower_service

    try:
        # wait for the next Pyre event
        for event in discovery.events():
            if event.type == 'SHOUT':
                # clock service announcement
                # ill-formatted messages will be dropped
                try:
                    update_leaderboard(event.peer_uuid,
                                       event.peer_name,
                                       float(event.msg[0]),
                                       int(event.msg[1]))
                except Exception as e:
                    logger.debug('Garbage raised `{}` -- dropping.'.format(e))
                follower_service = evaluate_leaderboard(follower_service)
            elif ((event.type == 'LEAVE' and event.group == pts_group)
                    or event.type == 'EXIT'):
                remove_from_leaderboard(event.peer_uuid)
                follower_service = evaluate_leaderboard(follower_service)

    except KeyboardInterrupt:
        pass
    finally:
        discovery.leave(pts_group)
        discovery.stop()
        if follower_service is not None:
            follower_service.terminate()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    t = Time_Object(100.)
    run_time_sync(t.get_time, t.jump_time, t.slew_time, 'time_sync_default')

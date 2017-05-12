'''
(*)~----------------------------------------------------------------------------------
 Pupil - eye tracking platform
 Copyright (C) 2012-2016  Pupil Labs

 Distributed under the terms of the GNU Lesser General Public License (LGPL v3.0).
 License details are in the file license.txt, distributed as part of this software.
----------------------------------------------------------------------------------~(*)
'''

from time import time
from pyre import Pyre
from network_time_sync import Clock_Sync_Master

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.getLogger('pyre').setLevel(logging.INFO)

try:
    from pyre import __version__
    assert __version__ >= '0.3.1'
except (ImportError, AssertionError):
    raise Exception("Pyre version is to old. Please upgrade")


def run_time_sync_master(group):

    pts_group = group + '-time_sync-v0.2'
    clock_service = Clock_Sync_Master(time)

    # This example is a clock service only, not a clock follower.
    # Therefore the rank is designed to always trump all others.
    rank = 1000
    discovery = Pyre('pupil-helper-service')
    discovery.join(pts_group)
    discovery.start()
    logger.info('Joining "{}" group with rank {}'.format(pts_group, rank))

    def announce_clock_service_info():
        discovery.shout(pts_group, [repr(rank).encode(), repr(clock_service.port).encode()])

    try:
        for event in discovery.events():
            if event.type == 'JOIN' and event.group == pts_group:
                logger.info('"{}" joined "{}" group. Announcing service.'.format(event.peer_name, pts_group))
                announce_clock_service_info()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info('Leaving "{}" group'.format(pts_group))
        discovery.leave(pts_group)
        discovery.stop()
        clock_service.stop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    run_time_sync_master('default')

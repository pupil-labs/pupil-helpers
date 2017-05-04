'''
(*)~----------------------------------------------------------------------------------
 Pupil - eye tracking platform
 Copyright (C) 2012-2016  Pupil Labs

 Distributed under the terms of the GNU Lesser General Public License (LGPL v3.0).
 License details are in the file license.txt, distributed as part of this software.
----------------------------------------------------------------------------------~(*)
'''

import sys
from time import time
from pyre import Pyre
from random import random
from network_time_sync import Clock_Sync_Master

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.getLogger('pyre').setLevel(logging.INFO)

pyre_requirement = 'Pyre >= 0.3.1 is required for Time Sync to work'
try:
    from pyre import __version__
except ImportError:
    logger.error(pyre_requirement)
else:
    if __version__ < '0.3.1':
        logger.error(pyre_requirement)


def run_time_sync_service(pts_group, base_bias):

    clock_service = Clock_Sync_Master(time)

    # This example is a clock service only, not a clock follower. Therefore,
    # it cannot be synced. For simplification, we assume that it has been clock master.
    has_been_master = 1.
    has_been_synced = 0.
    tie_breaker = random()
    rank = 4*base_bias + 2*has_been_master + has_been_synced + tie_breaker

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
        clock_service.terminate()


if __name__ == '__main__':
    if len(sys.argv)  < 2:
        bias = 1.0
    else:
        bias = float(sys.argv[1])
    logging.basicConfig(level=logging.DEBUG)
    run_time_sync_service('time_sync_default', bias)

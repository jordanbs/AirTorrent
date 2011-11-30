#!/usr/bin/env python

import logging
import time

import torrent_session_manager

logging.basicConfig(level=logging.DEBUG)

path = '/home/jbschne/torrents/The.Pleasure.Garden.1925.DVDRip.x264-DiRTY.torrent'

try:
    tsm = torrent_session_manager.TorrentSessionManager()
    tsm.start()
    tsm.add_download(path)

    test_file = open('/tmp/test_mov.ts', 'w')
    while True:
        time.sleep(20)
        for torrent_download in tsm.torrent_downloads.values():
            logging.debug('WRITING FILE!!!')
            f = torrent_download.transcode_object.get_chunk()
            test_file.write(f.read())
except (KeyboardInterrupt, SystemExit):
    test_file.close()
    tsm.stop()


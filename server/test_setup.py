#!/usr/bin/env python

import logging
import time
import pdb

import torrent_session_manager

logging.basicConfig(level=logging.DEBUG)

path = '/home/jbschne/torrents/The.Pleasure.Garden.1925.DVDRip.x264-DiRTY.torrent'
playlist = None
global tsm



import BaseHTTPServer
class HLSServer(BaseHTTPServer.HTTPServer):
    pass

class HLSRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path.endswith('m3u8'):
            self.send_response(200)
            self.end_headers()
            for torrent_download in tsm.torrent_downloads.values():
                if not torrent_download.is_transcoding:
                    torrent_download.start_transcode()
                playlist = torrent_download.playlist
                break
            self.wfile.write(playlist)

        else:
            self.send_response(200)
            self.end_headers()
            for torrent_download in tsm.torrent_downloads.values():
                segment_file = torrent_download.transcode_object.get_chunk()
                break

            # this may be rather memory intensive...
            segment = segment_file.read()
            self.wfile.write(segment)



try:
    tsm = torrent_session_manager.TorrentSessionManager()
    tsm.start()
    tsm.add_download(path)
    
    for torrent_download in tsm.torrent_downloads.values():
        server_address = ('', 8000)
        httpd = HLSServer(server_address, HLSRequestHandler)
        httpd.serve_forever()

except (KeyboardInterrupt, SystemExit):
    tsm.stop()

#!/usr/bin/env python


import BaseHTTPServer
import logging
import urlparse

from torrent_session_manager import TorrentSessionManager

class HLSTorrentServer(BaseHTTPServer.HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, media_save_path):
        BaseHTTPServer.HTTPServer.__init__(self, server_address, RequestHandlerClass)
        self.media_save_path = media_save_path
        self._setup()

    def _setup(self):
        self.torrent_session_manager = TorrentSessionManager(self.media_save_path,
                                                             self.segment_request_path_func)
        self.torrent_session_manager.start()
        # XXX: quick hack to test, REMOVE ME
        self.torrent_added = False

    def add_torrent(self, torrent_file_path):
        # returns a dict of files to choose from
        torrent_download = self.torrent_session_manager.add_download(torrent_file_path)
        return (torrent_download.torrent_info_hash, torrent_download.video_files)

    def get_playlist(self, torrent_info_hash, file_index=0):
        # will block until first piece of file is finished downloading
        return self.torrent_session_manager.get_playlist(torrent_info_hash, file_index)
        
    def segment_request_path_func(self, torrent_info_hash, enclosure):
        address, addrlength = self.socket.getsockname()
        listen_address, port = self.server_address
        # TODO: fix TranscodeObject.get_chunk() to append urls properly to get rid of junk
        # FIXME: Don't hard code this...
        address = "demo.airtorrent.tk"
        return ('http://%s:%d/%s.%s?junk=0' % (address, port, torrent_info_hash, enclosure))

    def get_chunk(self, torrent_info_hash, chunk):
        return self.torrent_session_manager.get_chunk(torrent_info_hash, chunk)

    def shutdown(self):
        self.torrent_session_manager.stop()


class HLSTorrentRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    def do_GET(self):
        url_parts = urlparse.urlparse(self.path)

        # XXX: quick test hack
        if 'get_playlist' in url_parts.path:
            if self.server.torrent_added is False:
                self.server.torrent_added = True
            else:
                logging.debug("Extra get playlist, path: %s", self.path)
                playlist = self.server.get_playlist(self.server.info_hash)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(playlist)
                return
            self.server.info_hash, video_files = self.server.add_torrent(torrent_path)
            playlist = self.server.get_playlist(self.server.info_hash)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(playlist)
            return

        if not url_parts.path.endswith('.ts'):
            logging.warn('Invalid GET request')
            return

        # XXX: this could be cleaner...
        torrent_info_hash = url_parts.path.lstrip('/')
        torrent_info_hash = torrent_info_hash[:torrent_info_hash.index('.')]
        
        params = urlparse.parse_qs(url_parts.query)
        try:
            chunk = params['chunk']
        except(KeyError):
            logging.error('Chunk not specified')
            return

        segment_file = self.server.get_chunk(torrent_info_hash, chunk)

        if not segment_file:
            # TODO: make these error messages proper
            self.send_error(404)
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.writelines(segment_file)        




if __name__ == '__main__':
        logging.basicConfig(level=logging.INFO)
        server_address = ('', 8000)
        save_path = '/home/jbschne/media'
        torrent_path = "/home/jbschne/torrents/Who's.Harry.Crumb.1989.DVDRip.x264-DiRTY.mkv.torrent"
        httpd = HLSTorrentServer(server_address, HLSTorrentRequestHandler, save_path)
        try:
            httpd.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            httpd.shutdown()

#!/usr/bin/env python


import BaseHTTPServer
import logging
import tempfile
import urlparse
import urllib

from torrent_session_manager import TorrentSessionManager
from miro_library_manager import MiroLibraryManager

# FIXME: put this in a config
broadcast_address = 'demo.airtorrent.tk'

class HLSTorrentServer(BaseHTTPServer.HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, media_save_path):
        BaseHTTPServer.HTTPServer.__init__(self, server_address, RequestHandlerClass)
        self.media_save_path = media_save_path
        self._setup()

    def _setup(self):
        self.torrent_session_manager = TorrentSessionManager(self.media_save_path,
                                                             self.segment_request_path_func)
        self.torrent_session_manager.start()

        self.miro_library_manager = MiroLibraryManager(self.segment_request_path_func_library)

        self.broadcast_address = broadcast_address

    def add_torrent(self, torrent_file_path):
        # returns a dict of files to choose from
        torrent_download = self.torrent_session_manager.add_download(torrent_file_path)
        return (torrent_download.torrent_info_hash, torrent_download.video_files)

    def get_playlist(self, torrent_info_hash, file_index=0):
        # will block until first piece of file is finished downloading
        return self.torrent_session_manager.get_playlist(torrent_info_hash, file_index)
        
    def get_playlist_by_name(self, torrent_name, file_index=0):
        # will block until first piece of file is finished downloading
        return self.torrent_session_manager.get_playlist_by_name(torrent_name, file_index)

    def get_playlist_from_library(self, itemid):
        return self.miro_library_manager.get_playlist(itemid)

    def get_chunk_from_library(self, itemid, chunk):
        return self.miro_library_manager.get_chunk(itemid, chunk)

    def segment_request_path_func(self, torrent_info_hash, enclosure):
        address, addrlength = self.socket.getsockname()
        listen_address, port = self.server_address
        # TODO: fix TranscodeObject.get_chunk() to append urls properly to get rid of junk
        # FIXME: Don't hard code this...
        address = "demo.airtorrent.tk"
        return ('http://%s:%d/segments/%s.%s?junk=0' % (address, port, torrent_info_hash, enclosure))

    def segment_request_path_func_library(self, itemid, enclosure):
        address, addrlength = self.socket.getsockname()
        listen_address, port = self.server_address
        # TODO: fix TranscodeObject.get_chunk() to append urls properly to get rid of junk
        # FIXME: Don't hard code this...
        address = "demo.airtorrent.tk"
        return ('http://%s:%d/segments/library/%d.%s?junk=0' % (address, port, itemid, enclosure))

    def get_chunk(self, torrent_info_hash, chunk):
        return self.torrent_session_manager.get_chunk(torrent_info_hash, chunk)

    def shutdown(self):
        self.torrent_session_manager.stop()


class HLSTorrentRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    def do_GET(self):
        logging.debug('GET REQ path: %s' % self.path)
        url_parts = urlparse.urlparse(self.path)

        if url_parts.path.lstrip('/').startswith('playlists'):
            self.handle_playlists(url_parts)
            return

        if url_parts.path.lstrip('/').startswith('segments'):
            self.handle_segments(url_parts)
            return

        self.send_error(404)

    def handle_playlists(self, url_parts):
        if not url_parts.path.endswith('.m3u8'):
            logging.warn('Bad playlist request')
            self.send_error(404)
            return

        if url_parts.path.lstrip('/').startswith('playlists/library'):
            self.handle_library_playlist(url_parts)
            return

        torrent_name = url_parts.path.lstrip('/').lstrip('playlists/')
        torrent_name = torrent_name[:-len('.m3u8')]
        torrent_name = urllib.unquote(torrent_name)
        # XXX: Until conversion to CherryPy, map playlist by name rather than info hash
        playlist = self.server.get_playlist_by_name(torrent_name)

        if playlist is None:
            self.send_error(404)
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(playlist)

    def handle_library_playlist(self, url_parts):
        item_id = url_parts.path.lstrip('/').lstrip('playlists/library')
        item_id = item_id[:-len('.m3u8')]
        item_id = int(item_id)
        playlist = self.server.get_playlist_from_library(item_id)

        if playlist is None:
            self.send_error(404)
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(playlist)

    def handle_segments(self, url_parts):
        if not url_parts.path.endswith('.ts'):
            logging.warn('Invalid GET request')
            self.send_error(404)
            return

        if url_parts.path.lstrip('/').startswith('segments/library'):
            self.handle_library_segments(url_parts)
            return

        # XXX: this could be cleaner...
        torrent_info_hash = url_parts.path.lstrip('/').lstrip('segments/')
        torrent_info_hash = torrent_info_hash[:-len('.ts')]
        
        params = urlparse.parse_qs(url_parts.query)
        try:
            chunk = params['chunk']
            chunk = int(chunk[0])
        except(KeyError):
            logging.error('Chunk not specified')
            self.send_error(500)
            return

        segment_file = self.server.get_chunk(torrent_info_hash, chunk)

        if not segment_file:
            # TODO: make these error messages proper
            self.send_error(404)
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.writelines(segment_file)        

    def handle_library_segments(self, url_parts):
        itemid = url_parts.path.lstrip('/segments/library/')
        itemid = itemid[:-len('.ts')]
        itemid = int(itemid)

        params = urlparse.parse_qs(url_parts.query)
        try:
            chunk = params['chunk']
            chunk = int(chunk[0])
        except(KeyError):
            logging.error('Chunk not specified')
            self.send_error(500)
            return

        
        segment_file = self.server.get_chunk_from_library(itemid, chunk)

        if not segment_file:
            self.send_error(404)
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.writelines(segment_file)

    def do_POST(self):
        logging.debug('POST path: %s' % self.path)
        url_parts = urlparse.urlparse(self.path)    
        if url_parts.path.lstrip('/').startswith('upload'):
            self.handle_upload_torrent()
            return

    def handle_upload_torrent(self):
        #data = self.rfile.readlines()
        '''
        while data != '':
            if 'application/x-bittorrent' in data:
                data = self.rfile.readline()
                break
            data = self.rfile.readline()

        if data == '':
            logging.warn('No post payload')
            self.send_error(500)
            return

        torrent_data = ''
        next_data = self.rfile.readline()
        while next_data != '' and next_data not in '-----WebKitFormBoundary':
            torrent_data.join(next_data)
            next_data = self.rfile.readline()
        
        if torrent_data == '':
            logging.warn('No torrent file found')
            self.send_error(500)
            return
        '''
        content_length = int(self.headers['content-length'])
        torrent_data = self.rfile.read(content_length)
        # FIXME: Clean this up
        torrent_data = torrent_data[torrent_data.index('\r\n\r\n'):]
        torrent_data = torrent_data[4:]
        torrent_data = torrent_data[:torrent_data.index('-----WebKitFormBoundary')]

        torrent_file = tempfile.NamedTemporaryFile(delete=False)
        torrent_file.write(torrent_data)
        torrent_file.close()

        # TODO: Make this exception smarter, probably do it in the add_torrent function
        try:
            info_hash, video_files = self.server.add_torrent(torrent_file.name)
        except(RuntimeError):
            logging.warn('Invalid torrent file, could be a parsing error')
            self.send_error(500)
            return

        listen_address, port = self.server.server_address
        playlist_url = "http://%s:%d/playlists/%s.m3u8" % (self.server.broadcast_address, port,
                                                           info_hash)

        # blocks the response until a playlist can be generated
        # this will also start the transcode process
        self.server.get_playlist(info_hash)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(playlist_url)
        

if __name__ == '__main__':
        logging.basicConfig(level=logging.DEBUG)
        server_address = ('', 8000)
        save_path = '/home/jbschne/media'
        #torrent_path = "/home/jbschne/torrents/Who's.Harry.Crumb.1989.DVDRip.x264-DiRTY.mkv.torrent"
        httpd = HLSTorrentServer(server_address, HLSTorrentRequestHandler, save_path)
        try:
            httpd.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            httpd.shutdown()

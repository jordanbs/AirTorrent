import cherrypy
import logging
import tempfile

from torrent_session_manager import TorrentSessionManager
from miro_library_manager import MiroLibraryManager

#TODO: move this to a config
broadcast_address = 'demo.airtorrent.tk'

class HLSTorrentSession(object):

    def __init__(self, media_path):
        self.media_path = media_path
        self._setup()

    def _setup(self):
        self.torrent_session_manager = TorrentSessionManager(self.media_path,
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

class HLSPlaylist(object):
    def __init__(self, hls_session):
        self.hls_session = hls_session

    def default(self, infohash):
        ext = '.m3u8'
        if infohash.endswith(ext):
            infohash = infohash[:-len(ext)]

        playlist = self.hls_session.get_playlist(infohash)
        if not playlist:
            raise cherrypy.HTTPError(404)

        return playlist

    default.exposed = True

class HLSSegments(object):
    
    def __init__(self, hls_session):
        self.hls_session = hls_session

    def default(self, infohash, junk, chunk):
        chunk = int(chunk)
        segment_file = self.hls_session.get_chunk(infohash, chunk)
        if not segment_file:
            raise cherrypy.HTTPError(404)
        #TODO: dispatcher?
        return segment_file

    default.exposed = True

class HLSLibrary(object):

    def __init__(self, hls_session):
        self.hls_session = hls_session
        self.playlist = HLSPlaylist(hls_session)
        self.segments = HLSSegments(hls_session)
        self.playlist.exposed = True
        self.segments.exposed = True

class HLSTorrentServer(object):

    def __init__(self, media_path):
        self.hls_torrent_session = HLSTorrentSession(media_path)
        
        self.playlist = HLSPlaylist(self.hls_torrent_session)
        self.segments = HLSSegments(self.hls_torrent_session)
        self.playlist.exposed = True
        self.segments.exposed = True


import cherrypy
import logging
import tempfile

from torrent_session_manager import TorrentSessionManager
from miro_library_manager import MiroLibraryManager

class HLSTorrentSession(object):

    def __init__(self, media_path, broadcast_address):
        self.media_path = media_path
        self.broadcast_address = broadcast_address
        self._setup()

    def _setup(self):
        self.torrent_session_manager = TorrentSessionManager(self.media_path,
                                                             self.segment_request_path_func)
        self.torrent_session_manager.start()

        self.miro_library_manager = MiroLibraryManager(self.segment_request_path_func_library)


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
        # TODO: fix TranscodeObject.get_chunk() to append urls properly to get rid of junk
        address = self.broadcast_address
        return ('http://%s/segments/%s.%s?junk=0' % (address, torrent_info_hash, enclosure))

    def segment_request_path_func_library(self, itemid, enclosure):
        # TODO: fix TranscodeObject.get_chunk() to append urls properly to get rid of junk
        address = self.broadcast_address
        return ('http://%s/segments/library/%d.%s?junk=0' % (address, itemid, enclosure))

    def get_chunk(self, torrent_info_hash, chunk):
        return self.torrent_session_manager.get_chunk(torrent_info_hash, chunk)

    def shutdown(self):
        self.torrent_session_manager.stop()

class Playlist(object):
    def __init__(self, hls_torrent_session):
        self.hls_torrent_session = hls_torrent_session

    exposed = True

    def GET(self, infohash):
        import ipdb; ipdb.set_trace()
        ext = '.m3u8'
        if infohash.endswith(ext):
            infohash = infohash[:-len(ext)]

        playlist = self.hls_torrent_session.get_playlist(infohash)
        if not playlist:
            raise cherrypy.HTTPError(404)

        return playlist

class Segment(object):
    
    def __init__(self, hls_torrent_session):
        self.hls_torrent_session = hls_torrent_session

    exposed = True

    def GET(self, infohash, junk, chunk):
        chunk = int(chunk)
        segment_file = self.hls_torrent_session.get_chunk(infohash, chunk)
        if not segment_file:
            raise cherrypy.HTTPError(404)
        #TODO: dispatcher?
        return segment_file

class Library(object):

    def __init__(self, hls_torrent_session):
        self.hls_torrent_session = hls_torrent_session
        self.playlist = Playlist(hls_torrent_session)
        self.segments = Segment(hls_torrent_session)
        self.playlist.exposed = True
        self.segments.exposed = True

class Torrent(object):
    def __init__(self, hls_torrent_session):
        self.hls_torrent_session = hls_torrent_session

    exposed = True

    def POST(self, torrent_file):
        out = """<html>
        <body>
            torrent_file filename: %s<br />
            torrent_file mime-type: %s<br />
        </body>
        </html>"""

        data = torrent_file.file.read()
    
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(data)
        temp_file.close()

        self.hls_torrent_session.add_torrent(temp_file.name)
        return out % (temp_file.name, torrent_file.content_type)


class HLSTorrentServer(object):

    def __init__(self, media_path, broadcast_address):
        self.hls_torrent_session = HLSTorrentSession(media_path, broadcast_address)
        
        self.playlist = Playlist(self.hls_torrent_session)
        self.segments = Segment(self.hls_torrent_session)
        self.torrent = Torrent(self.hls_torrent_session) 
        self.playlist.exposed = True
        self.segments.exposed = True

    exposed = True

    def GET(self):
        return """
            <html><body>
                <h2>Upload a file</h2>
                    <form action="torrent" method="post" enctype="multipart/form-data">
                        filename: <input type="file" name="torrent_file" /><br />
                        <input type="submit" />
                    </form>
                <h2>Download a file</h2>
                <a href='download'>This one</a>
            </body></html>
            """

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    config = 'config.ini'
    cherrypy.config.update(config)
    hls_torrent_server = HLSTorrentServer(cherrypy.config['torrent_save_dir'],
                                          cherrypy.config['broadcast_addr'])
    cherrypy.quickstart(hls_torrent_server, '/', config)

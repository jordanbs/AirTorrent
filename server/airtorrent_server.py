import cherrypy
import simplejson as json
import logging
import tempfile

import hls_torrent_session as hlsts

class Playlist(object):
    def __init__(self, hls_torrent_session):
        self.hls_torrent_session = hls_torrent_session

    exposed = True

    def GET(self, infohash):
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
        ext = '.ts'
        if infohash.endswith(ext):
            infohash = infohash[:-len(ext)]

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
        if str(torrent_file.content_type) != 'application/x-bittorrent':
            raise cherrypy.HTTPError(415)
        
        data = torrent_file.file.read()
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(data)
        temp_file.close()

        infohash, video_files = self.hls_torrent_session.add_torrent(temp_file.name)
        url = 'http://%s/playlist/%s.m3u8' % (cherrypy.config['broadcast_addr'], infohash)
        #TODO: Make appropriate for multiple video files
        return json.dumps({'playlistUrl': url})


class HLSTorrentServer(object):

    def __init__(self, hls_torrent_session):
        self.hls_torrent_session = hls_torrent_session
        
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

class HLSTorrentPlugin(cherrypy.process.plugins.SimplePlugin):

    def exit(self):
        self.hls_torrent_session.shutdown()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    config = 'config.ini'
    cherrypy.config.update(config)

    media_path = cherrypy.config['torrent_save_dir']
    broadcast_address = cherrypy.config['broadcast_addr']
    hls_torrent_session = hlsts.HLSTorrentSession(media_path, broadcast_address)

    hls_torrent_plugin = HLSTorrentPlugin(cherrypy.engine)
    hls_torrent_plugin.hls_torrent_session = hls_torrent_session
    cherrypy.engine.hls_torrent_plugin = hls_torrent_plugin
    cherrypy.engine.hls_torrent_plugin.subscribe()

    hls_torrent_server = HLSTorrentServer(hls_torrent_session)
    cherrypy.quickstart(hls_torrent_server, '/', config)

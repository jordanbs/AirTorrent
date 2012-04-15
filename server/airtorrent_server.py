import cherrypy
import logging
import tempfile

import hls_torrent_session as hlsts

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
        self.hls_torrent_session = hlsts.HLSTorrentSession(media_path, broadcast_address)
        
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

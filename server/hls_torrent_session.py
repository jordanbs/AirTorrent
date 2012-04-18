from torrent_session_manager import TorrentSessionManager

class HLSTorrentSession(object):

    def __init__(self, media_path, broadcast_address):
        self.media_path = media_path
        self.broadcast_address = broadcast_address
        self._setup()

    def _setup(self):
        self.torrent_session_manager = TorrentSessionManager(self.media_path,
                                                             self.segment_request_path_func)
        self.torrent_session_manager.start()

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


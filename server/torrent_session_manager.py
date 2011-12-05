

import libtorrent as lt
import logging
import sys
import threading

from torrent_download_manager import *

class TorrentSessionManager(threading.Thread):
    '''
    This class represents the outermost phase of the progressive torrent
    download and transcode
    '''

    def __init__(self, save_directory_path, request_path_func):
        super(TorrentSessionManager, self).__init__()
        self.save_directory_path = save_directory_path
        self.request_path_func = request_path_func
        self._setup()

    def _setup(self):
        self.session = lt.session()
        self.session.set_alert_mask(lt.alert.category_t.progress_notification |
                                    lt.alert.category_t.storage_notification |
                                    lt.alert.category_t.status_notification)
        self.torrent_downloads = dict()

    def _start_listening(self):
        self.session.listen_on(10000, 20000)

    def stop(self):
        self.is_running.clear()

    def add_download(self, metainfo_file_path):
        
        torrent_download_manager =  TorrentDownloadManager(metainfo_file_path, 
                                                           self.save_directory_path,
                                                           self.request_path_func)
        torrent_handle =  self.session.add_torrent(torrent_download_manager.params)
        torrent_download_manager.torrent_handle = torrent_handle

        torrent_info_hash = torrent_download_manager.torrent_info_hash

        self.torrent_downloads[torrent_info_hash] = torrent_download_manager
        torrent_download_manager.start()

        return torrent_download_manager
    
    def get_playlist(self, torrent_info_hash, file_index=0):
        '''
        returns a m3u8 playlist, blocks until first piece of file_index is finished
        '''
        try:
            torrent_download_manager = self.torrent_downloads[torrent_info_hash]
        except(KeyError):
            logging.warn('Torrent info hash is invalid')
            return None

        # transcoding has to start to generate the playlist
        # FIXME: threading issue here... for some reason this is blocking the download from starting
        if not torrent_download_manager.is_transcoding:
            torrent_download_manager.start_transcode(file_index)
        
        playlist = torrent_download_manager.playlist
        return playlist

    def get_chunk(torrent_info_hash, chunk):
        try:
            torrent_download_manager = self.torrent_downloads[torrent_info_hash]
        except(KeyError):
            logging.warn('Torrent info hash is invalid, cannot retreive chunk')
            return None

        return torrent_download_manager.get_chunk(chunk)

    def run(self):
        '''
        Run loop, will block until termination, instantiates its own
        thread
        '''
        self._start_listening()
        self.is_running = threading.Event()
        self.is_running.set()
        self.event_loop()

    def event_loop(self):
        while self.is_running.is_set():
            one_second = 1000
            self.session.wait_for_alert(one_second)
            alert = self.session.pop_alert()
            if alert is None:
                continue
            
            if not isinstance(alert, lt.torrent_alert):
                continue

            # identify torrent_download_manager
            torrent_info = alert.handle.get_torrent_info()
            torrent_info_hash = str(torrent_info.info_hash())
            torrent_download_manager = self.torrent_downloads[torrent_info_hash]

            if type(alert) is lt.piece_finished_alert:
                # identify torrent_download_manager and handle piece
                torrent_download_manager.handle_piece_finished(alert.piece_index)

            elif type(alert) is lt.read_piece_alert:
                torrent_download_manager.handle_piece_read(alert.buffer, alert.piece, alert.size)
            
            elif type(alert) is lt.torrent_resumed_alert:
                torrent_download_manager.check_piece_buffers()
                
        self.shutdown()

    def shutdown(self):
        for torrent_download in self.torrent_downloads.values():
            torrent_download.shutdown()


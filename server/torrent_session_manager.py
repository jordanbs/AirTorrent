

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

    def __init__(self):
        super(TorrentSessionManager, self).__init__()
        self._setup()

    def _setup(self):
        self.session = lt.session()
        self.session.set_alert_mask(lt.alert.category_t.progress_notification |
                                    lt.alert.category_t.storage_notification)
        self.torrent_downloads = dict()
        self.save_directory_path = '/home/jbschne/media'

    def _start_listening(self):
        self.session.listen_on(10000, 20000)

    def stop(self):
        self.is_running.clear()

    def add_download(self, metainfo_file_path):
        
        torrent_download_manager =  TorrentDownloadManager(metainfo_file_path, 
                                                           self.save_directory_path)
        torrent_handle =  self.session.add_torrent(torrent_download_manager.params)
        torrent_download_manager.torrent_handle = torrent_handle

        torrent_info = torrent_handle.get_torrent_info()
        torrent_info_hash = str(torrent_info.info_hash())
        self.torrent_downloads[torrent_info_hash] = torrent_download_manager
        torrent_download_manager.start()

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
            if type(alert) is lt.piece_finished_alert:
                # identify torrent_download_manager and handle piece
                torrent_info = alert.handle.get_torrent_info()
                torrent_name = torrent_info.name()
                logging.debug('piece %d of %s downloaded' % (alert.piece_index, torrent_name))
                
                torrent_info_hash = str(torrent_info.info_hash())
                torrent_download_manager = self.torrent_downloads[torrent_info_hash]
                torrent_download_manager.handle_piece_finished(alert.piece_index)

            elif type(alert) is lt.read_piece_alert:
                torrent_info = alert.handle.get_torrent_info()
                torrent_name = torrent_info.name()
                logging.debug('piece %d of %s read' % (alert.piece, torrent_name))

                torrent_info_hash = str(torrent_info.info_hash())
                torrent_download_manager = self.torrent_downloads[torrent_info_hash]
                torrent_download_manager.handle_piece_read(alert.buffer, alert.piece, alert.size)

        self.shutdown()

    def shutdown(self):
        for torrent_download in self.torrent_downloads.values():
            torrent_download.shutdown()


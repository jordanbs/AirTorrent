

import logging
import sys
import re
import threading
import Queue

import libtorrent as lt
from miro import transcode

class TorrentDownloadManager:
    '''
    This class represents an inidividual torrent download, piping the
    completed pieces (in order) to ffmpeg
    '''
    def __init__(self, metainfo_file_path, save_directory_path):
        self.metainfo_file_path = metainfo_file_path
        self.save_directory_path = save_directory_path
        self._setup()

    def _setup(self):
        self.params = {}
        metainfo_file = open(self.metainfo_file_path, 'rb')
        metainfo = lt.bdecode(metainfo_file.read())
        metainfo_file.close()
        self.torrent_info = lt.torrent_info(metainfo)

        self.params['save_path'] = self.save_directory_path
        self.params['ti'] = self.torrent_info
        self.params['paused'] = True
        self.params['duplicate_is_error'] = True
        self.params['storage_mode'] = lt.storage_mode_t.storage_mode_allocate

        # torrent_handle must be set by instantiating class
        self.torrent_handle = None
        self.piece_completed_map = list()
        self.piece_buffers = dict()
        self.is_transcoding = False

    def select_video_files(self):
        # select only the video files for download
        file_priorities = self.torrent_handle.file_priorities()
        files = self.torrent_info.files()
        self.video_files = dict()
        self.next_piece_index = None
        for index in range(len(files)):
            f = files[index]
            if is_video_file(f.path):
                logging.info('identified media file %d: %s' % (index, f.path))
                self.video_files[index] = f
                # identify lowest piece
                start_piece = self.min_piece_for_file_index(index)
                if self.next_piece_index is None:
                    self.next_piece_index = start_piece
                else:
                    self.next_piece_index = min(self.next_piece_index, start_piece)
            else:
                file_priorities[index] = 0

        self.torrent_handle.prioritize_files(file_priorities)
    
    def min_piece_for_file_index(self, file_index):
        peer_request = self.torrent_info.map_file(file_index, 0, 0)
        return peer_request.piece

    def start(self):
        if self.torrent_handle is None:
            raise Exception('self.torrent_handle is undefined')

        self.select_video_files()
        self.torrent_info = self.torrent_handle.get_torrent_info()
        self.num_pieces = self.torrent_info.num_pieces()
        # setup completed piece mapping
        for piece_index in range(self.num_pieces):
            self.piece_completed_map.append(False)

        self.torrent_handle.set_sequential_download(True)
        self.torrent_handle.resume()
        
    def handle_piece_finished(self, piece_index):
        self.piece_completed_map[piece_index] = True
        
        piece_size = self.torrent_info.piece_size(piece_index)
        file_slices = self.torrent_info.map_block(piece_index, 0, piece_size)
        
        # len(file_slices) will be > 1 if multiple files in piece
        piece_has_media_file = False
        for file_slice in file_slices:
            if file_slice.file_index in self.video_files:
                piece_has_media_file = True
                break
        if not piece_has_media_file:
            logging.warning('no media file found in piece %d, ignoring piece' % piece_index)
            return

        self.torrent_handle.read_piece(piece_index)

    def handle_piece_read(self, piece_buffer, piece_index, size):
        # find relevant part of piece
        # load piece into buffer (check ordering)
        # pipe to ffmpeg
        # TODO: this scheme will not work for multiple media files in one piece, which is common.
        #       Solution: index self.piece_buffers by (piece_index, file_index)
        piece_size = self.torrent_info.piece_size(piece_index)
        file_slices = self.torrent_info.map_block(piece_index, 0, piece_size)
        # len(file_slices) will be > 1 if multiple files in piece
        for file_slice in file_slices:
            if file_slice.file_index in self.video_files:
                # find which part of piece is part of this file
                peer_request = self.torrent_info.map_file(file_slice.file_index, 0,
                                                          file_slice.size)
                if peer_request.piece == piece_index:
                    # adjust piece_buffer to start at beginning of media file
                    logging.debug('piece %d contains the start of a media file' %
                                  piece_index)
                    piece_buffer = piece_buffer[peer_request.start:]

                if len(piece_buffer) > peer_request.length:
                    # adjust piece_buffer to end at end of media file
                    logging.debug('piece %d contains the end of a media file' % piece_index)
                    piece_buffer = piece_buffer[:peer_request.length]

        self.piece_buffers[piece_index] = piece_buffer
        self.write_available_buffer_to_pipe()

    def write_available_buffer_to_pipe(self):
        # write as many piece_buffers to the pipe sequentially as available
        # might want to add some code to assert self.piece_buffers isn't leaking
        while self.next_piece_index in self.piece_buffers:
            if not self.is_transcoding:
                # first piece, setup transcode
                self.setup_transcode()
                self.is_transcoding = True
            self.transcode_writer.write(self.piece_buffers[self.next_piece_index])
            logging.debug('piece %d written to pipe' % self.next_piece_index)
            del self.piece_buffers[self.next_piece_index]
            # TODO: iterate to next valid piece, there may be gaps between media files
            self.next_piece_index += 1

    def setup_transcode(self):
        # TODO: make this work for multiple files. don't rely on path, pipe
        media_path = self.save_directory_path + '/' + self.video_files[0].path
        yes, media_info = transcode.needs_transcode(media_path)
        logging.debug('media info: %s', media_info)
        assert(media_info)
        self.transcode_object = transcode.TranscodeObject(True, media_info,
                                                          request_path_func)
        self.transcode_writer = TranscodeWriter(self.transcode_object)
        self.transcode_writer.start()
        self.transcode_object.transcode()

    def shutdown(self):
        if self.transcode_writer:
            self.transcode_writer.stop()

class TranscodeWriter(threading.Thread):
    ''' TranscodeWriter
    Spawns a new thread to buffer data and write to TranscodeObject
    '''
    def __init__(self, transcode_object):
        super(TranscodeWriter, self).__init__()
        self.transcode_object = transcode_object
        self.buffer_queue = Queue.Queue()
        self.is_running = threading.Event()

    def write(self, chunk):
        # appends chunk to the write buffer
        self.buffer_queue.put(chunk)

    def run(self):
        self.is_running.set()
        while self.is_running.is_set():
            chunk = self.buffer_queue.get()
            self._write(chunk)
   
    def _write(self, chunk):
        # for this thread to use, writes chunk to transcode_object
        logging.debug('writing chunk of size %d to %s' % (len(chunk),
                                                          type(self.transcode_object)))
        self.transcode_object.input_pipe.write(chunk)

    def stop(self):
        self.is_running.clear()
        self.buffer_queue.put(None)

def request_path_func(itemid, enclosure):
    return 'filler' + enclosure

def generate_container_regex():
    #TODO this should be defined by ffmpeg
    video_extensions = ['aaf', '3gp', 'avi', 'dat', 'flv', 'm4v', 'mkv', 'mov', 'mpeg',
                        'mpg', 'mpe', 'mp4', 'ogg', 'ogv', 'wmv']
    container_regex_string = '('
    for ext in video_extensions:
        container_regex_string.join(ext + '|')
    container_regex_string = container_regex_string.rstrip('|') + ')$'
    container_regex = re.compile(container_regex_string)
    return container_regex

container_regex = generate_container_regex()

def is_video_file(path):
    if container_regex.search(path):
        return True
    return False
    

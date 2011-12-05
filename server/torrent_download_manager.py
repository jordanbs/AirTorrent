

import logging
import sys
import re
import threading
import Queue
import time

import libtorrent as lt
from miro import transcode

class TorrentDownloadManager:
    '''
    This class represents an inidividual torrent download, piping the
    completed pieces (in order) to ffmpeg
    '''
    def __init__(self, metainfo_file_path, save_directory_path, request_path_func):
        self.metainfo_file_path = metainfo_file_path
        self.save_directory_path = save_directory_path
        self.request_path_func = request_path_func
        self._setup()

    def _setup(self):
        self.params = {}
        metainfo_file = open(self.metainfo_file_path, 'rb')
        metainfo = lt.bdecode(metainfo_file.read())
        metainfo_file.close()
        self.torrent_info = lt.torrent_info(metainfo)
        self.torrent_info_hash = str(self.torrent_info.info_hash())

        self.params['save_path'] = self.save_directory_path
        self.params['ti'] = self.torrent_info
        self.params['paused'] = True
        self.params['duplicate_is_error'] = True
        self.params['storage_mode'] = lt.storage_mode_t.storage_mode_allocate

        # torrent_handle must be set by instantiating class
        self.torrent_handle = None
        self.piece_completed_map = dict()
        self.piece_buffers = dict()
        self.is_transcoding = False
        self.transcode_object = None
        self.transcode_writer = None
        self.completed_piece_buffers_loaded = False

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
                start_piece = self.min_piece_for_file_index(index)
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
        self.torrent_name = self.torrent_info.name()
        self.num_pieces = self.torrent_info.num_pieces()
        # setup completed piece mapping

        self.torrent_handle.set_sequential_download(True)
        self.torrent_handle.resume()

    def check_piece_buffers(self):
        # checks if existing pieces have been loaded, loads them if not
        if not self.completed_piece_buffers_loaded:
            self._load_completed_piece_buffers()
            self.completed_piece_buffers_loaded = True

    def handle_piece_finished(self, piece_index):
        logging.debug('piece %d of %s downloaded' % (piece_index, self.torrent_name))
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
        piece_size = self.torrent_info.piece_size(piece_index)
        file_slices = self.torrent_info.map_block(piece_index, 0, piece_size)
        # len(file_slices) will be > 1 if multiple files in piece
        for file_slice in file_slices:
            if file_slice.file_index in self.video_files:
                # find which part of piece is part of this file
                peer_request = self.torrent_info.map_file(file_slice.file_index, 0,
                                                          file_slice.size)
                file_buffer = piece_buffer
                if peer_request.piece == piece_index:
                    # adjust piece_buffer to start at beginning of media file
                    logging.debug('piece %d contains the start of a media file' %
                                  piece_index)
                    file_buffer = file_buffer[peer_request.start:]

                if len(piece_buffer) > peer_request.length:
                    # adjust piece_buffer to end at end of media file
                    logging.debug('piece %d contains the end of a media file' % piece_index)
                    file_buffer = file_buffer[:peer_request.length]

                self.piece_buffers[(piece_index, file_slice.file_index)] = file_buffer

        logging.debug('piece %d of %s read' % (piece_index, self.torrent_name))

        if self.is_transcoding:
            self.write_available_buffer_to_pipe()

    def write_available_buffer_to_pipe(self):
        # write as many piece_buffers to the pipe sequentially as available
        # might want to add some code to assert self.piece_buffers isn't leaking
        while (self.next_piece_index, self.transcode_file_index) in self.piece_buffers:
            piece_buffer = self.piece_buffers[(self.next_piece_index, self.transcode_file_index)]
            self.transcode_writer.write(piece_buffer)
            logging.debug('piece %d with file %d written to pipe' % (self.next_piece_index,
                                                                     self.transcode_file_index))
            del self.piece_buffers[(self.next_piece_index, self.transcode_file_index)]
            self.next_piece_index += 1

    def _load_completed_piece_buffers(self):
        # update piece_copmleted_map
        # ensure that all completed pieces are buffered
        torrent_status = self.torrent_handle.status()
        pieces = torrent_status.pieces
        num_pieces = torrent_status.num_pieces

        # XXX: look into iterating on pieces, might be faster
        for piece_index in range(self.num_pieces):
            if pieces[piece_index]:
                self.torrent_handle.read_piece(piece_index)
                self.piece_completed_map[piece_index] = True
            else:
                self.piece_completed_map[piece_index] = False
            

    def _setup_transcode(self):
        # TODO: make this work for multiple files. don't rely on path, pipe
        # Must be run after the first piece of media has been downloaded
        
        # wait for first piece to become available
        # TODO: don't make this rely on sleep
        first_piece = self.min_piece_for_file_index(self.transcode_file_index)
        while (first_piece, self.transcode_file_index) not in self.piece_buffers:
            logging.debug('first piece not available, waiting on download')
            time.sleep(1)

        media_path = self.save_directory_path + '/' + self.video_files[0].path
        yes, media_info = transcode.needs_transcode(media_path)
        logging.debug('media info: %s', media_info)
        assert(media_info)
        self.transcode_object = transcode.TranscodeObject('-', None, 0, None, media_info,
                                                          self.request_path_func)
        self.playlist = self.transcode_object.playlist
        self.transcode_writer = TranscodeWriter(self.transcode_object)
        self.transcode_writer.start()

    def start_transcode(self, file_index=0):
        self.transcode_file_index = file_index
        self.next_piece_index = self.min_piece_for_file_index(file_index)
        self._setup_transcode()
        self.transcode_object.transcode()
        # XXX make is_transcoding an event to make thread safe?
        self.is_transcoding = True
        logging.info('transcoding started')
        
        return self.playlist

    def get_chunk(chunk):
        # TODO: track where the chunk is, if it skips, then toss the transcode_object and create
        # a new one at the start of the chunk. necessary for seeking
        return self.transcode_object.get_chunk()

    def shutdown(self):
        if self.transcode_writer:
            self.transcode_writer.stop()


# TODO: integrate this into the subclass of TranscodeObject
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
        # XXX move this to TranscodeObject subclass shutdown
        self.transcode_object.input_pipe.flush()
        self.transcode_object.input_pipe.close()
   
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
    

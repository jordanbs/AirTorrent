

import logging

from miro import app
from miro import transcode

class MiroLibraryManager:
    '''MiroLibraryManager
    Manages objects to transcode from miro's library
    '''

    def __init__(self, request_path_func):
        self.request_path_func = request_path_func
        self.transcodes = dict()

    def get_playlist(self, itemid):
        item_info = app.item_info_cache.get_info(itemid)
        
        if not item_info.video_path:
            logging.warn('No video_path for itemid %d' % itemid)
            return None

        transcode_object = self.start_transcode(item_info.video_path, itemid)
        self.transcodes[itemid] = transcode_object
        
        logging.debug('Playlist retreived for itemid %d' % itemid)
        return transcode_object.playlist

    def get_chunk(self, itemid, chunk):
        try:
            transcode_object = self.transcodes[itemid]
        except(KeyError):
            logging.warn('Invalid get_chunk for itemid %d' % itemid)
            return None

        logging.debug('Chunk %d retreived for itemid %d' % (chunk, itemid))
        return transcode_object.get_chunk()

    def start_transcode(self, media_path, itemid):
        transcode_object = self._setup_transcode(media_path, itemid)
        transcode_object.transcode()
        return transcode_object

    def _setup_transcode(self, media_path, itemid):
        yes, media_info = transcode.needs_transcode(media_path)
        logging.debug('media info: %s', media_info)
        assert(media_info)
        transcode_object = transcode.TranscodeObject(media_path, itemid, 0, None,
                                                     media_info, self.request_path_func)
        return transcode_object


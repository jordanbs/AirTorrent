import unittest
import logging

import transcode

test_media = ''

class TestTranscodeFunctions(unittest.TestCase):

    def setUp(self):
        pass

    def test_needs_transcode(self):
        boolean, media_info = transcode.needs_transcode(test_media)
        logging.debug('Media file needs transcode: %s' % boolean)
        logging.debug('Media info: %s' % str(media_info))

    def test_transcode(self):
        boolean, media_info = transcode.needs_transcode(test_media)
        transcode_object = transcode.TranscodeObject(test_media, 0, 0,
                                                     None, media_info,
                                                     request_path_func)
        transcode_object.transcode()
        logging.debug(transcode_object.get_chunk())

def request_path_func(itemid, enclosure):
    return 'filler' + str(itemid) + '.' + enclosure

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()

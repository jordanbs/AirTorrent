import logging

from miro import app
from miro import startup
from miro import messages
from miro import signals
from miro import appconfig
from miro import startfrontend
from miro.frontends.shell import application as shell_app

import hls_torrent_server as hls_server

def empty(a):
    return ''

def handle(message):
    print 'got message: ', message

def run_application():
    #app.config = appconfig.AppConfig()
    app.info_updater = shell_app.InfoUpdater()
    messages.FrontendMessage.install_handler(MessageHandler())
    startup.startup()
    
    logging.basicConfig(level=logging.DEBUG)
    server_address = ('', 8000)
    save_path = '/home/jbschne/media'
    httpd = hls_server.HLSTorrentServer(server_address, hls_server.HLSTorrentRequestHandler, save_path)
    try:
        httpd.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        httpd.shutdown()
    print 'startup exit'


class MessageHandler(messages.MessageHandler):
    def handle(self, message):
        print 'got message: ', message


if __name__ == '__main__':
    #from miro import bootstrap
    #bootstrap.bootstrap()
    #startfrontend.run_application('', dict(), None)
    run_application()

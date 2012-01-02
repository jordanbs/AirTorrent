import logging
import cherrypy

from miro import app
from miro import startup
from miro import messages
from miro import signals
from miro import appconfig
from miro import startfrontend
from miro.frontends.shell import application as shell_app

import hls_server
import web

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
    save_path = '/home/jbschne/media'
    httpd = web.AirTorrent(save_path)
    try:
        #TODO: Really, stop doing these hard coded strings. make a config goddammit.
        cherrypy.config.update('/home/jbschne/airtorrent-env/src/AirTorrent/server/config.ini')
        cherrypy.quickstart(httpd) 
    except (KeyboardInterrupt, SystemExit):
        pass
        #httpd.shutdown()
    print 'startup exit'


class MessageHandler(messages.MessageHandler):
    def handle(self, message):
        print 'got message: ', message


if __name__ == '__main__':
    #from miro import bootstrap
    #bootstrap.bootstrap()
    #startfrontend.run_application('', dict(), None)
    run_application()

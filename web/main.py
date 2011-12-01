import cherrypy
import os
import ConfigParser
import base64
import sqlite3


class AirTorrent:


    def index(self):
        # Ask for the user's name.
        value = '''
<html>
<head>
<link href="static/css/stylesheet.css" type="text/css" rel="stylesheet" />  
<link href="static/css/table.css" type="text/css" rel="stylesheet" />
<link href="static/css/upload.css" type="text/css" rel="stylesheet" />
<script type="text/javascript" src="static/scripts/enhance.js"></script>        
<script type="text/javascript" src="static/scripts/complete.min.js"></script>
<script type="text/javascript" language="javascript" src="static/scripts/jquery.js"></script>
<script type="text/javascript" language="javascript" src="static/scripts/jquery.dataTables.js"></script>
<script type="text/javascript" language="javascript" src="static/scripts/ColReorder.js"></script>
<script type="text/javascript" language="javascript" src="static/scripts/AirTorrentWebUI.js"></script>
<script type="text/javascript" src="static/scripts/jQuery.fileinput.js"></script>
<script type="text/javascript" src="static/scripts/example.js"></script>
</head>
<body>
'''
        value+=self.generateBody()
        return value;
    index.exposed = True

    
    def generateBody(self):
        #set up the menu div with proper playlists and filters
        #put something in the right div
        audiolink = 'libraryDiv?libType=audio'
        videolink = 'libraryDiv?libType=video'
        torrentlink = 'upload?temp=0'
        audio='<div data-ajaxlink="'+audiolink+'" class="menuLinkDiv library notloaded" id="menuLinkDivAudio"><div class="menuIcon" id="iconAudioDiv"></div><div class="menuTextLink">Audio</div></div>\n'
        video='<div data-ajaxlink="'+videolink+'" data-libid="0" class="menuLinkDiv library selected loaded" id="menuLinkDivVideo"><div class="menuIcon" id="iconVideoDiv"></div><div class="menuTextLink">Video</div></div>\n'
        torrent='<div data-ajaxlink="'+torrentlink+'" class="menuLinkDiv notloaded" id="menuLinkDivTorrent"><div class="menuIcon" id="iconTorrentDiv"></div><div class="menuTextLink">Torrent</div></div>\n'
        value = '<div id="menuDiv">\n<div id="filterMenuDiv">'+video+audio+torrent+'</div>\n'
        value+='''
</div>
<div id="contentDiv">
</div>
<div id="controlsDiv">
<img class="skipPrvBtnImg" src="static/images/skip_previous_disabled.png"/><img class="stopBtnImg" src="static/images/stop_disabled.png"/><img class="playBtnImg play enabled" src="static/images/play.png"/><img class="skipFwdBtnImg" src="static/images/skip_forward_disabled.png"/>
</div>
<div id="mediaDiv">
<div id="videoDiv">
</div>
<div id="audioDiv">
</div>
</div>
</body>
</html>
'''
        return value;
    generateBody.exposed = True
    
    
    def mediaDiv(self, source = None): 
        value = '<div id="media"><div id="mediaTitle">'+'Title as supplied by some AJAX goes here'+'</div>'
        value += '''
        <div id="mediaMain">
        <video width="640px" height="360px" autoplay="autoplay" controls>
        <source src="static/test.webm">
        </video>
        </div>
        <div id="mediaExtra">
        <a href="javascript:openPopOutMedia()">Open in new window</a>
        </div></div>
        '''
        return value;
    mediaDiv.exposed = True
    
    
    def menuDiv(self):
        #generate the entire menu html
        return ""
    menuDiv.exposed = True
    
    def filterMenuDiv(self):
        #generate the filter (ex: audio and video) portion of the menu
        return ""
    filterMenuDiv.exposed = True
        
    def playlistMenuDiv(self):
        #generate the html for the playlist section of the menu
        return ""
    playlistMenuDiv.exposed = True

    def libraryDiv(self, libType, libId="0"):
        #generate the table of library contents
        #columns will be a comma deliminated list
        if libType=="audio":
            columns = "id,file_type,entry_title,album,artist,genre"
            filters = "file_type = 'audio'"
        elif libType=="video":
            columns = "id,file_type,entry_title,album,artist,genre"
            filters = "file_type = 'video'"
        else:
            columns = "id,file_type,entry_title,album,artist,genre"
            filters = "file_type = 'audio'"
        conn = sqlite3.connect('sqlitedb')
        cursor = conn.cursor()
        columnList = columns.rsplit(',')
        table=""
        #cutting some corners here with the SQL. This is not secure, fix later!!!
        query = "SELECT "+columns+" FROM item WHERE "+filters
        cursor.execute(query)
        
        #set up the table header
        table+='<div id="containerDiv'+str(libId)+'" class="containerDiv">\n<table cellpadding="0" cellspacing="0" border="0" class="display" id="libraryTable'+str(libId)+'">'
        
        row=cursor.fetchone()
        if 1:
            table+='<thead>\n'
            table+='<th></th>\n'
            for i in range(2, len(columnList)):
                if type(row[i]) is int:
                    table+='<th>'+columnList[i]+'</th>\n'
                else:
                    table+='<th>'+columnList[i]+'</th>\n'
            table+='</thead>\n'
        
        #set up the body of the table
        table+='<tbody>\n'
        count=0;
        
        while row:
            table+='<tr class="'+str(row[0])+' '+str(row[1])+'">\n'
            table+='<td></td>'
            for i in range(2, len(columnList)):
                table+='<td>'+str(row[i])+'</td>\n'
            row = cursor.fetchone()
            count+=1
            table+='</tr>\n'
        
        table+='</tbody>\n</table>\n</div>\n'
      
        return table
    libraryDiv.exposed = True
        
    def createPlaylist(self, playlistname, itemid):
        #create new playlist in  miro using given song
        #return new playlist section div
        return ""
    createPlaylist.exposed = True

    def deletePlaylist(self, playlistname):
        #delete playlist from miro
        #return new playlist section div
        return ""
    deletePlaylist.exposed = True
    
    def addWatchlistFolder(self, folder):
        #add folder to miro watchlist folders
        #return success or failure
        return ""
    addWatchlistFolder.exposed = True
    
    def removeWatchlistFolder(self, folder):
        #remove folder from miro watchlist folders
        #return success or failure
        return ""
    removeWatchlistFolder.exposed = True
        
    def upload(self, temp, libId):
        out = '<div id="containerDiv'+str(libId)+'" class="containerDiv torrent">'
        out+= """
    <div id="headerDiv">Torrent Upload</div>
    <div id="uploadInstructions">Upload a torrent file containing a video and begin watching nearly instantly.</div>
    <div id="formDiv">   
    <form id="uploadForm" target="uploadIframe" action="uploadSubmit" method="post" enctype="multipart/form-data">
        <fieldset>
            <input id="file" type="file" name="myFile"/>
            <input id="upload" type="submit" value="Upload Torrent"/>
        </fieldset>
        <br>
        <img id="loadWheelImg" class="hidden" src="static/images/loading_wheel.gif" />
    </form>
    
    <iframe style="display:none;" id="uploadIframe" onload="torrentReturned()"></iframe>
    </div>
</div>
        """
        return out;
    upload.exposed = True

    def uploadSubmit(self, myFile):
        out = """<html>
        <body>
            myFile length: %s<br />
            myFile filename: %s<br />
            myFile mime-type: %s
        </body>
        </html>"""


        # Although this just counts the file length, it demonstrates
        # how to read large files in chunks instead of all at once.
        # CherryPy reads the uploaded file into a temporary file;
        # myFile.file.read reads from that.
        size = 0
        while True:
            data = myFile.file.read(8192)
            if not data:
                break
            size += len(data)

        return out % (size, myFile.filename, myFile.content_type)
        #return("<html><body>static/test.webm</body></html>")
    uploadSubmit.exposed = True    
        
conf = os.path.join(os.path.dirname(__file__), 'config.ini')

if __name__ == '__main__':
    # CherryPy always starts with app.root when trying to map request URIs
    # to objects, so we need to mount a request handler root. A request
    # to '/' will be mapped to HelloWorld().index().
    cherrypy.config.update({'server.socket_host': '192.168.1.98'})
    cherrypy.quickstart(AirTorrent(), config=conf)
else:
    # This branch is for the test suite; you can ignore it.
    cherrypy.config.update({'server.socket_host': '192.168.1.98'})
    cherrypy.tree.mount(AirTorrent(), config=conf)
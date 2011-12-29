import cherrypy
import os
import sqlite3
import mako

class AirTorrent:
    def __init__(self):
        mako_lookup = TemplateLookup(directories=['.'])
        self.main_tpl = Template(filename='/main.tpl',
                                 module_directory='./templates',
                                 lookup=mako_lookup)

    def index(self):
        stuff = {
            audiolink: 'libraryDiv?libType=audio',
            videolink: 'libraryDiv?libType=video',
            torrentlink: 'upload?temp=0'
        }
        return self.main_tpl.render(stuff)
    index.exposed = True
    
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
            columns = "id,file_type,entry_title,title_tag,artist,album,track,duration,genre,year"
            filters = "file_type = 'audio'"
        elif libType=="video":
            columns = "id,file_type,entry_title,title_tag,duration,creationTime, episode_number, season_number"
            filters = "file_type = 'video'"
        else:
            #this is for playlists...but yet to finish that part
            columns = "id,file_type,entry_title,album,artist,genre"
            filters = "file_type = 'audio'"
        conn = sqlite3.connect('/home/jbschne/.miro/sqlitedb')
        cursor = conn.cursor()
        table=""
        #cutting some corners here with the SQL. This is not secure, fix later!!!
        query = "SELECT "+columns+" FROM item WHERE "+filters
        cursor.execute(query)
        
        #set up the table header
        table+='<div id="containerDiv'+str(libId)+'" class="containerDiv">\n<table cellpadding="0" cellspacing="0" border="0" class="display" id="libraryTable'+str(libId)+'">'
        
        
        
        
        
        #set up the actual table
        if(libType=="audio"):
            table+='''
<thead>
<tr>
<th class="playIconRow"></th>
<th>Name</th>
<th>Artist</th>
<th>Album</th>
<th>Track</th>
<th>Time</th>
<th>Genre</th>
<th>Year</th>
</tr>
</thead>
<tbody>
'''
            row=cursor.fetchone()
            while row:
                table+='<tr class="'+str(self.cleanCell(row[0]))+' '+str(self.cleanCell(row[1]))+'">\n'
                table+='<td class="playIconRow"></td>\n'
                if(row[3]):
                    table+='<td class="mediaTitleCell"><div class="cell">'+str(self.cleanCell(row[3]))+'</div></td>\n'
                else:
                    table+='<td class="mediaTitleCell"><div class="cell">'+str(self.cleanCell(row[2]))+'</div></td>\n'
                table+='<td class="mediaArtistCell"><div class="cell">'+str(self.cleanCell(row[4]))+'</div></td>\n'
                table+='<td class="mediaAlbumCell"><div class="cell">'+str(self.cleanCell(row[5]))+'</div></td>\n'
                table+='<td><div class="cell">'+str(self.cleanCell(row[6]))+'</div></td>\n'
                seconds = self.cleanCell(row[7])/1000
                duration = "%01d:%02d" % (seconds/60, seconds%60)
                table+='<td><div class="cell">'+duration+'</div></td>\n'
                table+='<td><div class="cell">'+str(self.cleanCell(row[8]))+'</div></td>\n'
                table+='<td><div class="cell">'+str(self.cleanCell(row[9]))+'</div></td>\n'
                table+='</tr>\n'
                row = cursor.fetchone()
        elif(libType=="video"):
            table+='''
<thead>
<tr>
<th class="playIconRow"></th>
<th>Name</th>
<th>Time</th>
<th>Date Added</th>
<th>Episode Number</th>
<th>Season Number</th>
</tr>
</thead>
<tbody>
'''
            row=cursor.fetchone()
            while row:
                table+='<tr class="'+str(self.cleanCell(row[0]))+' '+str(self.cleanCell(row[1]))+'">\n'
                table+='<td class="playIconRow"></td>\n'
                if(row[3]):
                    table+='<td class="mediaTitleCell"><div class="cell">'+str(self.cleanCell(row[3]))+'</div></td>\n'
                else:
                    table+='<td class="mediaTitleCell"><div class="cell">'+str(self.cleanCell(row[2]))+'</div></td>\n'
                seconds = self.cleanCell(row[4])/1000
                duration = "%01d:%02d" % (seconds/60, seconds%60)
                table+='<td><div class="cell">'+duration+'</div></td>\n'
                table+='<td><div class="cell">'+str(self.cleanCell(row[5]))+'</div></td>\n'
                table+='<td><div class="cell">'+str(self.cleanCell(row[6]))+'</div></td>\n'
                table+='<td><div class="cell">'+str(self.cleanCell(row[7]))+'</div></td>\n'
                table+='</tr>\n'
                row = cursor.fetchone()
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
    <form id="uploadForm" target="uploadIframe" action="http://demo.airtorrent.tk:8000/upload" method="post" enctype="multipart/form-data">
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
        return("static/test.webm")
    uploadSubmit.exposed = True
    
    def cleanCell(self, cell):
        if cell==None:
            return " ";
        else:
            return cell;
        
conf = os.path.join(os.path.dirname(__file__), 'config.ini')

if __name__ == '__main__':
    # CherryPy always starts with app.root when trying to map request URIs
    # to objects, so we need to mount a request handler root. A request
    # to '/' will be mapped to HelloWorld().index().
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.quickstart(AirTorrent(), config=conf)
else:
    # This branch is for the test suite; you can ignore it.
    cherrypy.config.update({'server.socket_host': '192.168.1.98'})
    cherrypy.tree.mount(AirTorrent(), config=conf)

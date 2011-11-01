import cherrypy
import os
import ConfigParser
import base64



class AirTorrent:


    def index(self):
        # Ask for the user's name.
        value = '''
<html>
<head>
<link rel="stylesheet" type="text/css" href="css/stylesheet.css" />
<script type="text/javascript">
  function updateAJAX(div, pageLink){
    var xmlhttp;
      if (window.XMLHttpRequest){
      // code for IE7+, Firefox, Chrome, Opera, Safari
        xmlhttp=new XMLHttpRequest();
      }
      else{// code for IE6, IE5
        xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
      }
      xmlhttp.onreadystatechange=function(){
        if (xmlhttp.readyState==4 && xmlhttp.status==200){
          document.getElementById(div).innerHTML=xmlhttp.responseText;
        }
      }
      xmlhttp.open("GET",pageLink,true);
      xmlhttp.send();
  }
</script>
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"></script>
        <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"></script>
<script type="text/javascript">
$(document).ready(function(){

  window.clickedFolder = $("div.listLinkDiv:first");
  window.selectedFolderColor = "grey"
  window.clickedFolderColor = "#222222"
  window.normalFolderColor = "black"
  $(".listLinkDiv").live('click',function(){
    $(window.clickedFolder).css("background-color", window.normalFolderColor);
    $(this).css("background-color", window.clickedFolderColor);
    window.clickedFolder = this;
  });
  
  $(".listLinkDiv").live('mouseover', function(){
    if(this==window.clickedFolder){
      $(this).css("background-color", window.clickedFolderColor);
    }
    else{
      $(this).css("background-color", window.selectedFolderColor);
    }
  });
  
  $(".listLinkDiv").live('mouseout', function(){
    if(this==window.clickedFolder){
      $(this).css("background-color", window.clickedFolderColor);
    }
    else{
      $(this).css("background-color", window.normalFolderColor);
    }
  });
});
</script>
</head>
<body>'''
        value+=self.leftListContent()
        return value;
    index.exposed = True

    def printFiles(self, sysdir):
        value=""
        sysdir = sysdir+"="
        sysdir = base64.urlsafe_b64decode(sysdir.encode('ascii'))
        os.chdir(sysdir)
        files = filter(os.path.isfile, os.listdir(os.curdir))
        for file in files:
            newsysdir = base64.urlsafe_b64encode(sysdir)
            value+='<a href="javascript:updateAJAX(\'rightDiv\',\'mediaContent\')'+'">'+file+'</a><br>'  
        return value
    printFiles.exposed = True
        
    def printDirectories(self, sysdir, style = None):
        value='''

'''
        jslink=""
        sysdir = sysdir+'='
        sysdir = base64.urlsafe_b64decode(sysdir.encode('ascii'))
        os.chdir(sysdir)
        directories = filter(os.path.isdir, os.listdir(os.curdir))
        if style is None:
            for directory in directories:
                newsysdir = base64.urlsafe_b64encode(sysdir+"\\"+directory)
                jslink='javascript:updateAJAX(\'rightDiv\',\'listContent?sysdir='+newsysdir+'\')'
                divID='listLinkDiv'+directory
                value+='<a href="'+jslink+'">'+directory+'</a><br>'
        else:
            for directory in directories:
                newsysdir = base64.urlsafe_b64encode(sysdir+"\\"+directory)
                jslink='javascript:updateAJAX(\'rightDiv\',\'listContent?sysdir='+newsysdir+'\')'
                divID='listLinkDiv'+directory
                value+='<div onclick="'+jslink+'" class="listLinkDiv" id="'+divID+'"><span class="listLinkSpan"><a href="'+jslink+'">'+directory+'</a></span></div>'
            
        return value
    printDirectories.exposed = True
    
    def leftListContentHelper(self, folder = None):
        value=""
        sysdir=""
        os.chdir(os.getcwd())
        Config = ConfigParser.ConfigParser()        
        Config.read(conf)
        options = Config.options('Media')
        if folder == None:
            if len(options) > 0:
                folder = options[0]
            else:
                value += "You currently have no media folders configured."
                return value
        if Config.has_option('Media', folder):
            #generate links
            sysdir = Config.get('Media', folder)
            sysdir = (sysdir[1:-1])
            sysdir = base64.urlsafe_b64encode(sysdir)
            value+=self.printDirectories(sysdir, "left")            
        else:
            value+="The folder parameter is not properly configured."
        return value
    leftListContentHelper.exposed = True
    
    def leftListContent(self):
        # List folder contents of a directory
        os.chdir(os.getcwd())
        Config = ConfigParser.ConfigParser()
        Config.read(conf)
        options = Config.options('Media')
        value = '''
<div id="leftDiv">
<div id="dropDownDiv">
<form id="directoryForm" name="directoryForm">
<select id="directoryMenu" name="directoryMenu" onChange="updateAJAX('directoryList', document.directoryForm.directoryMenu.options[document.directoryForm.directoryMenu.options.selectedIndex].value)">
'''
        for option in options:
            value+="<option value=leftListContentHelper?folder="+option+">"+option+"</option>"
        value+='</select></form></div><div id="directoryList">'+self.leftListContentHelper(None)+'</div>'
        value+='</div><div id="rightDiv">THIS IS OUR WELCOME PAGE. AS YOU CAN TELL, WE HAVE PUT A TON OF EFFORT INTO IT</div></body></html>'
        return value;
    leftListContent.exposed = True
    
    
    def listContent(self, sysdir = None, file = None):
        value = ""
        if not file:
            #list directory contests
            value+='<div id="directoryTitle">'+os.path.basename(base64.urlsafe_b64decode(sysdir.encode('ascii')))+'</div>'
            value+=self.printDirectories(sysdir)
            value+=self.printFiles(sysdir)
        return value
    listContent.exposed = True
    
    def mediaContent(self, source = None): 
        value = '<div id="media"><div id="mediaTitle">'+'Title as supplied by some AJAX goes here'+'</div>'
        value += '''
        <div id="mediaMain">
        <video width="640px" height="360px" autoplay="autoplay" controls>
        <source src="static/test.webm">
        </video>
        </div>
        <div id="mediaExtra">
        <a href="javascript:openPopOutMedia()">Open in new window (not functional yet)</a>
        </div></div>
        '''
        return value;
    mediaContent.exposed = True
    
    def mediaPopOutContent(self, source = None):
        #Display available media files and subfolders
        #
        if mediaType=="video":
            return '''<html>
                <head>
                <link rel="stylesheet" type="text/css" href="css/stylesheet.css" />
                <title>Test</title>
                </head>
                <body>
                <div id="mediaPopOut" style="height:100%">
                <video width="100%" height="100%" src="static/test.webm" controls>
                </video>
                </div>
                </body>
                </html>'''
    mediaPopOutContent.exposed = True
    

conf = os.path.join(os.path.dirname(__file__), 'config.ini')

if __name__ == '__main__':
    # CherryPy always starts with app.root when trying to map request URIs
    # to objects, so we need to mount a request handler root. A request
    # to '/' will be mapped to HelloWorld().index().
    cherrypy.quickstart(AirTorrent(), config=conf)
else:
    # This branch is for the test suite; you can ignore it.
    cherrypy.tree.mount(AirTorrent(), config=conf)
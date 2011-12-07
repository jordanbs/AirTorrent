$(document).ready(function(){     
  window.playlistHistory = new Array();
  window.tables = new Array();
  window.playingTableIndex = -1;
  window.currentPlaylistIndex = -1;
  window.timer;
  window.isFadingIn = false;           //used for some book-keeping with the controls div
  window.isShuffle = false;
  window.isLoop = false;
  window.isLoopOnce = false;
  window.loopCount = 0;
  window.selectedID = -1;
  window.playingID = -1;
  window.lastVolume = 0;
  $('.playbackTrack').hide()
  $('#videoDiv').hide();
  updateAJAX('contentDiv', 'libraryDiv?libType=video&libId=0', '0');

  $('.playbackCursor').drag(function(ev, dd){
    //$(this).css('left', dd.offsetX)
  });
  
  $('.volumeIconDiv').click(function(){
    var temp = parseInt($('.volumeKnobDiv').css('left'));
    $('.volumeKnobDiv').css('left', window.lastVolume);
    $('.mediaPlayer').get(0).volume = (window.lastVolume)/93;
    window.lastVolume = temp;
  });
  
  $('.volumeTrackDiv').mousedown(function(e){
    var val = e.offsetX + 9;
    if (val<0){
      val=0;
    }
    if (val>93){
      val=93;
    }
    $('.volumeKnobDiv').css('left', val);
    $('.mediaPlayer').get(0).volume = val/93;
    window.lastVolume = 0;
  });
  
  $('.volumeKnobDiv').drag(function(ev, dd){
    var orig = $(this).css('left');
    var val = (dd.offsetX);
    if (val<0){
      val=0;
    }
    if (val>93){
      val=93;
    }
    $(this).css('left', val);
    $('.mediaPlayer').get(0).volume = val/93;
    window.lastVolume = 0;
  }, {relative: true});
  
  $("tr.video").live('dblclick',function(){
    startNewPlaylist();
  });
  
  $("tr.audio").live('dblclick',function(){
    startNewPlaylist();
  });
  
//CONTROLS GUI
  $('#videoDiv').bind('mousemove', function(){
    if(window.timer){
        clearTimeout(window.timer);
        window.timer=0;
    }
    if(window.isFadingIn!=true){
      $("#controlsDiv.video").fadeIn();
      window.isFadingIn = true;
    }
    window.timer = setTimeout(function() {
      $("#controlsDiv.video").fadeOut();
      window.isFadingIn = false;
    }, 1200);
  });

  $('#controlsDiv.video').live('mouseleave', function(){
    if(window.timer){
      clearTimeout(window.timer);
      window.timer=0;
    }
    if(window.isFadingIn!=true){
      $("#controlsDiv.video").fadeIn();
      window.isFadingIn = true;
    }
    window.timer = setTimeout(function() {
      $("#controlsDiv.video").fadeOut();
      window.isFadingIn = false;
    }, 1200);
  });
  
  $('#controlsDiv.video').live('mouseenter', function(){
    if(timer){
        clearTimeout(timer);
        timer=0;
    }
  });
  
  
  
  //CONTROL BUTTONS
  $(".playBtnImgDiv.enabled.play").live('mousedown', function(){
    $(this).addClass('mousedown');
    //$(this).attr('src', 'static/images/play_active.png');
  });
  
  
  $(".playBtnImgDiv.enabled.play").live('mouseup', function(){
    $(this).removeClass('mousedown');
    if($('#libraryTable'+window.playingTableIndex+' tbody tr.playing').length > 0){
      var player = $('.mediaPlayer').get(0);
      player.play();
    }
    else{
      if($('.menuLinkDiv.selected').hasClass('torrent')){
        if($('.mediaPlayer').length > 0){
          //there's a torrent currently loaded in, so play
          var player = $('.mediaPlayer').get(0);
          player.play();
          return;
        }
        else{
          //do nothing, don't start a new playlist or anything
          return;
        }
      }
      startNewPlaylist();
    }
  });
  
  $(".playBtnImgDiv.enabled.pause").live('mousedown', function(){
    $(this).addClass('mousedown');
  });
  
  $(".playBtnImgDiv.enabled.pause").live('mouseup', function(){
    $(this).removeClass('mousedown');
    var player = $('.mediaPlayer').get(0);
    player.pause();
  });

  $('.skipFwdBtnImgDiv.enabled').live('mousedown', function(){
    $(this).addClass('mousedown');
  });
  $('.skipFwdBtnImgDiv.enabled').live('mouseup', function(){
    $(this).removeClass('mousedown');
    playNext();
  });
  
  $('.skipPrvBtnImgDiv.enabled').live('mousedown', function(){
    $(this).addClass('mousedown');
  });
  $('.skipPrvBtnImgDiv.enabled').live('mouseup', function(){
    $(this).removeClass('mousedown');
    playPrevious();
  });
  
  $('.stopBtnImgDiv.enabled').live('mousedown', function(){
    $(this).addClass('mousedown');
  });
  $('.stopBtnImgDiv.enabled').live('mouseup', function(){
    $(this).removeClass('mousedown');
    stopPlaylist();
  });
  
  
  
  
  $('.shuffleBtnDiv.off').live('mousedown', function(){
    $(this).addClass('mousedown');
  });
  $('.shuffleBtnDiv.off.mousedown').live('mouseup', function(){
    $(this).removeClass('mousedown');
    $(this).removeClass('off');
    $(this).addClass('on');
    window.isShuffle = true;
  });
  
  $('.shuffleBtnDiv.on').live('mousedown', function(){
    $(this).addClass('mousedown');
  });
  $('.shuffleBtnDiv.on.mousedown').live('mouseup', function(){
    $(this).removeClass('mousedown');
    $(this).removeClass('on');
    $(this).addClass('off');
    window.isShuffle = false;
  });
  
  
  
  $('.loopBtnDiv.off').live('mousedown', function(){
    $(this).addClass('mousedown');
  });
  $('.loopBtnDiv.off.mousedown').live('mouseup', function(){
    $(this).removeClass('mousedown');
    $(this).removeClass('off');
    $(this).addClass('on');
    window.isLoop = true;
    window.isLoopOnce = false;
  });
  
  $('.loopBtnDiv.on').live('mousedown', function(){
    $(this).addClass('mousedown');
  });
  $('.loopBtnDiv.on.mousedown').live('mouseup', function(){
    $(this).removeClass('mousedown');
    $(this).removeClass('on');
    $(this).addClass('once');
    window.isLoop = false;
    window.isLoopOnce = true;
  });
  
  
  $('.loopBtnDiv.once').live('mousedown', function(){
    $(this).addClass('mousedown');
  });
  $('.loopBtnDiv.once.mousedown').live('mouseup', function(){
    $(this).removeClass('mousedown');
    $(this).removeClass('once');
    $(this).addClass('off');
    window.isLoop = false;
    window.isLoopOnce = false;
  });
  
  
  
//TORRENT GUI  
  $('#upload').live('click', function(e){
    $('#loadWheelImg').removeClass('hidden');
    $('#upload').hide();
    var file=this.form[1].files[0];
    if(file){
      return;
    }
    else{
      alert('Please choose a torrent file');
      e.preventDefault();
      $('#loadWheelImg').addClass('hidden');
      $('#upload').show();
    }
  });

   
        

//RESIZING 
  $(window).resize(function() {
    if($(".containerDiv").length > 0){
      $('.dataTables_scroll').css("height", (($('#contentDiv').outerHeight(true))-($('.dataTables_filter').outerHeight(true))));
      $('.dataTables_scrollBody').css("height", (($('#contentDiv').outerHeight(true))-($('.dataTables_filter').outerHeight(true))-(29)));
    }
    var val = (this.currentTime/this.duration) * ($('.playbackTrack').outerWidth() - 18);
    $('.playbackCursor').css('left', val+'px');
    if(val>1){
      $('.playbackTrackLeftProgress').show();
    }
    else{
      $('.playbackTrackCenterProgress').css('right', $('.playbackTrack').outerWidth() - val - 9);
    }
    resizeColumns();
  });
  
  
//MENU GUI  
  $(".menuLinkDiv.notloaded").live('click',function(){
    var libId=$('.containerDiv').length;
    $(this).attr('data-libid', libId);
    var link=$(this).data('ajaxlink')+'&libId='+$(this).data('libid');
    updateAJAX('contentDiv', link);
    $('.menuLinkDiv.selected').toggleClass('selected'); 
    $(this).toggleClass('selected');  
    $(this).addClass('loaded');
    $(this).removeClass('notloaded');
  });
  
  $(".menuLinkDiv.loaded").live('click',function(){
    var libId = $(this).data('libid');
    $('.menuLinkDiv.selected').toggleClass('selected'); 
    $(this).toggleClass('selected');  
    $('.containerDiv.active').toggleClass('active'); 
    $('#containerDiv'+libId).toggleClass('active');
    resizeColumns();
  });
  
});


//FUNCTIONS


function updateAJAX(div, pageLink){
  if (arguments.length===2){
    libId="0";
  }
  var xmlhttp;
  if (window.XMLHttpRequest){
  // code for IE7+, Firefox, Chrome, Opera, Safari
    xmlhttp=new XMLHttpRequest();
  }
  else{// code for IE6, IE5
    xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  }
  xmlhttp.onreadystatechange=function(){
    if (xmlhttp.readyState===4 && xmlhttp.status===200){
      if(div==='contentDiv'){
        //if we're loading another library table in, append it to the content div
        var libId = $('.containerDiv').length;
        $('#contentDiv').append(xmlhttp.responseText);
        if($('#libraryTable'+libId).length > 0){
          //load table in
          window.tables[libId] = $('#libraryTable'+libId).dataTable({"sScrollY": "100%", "bPaginate": false, "sDom": 'Rlfrtip'});
          $('.dataTables_scroll').css("height", (($('#contentDiv').outerHeight(true))-($('.dataTables_filter').outerHeight(true))));
          $('.dataTables_scrollBody').css("height", (($('#contentDiv').outerHeight(true))-($('.dataTables_filter').outerHeight(true))-(29)));
          
          //Event handlers for new table
          $('#libraryTable'+libId+'_filter input').unbind('keyup.DT');
          $('#libraryTable'+libId+'_filter').html('<label><input type="text"></label>');  
          $('#libraryTable'+libId+'_filter input').bind('keyup.DT', function(){
            window.tables[libId].fnFilter($('#libraryTable'+libId+'_filter input').val());
            $('#libraryTable'+libId+' tbody tr.playing:not(.'+window.playingID+')').addClass('played');
            $('#libraryTable'+libId+' tbody tr.playing:not(.'+window.playingID+') img').remove();
            $('#libraryTable'+libId+' tbody tr.playing:not(.'+window.playingID+')').removeClass('playing');              
            $('#libraryTable'+libId+' tbody tr.selected:not(.'+window.selectedID+')').removeClass('selected');
          });
          $('#libraryTable'+libId+' tbody tr').live('click', function(){
            $('#libraryTable'+libId+' tr.selected').removeClass('selected'); 
            $(this).addClass('selected');
            window.selectedID = getMediaID($(this).attr('class').split(' '));
          });
          
          //select the first row automatically
          if($('#libraryTable'+libId+' tbody tr').length > 0){
            $('#libraryTable'+libId+' tr.selected').toggleClass('selected'); 
            $('#libraryTable'+libId+' tbody tr:eq(0)').toggleClass('selected');
          }
          //hide other tables, make this one visible
          $('.containerDiv.active').removeClass('active');
          $('#containerDiv'+libId).addClass('active');
          window.tables[libId].fnAdjustColumnSizing();
        }
        else{
          $('#file').customFileInput();
          $('.containerDiv.active').removeClass('active');
          $('#containerDiv'+libId).addClass('active');
        }
      }
      else{
        document.getElementById(div).innerHTML=xmlhttp.responseText;
      }
    }
  }
  xmlhttp.open("GET",pageLink,true);
  xmlhttp.send();
}



function randOrd(){
  return (Math.round(Math.random())-0.5); 
}

function torrentReturned(){
  var file = $('#upload').get(0).form[1].files[0];
  if(!file){
    return;
  }
  var src = "";
  if(file.fileName.length > 7){
    src = file.fileName.substr(0, file.fileName.length-7)+'m3u8';
  }
  else{
    $('#loadWheelImg').addClass('hidden');
    $('#upload').show();
    return;
  }
  $('#loadWheelImg').addClass('hidden');
  $('#upload').show();
  startTorrentPlayback(src);
}


function startTorrentPlayback(source){
  stopPlaylist();
  $('.playBtnImgDiv').addClass('enabled');
  $('.skipPrvBtnImgDiv').removeClass('enabled');
  $('.skipFwdBtnImgDiv').removeClass('enabled');
  $('.stopBtnImgDiv').addClass('enabled');
  window.playingTableIndex = -1; //this is already done in stopPlaylist, just here for clarity purposes
  newdiv='<video class="mediaPlayer video" width="100%" height="100%"><source src="http://demo.airtorrent.tk:8000/playlists/'+source+'"></video>'
  $('#videoDiv').append(newdiv);
  $('#controlsDiv').addClass('video');
  $('#videoDiv').show();
  var title="Uploaded Torrent"
  $('.progressTimelineTitle').html('<img class="progressTimelineIconAudio" src="static/images/mini-icon-audio.png"><img class="progressTimelineIconVideo" src="static/images/mini-icon-video.png">'+title);
  $('.progressTimelineArtist').html('');
  $('.progressTimelineAlbum').html('');
  
  
  $('.mediaPlayer').bind('play', function(){
    $(".playBtnImgDiv").addClass('pause');
    $(".playBtnImgDiv").removeClass('play');
  });
  $('.mediaPlayer').bind('pause', function(){
    $(".playBtnImgDiv").removeClass('pause');
    $(".playBtnImgDiv").addClass('play');
  });
  $('.mediaPlayer').bind('timeupdate', function(){
    //seek bar update
    var val = (this.currentTime/this.duration) * ($('.playbackTrack').outerWidth() - 18);
    $('.playbackCursor').css('left', val+'px');
    if(val>1){
      $('.playbackTrackLeftProgress').show();
    }
    $('.playbackTrackCenterProgress').css('right', $('.playbackTrack').outerWidth() - val - 9);
    $('.progressTimelineTimePlayed').html(secondstominutes(parseInt(this.currentTime)));
    $('.progressTimelineTimeLeft').html('-'+secondstominutes(parseInt(this.duration) - parseInt(this.currentTime)));
  });
  $('.mediaPlayer').bind('ended', function(){
    playNext();
  });
  window.playingID = -1;
  $('.mediaPlayer').get(0).volume = (parseInt($('.volumeKnobDiv').css('left')))/93;
  $('.playbackTrack').show()
  $('.playbackTrackCenterProgress').css('right', $('.playbackTrack').outerWidth() - $('.playbackTrackCenterProgress').css('left'));
  $('.playbackTrackLeftProgress').hide()
  $('.playbackTrackRightProgress').hide()
  $('.playbackCursor').css('left', 0+'px');
  $('.playbackCursor').show()
  $('.progressTimelineHeader').show();
  $('.progressTimelineTimeLeft').show();
  $('.progressTimelineTimePlayed').show();
  var player = $('.mediaPlayer').get(0);
  player.play();
}

function startNewPlaylist(){
  stopPlaylist();
  $('.playBtnImgDiv').addClass('enabled');
  $('.skipPrvBtnImgDiv').addClass('enabled');
  $('.skipFwdBtnImgDiv').addClass('enabled');
  $('.stopBtnImgDiv').addClass('enabled');
  window.playingTableIndex = $('.menuLinkDiv.selected').attr('data-libid');
  //parse the row id from the class
  id=getMediaID($('#libraryTable'+window.playingTableIndex+' tbody tr.selected:first').attr('class').split(' '));
  window.currentPlaylistIndex = window.playlistHistory.length;  //0
  window.playlistHistory[window.playlistHistory.length] = id;  
  loadContent(id); 
}

function stopPlaylist(){
  if(window.playingTableIndex > -1){
    $('#libraryTable'+window.playingTableIndex+' tbody tr').removeClass('played');
    $('#libraryTable'+window.playingTableIndex+' tbody tr.playing img').remove();
    $('#libraryTable'+window.playingTableIndex+' tbody tr').removeClass('playing');
  }
  window.playingID = -1;
  window.loopCount = 0;
  window.playlistHistory.length = 0;
  window.playingTableIndex = -1;
  window.currentPlaylistIndex = -1;
  $('#videoDiv').hide();
  $('#controlsDiv.video').removeClass('video');
  if(window.timer){
    clearTimeout(window.timer);
    window.timer=0;
  }
  $('#controlsDiv').show();
  $('.mediaPlayer').remove();
  $('.playBtnImgDiv').removeClass('pause');
  $('.playBtnImgDiv').addClass('play');
  $('.skipPrvBtnImgDiv').removeClass('enabled');
  $('.skipFwdBtnImgDiv').removeClass('enabled');
  $('.stopBtnImgDiv').removeClass('enabled');
  $('.playbackTrack').hide()
  $('.playbackCursor').css('left', 0+'px');
  $('.playbackCursor').hide()
  $('.playbackTrackCenterProgress').css('right', $('.playbackTrack').outerWidth() - $('.playbackTrackCenterProgress').css('left'));
  $('.playbackTrackLeftProgress').hide()
  $('.playbackTrackRightProgress').hide()
  $('.progressTimelineHeader').hide();
  $('.progressTimelineTimePlayed').html('');
  $('.progressTimelineTimeLeft').html('');
  $('.progressTimelineTimeLeft').hide();
  $('.progressTimelineTimePlayed').hide();
}

function playPrevious(){
  var id;
  if(window.isShuffle){
    //if in non random part of a random playlist, play previous song played
    if(window.currentPlaylistIndex > 0){
      window.currentPlaylistIndex=window.currentPlaylistIndex-1;
      id = window.playlistHistory[window.currentPlaylistIndex];
    }
    else{
      //current playlist is at beggining, so go back to end of playlist if looping
      if(window.isLoop || window.isLoopOnce){
        if(window.loopCount>0){
          //go back to end of playlist
          window.loopCount=window.loopCount-1;
          window.currentPlaylistIndex=window.playlistHistory.length-1;
          id = window.playlistHistory[window.currentPlaylistIndex];
        }
        else{
          stopPlaylist();
          return;
        }
      }
      else{
        stopPlaylist();
        return;
      }
    }
  }
  else{
    //play previous song in the table
    if($('#libraryTable'+window.playingTableIndex+' tbody tr.playing').length > 0){
      //if the curretly playing song is actually visible in the table
      if($('#libraryTable'+window.playingTableIndex+' tbody tr.playing').prev().length > 0){
        //take the previous song visible in the table
        id=getMediaID($('#libraryTable'+window.playingTableIndex+' tbody tr.playing').prev().attr('class').split(' '));
      }
      else{
        //if there is no previoius song, either go back to the end of the table for loop, or stop
        if(window.isLoop || window.isLoopOnce){
          if(window.loopCount>0){
            //go back to end of playlist
            window.loopCount=window.loopCount-1;
            id=getMediaID($('#libraryTable'+window.playingTableIndex+' tbody tr:last').attr('class').split(' '));
          }
          else{
            stopPlaylist();
            return;
          }
        }
        else{
          stopPlaylist();
          return;
        }
      }
    }
    else{
      //the current song is not visible, stop the playlist
      stopPlaylist();
      return;
    }
  }	
  if($('#libraryTable'+window.playingTableIndex+' tbody tr.'+id).length>0){
    //make sure ID is actually in the current table and hasn't been filtered out
    loadContent(id);
  }
  else{
    stopPlaylist();
    return;
  }
}

function playNext(){
  var id;
  if(window.playingTableIndex<0){
    //mainly here for the purpose of breaking when a torrent is done playing
    stopPlaylist();
    return;
  }
  if(window.isShuffle){
    //if in non random part of a random playlist
    if(window.currentPlaylistIndex < (window.playlistHistory.length-1)){   //example, playlist history is length 5, index is 3, not on last song in history
      window.currentPlaylistIndex++;
      id = window.playlistHistory[window.currentPlaylistIndex];
    }
    //else take random next song
    else{
      if($('#libraryTable'+window.playingTableIndex+' tbody tr:not(".played"):not(".playing")').length > 0){
        id=getMediaID($('#libraryTable'+window.playingTableIndex+' tbody tr:not(".played"):not(".playing")').random().attr('class').split(' '));
        window.currentPlaylistIndex++;
        window.playlistHistory[window.currentPlaylistIndex]=id;
      }
      else{
        if(window.isLoop){
          //go back to beginning of playlist
          window.loopCount++;
          window.currentPlaylistIndex=0;
          id = window.playlistHistory[window.currentPlaylistIndex];
        }
        else if (window.isLoopOnce){
          if(window.loopCount===0){
            window.loopCount++;
            window.currentPlaylistIndex=0;
            id = window.playlistHistory[window.currentPlaylistIndex];
          }
          else{
            stopPlaylist();
            return;
          }
        }
        else{
          stopPlaylist();
          return;
        }
      }
    }
  }
  else{
    //play next song in the table
    if($('#libraryTable'+window.playingTableIndex+' tbody tr.playing').length > 0){
      //if the curretly playing song is actually visible in the table
      if($('#libraryTable'+window.playingTableIndex+' tbody tr.playing').next().length > 0){
        //take the next song visible in the table
        id=getMediaID($('#libraryTable'+window.playingTableIndex+' tbody tr.playing').next().attr('class').split(' '));
      }
      else{
        //if there is no next song, either go back to the beggining of the table for loop, or stop
        if(window.isLoop){
          //go back to beginning of playlist
          id=getMediaID($('#libraryTable'+window.playingTableIndex+' tbody tr:first').attr('class').split(' '));
          window.loopCount++;
        }
        else if (window.isLoopOnce){
          if(window.loopCount==0){
            id=getMediaID($('#libraryTable'+window.playingTableIndex+' tbody tr:first').attr('class').split(' '));
            window.loopCount++;
          }
          else{
            stopPlaylist();
            return;
          }
        }
        else{
          stopPlaylist();
          return;
        }
      }
    }
    else{
      //the current song is not visible, play the first song in the new view
      id=getMediaID($('#libraryTable'+window.playingTableIndex+' tbody tr:first').attr('class').split(' '));
    }
  }	
  if($('#libraryTable'+window.playingTableIndex+' tbody tr.'+id).length>0){
    //make sure ID is actually in the current table and hasn't been filtered out
    loadContent(id);
  }
  else{
    stopPlaylist();
    return;
  }
}

function resizeColumns(){
  var table;
  if ($('.menuLinkDiv.selected').hasClass('library')){
    table=window.tables[$('.menuLinkDiv.selected').attr('data-libid')];
    if(table){
      table.fnAdjustColumnSizing();
    }
  }
}

function getMediaID(classes){
  //this looks inefficient, but the ID should always be the first class,
  //this is just an extra precaution, I swear!
  for(i=0; i<classes.length; i++){
    if(classes[i].match(/^[0-9]+$/)){
      return classes[i];
    }
  }
  return -1;
}



function loadContent(id){
  $('.mediaPlayer').remove();
  var contentType = "";
  if($('#libraryTable'+window.playingTableIndex+' tbody tr.'+id).hasClass('audio')){
    contentType = 'audio';
  }
  else{
    contentType = 'video';
  }  
  var newdiv = "";
  if (contentType==="video"){
    newdiv='<video class="mediaPlayer video" width="100%" height="100%"><source src="http://demo.airtorrent.tk:8000/playlists/library/'+id+'.m3u8"></video>'
    $('#videoDiv').append(newdiv);
    $("#controlsDiv").addClass('video');
    $('#videoDiv').show();
    var title=$('#libraryTable'+window.playingTableIndex+' tbody tr.'+id+' td.mediaTitleCell div').html();
    $('.progressTimelineTitle').html('<img class="progressTimelineIconAudio" src="static/images/mini-icon-audio.png"><img class="progressTimelineIconVideo" src="static/images/mini-icon-video.png">'+title);
    $('.progressTimelineArtist').html('');
    $('.progressTimelineAlbum').html('');
  }
  else{
    newdiv='<audio class="mediaPlayer audio" width="0%" height="0%"><source src="http://demo.airtorrent.tk:8000/playlists/library/'+id+'.m3u8"></audio>'
    $('#audioDiv').append(newdiv);
    $("#controlsDiv").removeClass('video');
    //set up player to have proper info
    var title=$('#libraryTable'+window.playingTableIndex+' tbody tr.'+id+' td.mediaTitleCell div').html();
    var artist=$('#libraryTable'+window.playingTableIndex+' tbody tr.'+id+' td.mediaArtistCell div').html();
    var album=$('#libraryTable'+window.playingTableIndex+' tbody tr.'+id+' td.mediaAlbumCell div').html();
    $('.progressTimelineTitle').html('<img class="progressTimelineIconAudio" src="static/images/mini-icon-audio.png"><img class="progressTimelineIconVideo" src="static/images/mini-icon-video.png">'+title);
    if(artist!=" "){
      $('.progressTimelineArtist').html(' - '+artist);
    }
    else{
      $('.progressTimelineArtist').html('');
    }
    if(album!=" "){
      $('.progressTimelineAlbum').html(' - '+album);
    }
    else{
      $('.progressTimelineAlbum').html('');
    }
  }
  $('.mediaPlayer').bind('play', function(){
    $(".playBtnImgDiv").addClass('pause');
    $(".playBtnImgDiv").removeClass('play');
  });
  $('.mediaPlayer').bind('pause', function(){
    $(".playBtnImgDiv").removeClass('pause');
    $(".playBtnImgDiv").addClass('play');
  });
  $('.mediaPlayer').bind('timeupdate', function(){
    //seek bar update
    var val = (this.currentTime/this.duration) * ($('.playbackTrack').outerWidth() - 18);
    $('.playbackCursor').css('left', val+'px');
    if(val>1){
      $('.playbackTrackLeftProgress').show();
    }
    $('.playbackTrackCenterProgress').css('right', $('.playbackTrack').outerWidth() - val - 9);
    $('.progressTimelineTimePlayed').html(secondstominutes(parseInt(this.currentTime)));
    $('.progressTimelineTimeLeft').html('-'+secondstominutes(parseInt(this.duration) - parseInt(this.currentTime)));
  });
  $('.mediaPlayer').bind('ended', function(){
    playNext();
  });
  window.playingID = id;
  $('#libraryTable'+window.playingTableIndex+' tbody tr.playing').addClass('played');
  $('#libraryTable'+window.playingTableIndex+' tbody tr.playing img').remove();
  $('#libraryTable'+window.playingTableIndex+' tbody tr.playing').removeClass('playing');
  $('#libraryTable'+window.playingTableIndex+' tbody tr.'+id).addClass('playing');
  $('#libraryTable'+window.playingTableIndex+' tbody tr.playing td:first').append('<img src="static/images/status-icon-playing.png">');
  $('.mediaPlayer').get(0).volume = (parseInt($('.volumeKnobDiv').css('left')))/93;
  $('.playbackTrack').show()
  $('.playbackTrackCenterProgress').css('right', $('.playbackTrack').outerWidth() - $('.playbackTrackCenterProgress').css('left'));
  $('.playbackTrackLeftProgress').hide()
  $('.playbackTrackRightProgress').hide()
  $('.playbackCursor').css('left', 0+'px');
  $('.playbackCursor').show()
  $('.progressTimelineHeader').show();
  $('.progressTimelineTimeLeft').show();
  $('.progressTimelineTimePlayed').show();
  var player = $('.mediaPlayer').get(0);
  player.play();
}




function secondstominutes(secs)
{
   var mins = Math.floor(secs / 60);
   secs = secs % 60;

   return (mins < 10 ? "" + mins : mins) 
          + ":"
          + (secs < 10 ? "0" + secs : secs);
}

jQuery.fn.random = function() {
    var randomIndex = Math.floor(Math.random() * this.length);  
    return jQuery(this[randomIndex]);
};


$(document).ready(function(){     
  window.playlistHistory = new Array();
  window.tables = new Array();
  window.playingTableIndex = -1;
  window.currentPlaylistIndex = -1;
  window.timer;
  window.isFadingIn = false;           //used for some book-keeping with the controls div
  window.isShuffle = false;
  window.isLoop = true;
  window.isLoopOnce = false;
  window.loopCount = 0;
  window.playngID = -1;
  window.selectedID = -1;
  $('#videoDiv').hide();
  updateAJAX('contentDiv', 'libraryDiv?libType=video&libId=0', '0');

  
  $("tr.video").live('dblclick',function(){
    stopPlaylist();
    startNewPlaylist();
  });
  
  $("tr.audio").live('dblclick',function(){
    stopPlaylist();
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
  $(".playBtnImg.enabled.play").live('mousedown', function(){
    $(this).attr('src', 'static/images/play_active.png');
  });
  
  
  //HEY GO HERE
  $(".playBtnImg.enabled.play").live('mouseup', function(){
    if($('#libraryTable'+window.playingTableIndex+' tbody tr.playing').length > 0){
      var player = $('.mediaPlayer').get(0);
      player.play();
    }
    else{
      stopPlaylist();
      startNewPlaylist();
    }
  });
  
  $(".playBtnImg.enabled.pause").live('mousedown', function(){
    $(this).attr('src', 'static/images/pause_active.png');
  });
  
  $(".playBtnImg.enabled.pause").live('mouseup', function(){
    var player = $('.mediaPlayer').get(0);
    player.pause();
  });

  $('.skipFwdBtnImg.enabled').live('mousedown', function(){
    $(this).attr('src', 'static/images/skip_forward_active.png');
  });
  $('.skipFwdBtnImg.enabled').live('mouseup', function(){
    $(this).attr('src', 'static/images/skip_forward.png');
    playNext();
  });
  
  $('.skipPrvBtnImg.enabled').live('mousedown', function(){
    $(this).attr('src', 'static/images/skip_previous_active.png');
  });
  $('.skipPrvBtnImg.enabled').live('mouseup', function(){
    $(this).attr('src', 'static/images/skip_previous.png');
  });
  
  $('.stopBtnImg.enabled').live('mousedown', function(){
    $(this).attr('src', 'static/images/stop_active.png');
  });
  $('.stopBtnImg.enabled').live('mouseup', function(){
    $(this).attr('src', 'static/images/stop.png');
    stopPlaylist();
  });
  
  
//TORRENT GUI  
  $('#upload').live('click', function(e){
    $('#loadWheelImg').removeClass('hidden');
    var file=this.form[1].files[0];
    if(file){
      if(file.type != "application/x-bittorrent"){
        alert('Please choose a torrent file');
        e.preventDefault();
        $('#loadWheelImg').addClass('hidden');
      }
    }
    else{
      alert('Please choose a torrent file');
      e.preventDefault();
      $('#loadWheelImg').addClass('hidden');
    }
  });

   
        

//RESIZING 
  $(window).resize(function() {
    if($(".containerDiv").length > 0){
      $('.dataTables_scroll').css("height", (($('#contentDiv').outerHeight(true))-($('.dataTables_filter').outerHeight(true))));
      $('.dataTables_scrollBody').css("height", (($('#contentDiv').outerHeight(true))-($('.dataTables_filter').outerHeight(true))-(29)));
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
  if (arguments.length==2){
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
    if (xmlhttp.readyState==4 && xmlhttp.status==200){
      if(div=='contentDiv'){
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
            var temp='tbody tr.playing:not(.'+window.playingID+')'
            $(temp).each(function(index) {
                $(this).removeClass('playing');
                $(this).remove('td:first img');
                $(this).addClass('played');
            });
  
              
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
  var myIFrame = document.getElementById('uploadIframe');
  var content = myIFrame.contentWindow.document.body.innerHTML;
  $('#loadWheelImg').addClass('hidden');
  if(content!=""){
      alert(content);
  }

}



function startNewPlaylist(){
  $('.playBtnImg').addClass('enabled');
  $('.playBtnImg').attr('src', 'static/images/play.png');
  $('.skipPrvBtnImg').addClass('enabled');
  $('.skipPrvBtnImg').attr('src', 'static/images/skip_previous.png');
  $('.skipFwdBtnImg').addClass('enabled');
  $('.skipFwdBtnImg').attr('src', 'static/images/skip_forward.png');
  $('.stopBtnImg').addClass('enabled');
  $('.stopBtnImg').attr('src', 'static/images/stop.png');
  window.playingTableIndex = $('.menuLinkDiv.selected').attr('data-libid');
  //parse the row id from the class
  id=getMediaID($('#libraryTable'+window.playingTableIndex+' tbody tr.selected:first').attr('class').split(' '));
  window.currentPlaylistIndex = window.playlistHistory.length;  //0
  window.playlistHistory[window.playlistHistory.length] = id;  
  loadContent(id); 
}

function stopPlaylist(){
  $('#libraryTable'+window.playingTableIndex+' tbody tr').removeClass('played');
  $('#libraryTable'+window.playingTableIndex+' tbody tr.playing img').remove();
  $('#libraryTable'+window.playingTableIndex+' tbody tr').removeClass('playing');
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
  $('.playBtnImg').attr('src', 'static/images/play.png');
  $('.skipPrvBtnImg').removeClass('enabled');
  $('.skipPrvBtnImg').attr('src', 'static/images/skip_previous_disabled.png');
  $('.skipFwdBtnImg').removeClass('enabled');
  $('.skipFwdBtnImg').attr('src', 'static/images/skip_forward_disabled.png');
  $('.stopBtnImg').removeClass('enabled');
  $('.stopBtnImg').attr('src', 'static/images/stop_disabled.png');
}

function playNext(){
  var id;
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
          window.currentPlaylistIndex=0;
          id = window.playlistHistory[window.currentPlaylistIndex];
        }
        else if (window.isLoopOnce){
          window.isLoopOnce = false;
          window.currentPlaylistIndex=0;
          id = window.playlistHistory[window.currentPlaylistIndex];
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
        }
        else if (window.isLoopOnce){
          window.isLoopOnce = false;
          id=getMediaID($('#libraryTable'+window.playingTableIndex+' tbody tr:first').attr('class').split(' '));
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
  if($('#libraryTable'+window.playingTableIndex+' tbody tr.audio.'+id).length>0){
    loadContent(id, 'audio');
  }
  else{
    loadContent(id, 'video');
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
  if (contentType=="video"){
    newdiv='<video class="mediaPlayer video" width="100%" height="100%"><source src="static/test.webm"></video>'
    $('#videoDiv').append(newdiv);
    $("#controlsDiv").addClass('video');
    $('#videoDiv').show();
  }
  else{
    newdiv='<audio class="mediaPlayer audio" width="0%" height="0%"><source src="static/Kalimba.mp3"></audio>'
    $('#audioDiv').append(newdiv);
    $("#controlsDiv").removeClass('video');
  }
  $('.mediaPlayer').bind('play', function(){
    $(".playBtnImg").attr('src', 'static/images/pause.png');
    $(".playBtnImg").addClass('pause');
    $(".playBtnImg").removeClass('play');
  });
  $('.mediaPlayer').bind('pause', function(){
    $(".playBtnImg").attr('src', 'static/images/play.png');
    $(".playBtnImg").removeClass('pause');
    $(".playBtnImg").addClass('play');
  });
  $('.mediaPlayer').bind('ended', function(){
    playNext();
  });
  $('#libraryTable'+window.playingTableIndex+' tbody tr.playing').addClass('played');
  $('#libraryTable'+window.playingTableIndex+' tbody tr.playing img').remove();
  $('#libraryTable'+window.playingTableIndex+' tbody tr.playing').removeClass('playing');
  $('#libraryTable'+window.playingTableIndex+' tbody tr.'+id).addClass('playing');
  window.playingID = id;
  $('#libraryTable'+window.playingTableIndex+' tbody tr.playing td:first').append('<img src="static/images/status-icon-playing.png">');
  var player = $('.mediaPlayer').get(0);
  player.play();
}


jQuery.fn.random = function() {
    var randomIndex = Math.floor(Math.random() * this.length);  
    return jQuery(this[randomIndex]);
};


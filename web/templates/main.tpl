<!DOCTYPE html>
<html>
<head>
<link href="static/css/stylesheet.css" type="text/css" rel="stylesheet" />  
<link href="static/css/table.css" type="text/css" rel="stylesheet" />
<link href="static/css/upload.css" type="text/css" rel="stylesheet" />
<script type="text/javascript" src="static/scripts/enhance.js"></script>        
<script type="text/javascript" src="static/scripts/complete.min.js"></script>
<script type="text/javascript" language="javascript" src="static/scripts/jquery.js"></script>
<script type="text/javascript" language="javascript" src="static/scripts/jquery.event.drag.js"></script>
<script type="text/javascript" language="javascript" src="static/scripts/jquery.dataTables.js"></script>
<script type="text/javascript" language="javascript" src="static/scripts/ColReorder.js"></script>
<script type="text/javascript" language="javascript" src="static/scripts/AirTorrentWebUI.js"></script>
<script type="text/javascript" src="static/scripts/jQuery.fileinput.js"></script>
</head>
<body>
<div id="menuDiv">
  <div data-ajaxlink="'${audioLink}'" class="menuLinkDiv library notloaded" id="menuLinkDivAudio">
    <div class="menuIcon" id="iconAudioDiv"></div>
    <div class="menuTextLink">Audio</div></div>
    <div data-ajaxlink="${videoLink}" data-libid="0" class="menuLinkDiv library selected loaded" id="menuLinkDivVideo">
      <div class="menuIcon" id="iconVideoDiv"></div>
      <div class="menuTextLink">Video</div></div>
    <div data-ajaxlink="'${torrentLink}'" class="menuLinkDiv torrent notloaded" id="menuLinkDivTorrent">
      <div class="menuIcon" id="iconTorrentDiv"></div>
      <div class="menuTextLink">Torrent</div></div>
    </div>
</div>
<div id="contentDiv"></div>
<div id="controlsDiv">
  <div id=controlButtons>
    <div class="skipPrvBtnImgDiv"></div>
    <div class="stopBtnImgDiv"></div>
    <div class="playBtnImgDiv play enabled"></div>
    <div class="skipFwdBtnImgDiv"></div></div>
    <div class="progressTimeline">
      <div class="progressTimelineHeader">
        <div class="progressTimelineTitle">
          <img class="progressTimelineIconAudio" src="static/images/mini-icon-audio.png">
          <img class="progressTimelineIconVideo" src="static/images/mini-icon-video.png">
        </div>
        <div class="progressTimelineAlbum"></div>
        <div class="progressTimelineArtist"></div>
      </div>
      <div class="progressTimelineLeftDiv"></div>
      <div class="progressTimelineCenterDiv"></div>
      <div class="progressTimelineRightDiv"></div>
      <div class="progressTimelineTimePlayed">0:00</div>
      <div class="progressTimelineTimeLeft">-0:00</div>
      <div class="playbackTrack">
        <div class="playbackCursor"></div>
        <div class="playbackTrackLeft"></div>
        <div class="playbackTrackCenter"></div>
        <div class="playbackTrackRight"></div>
        <div class="playbackTrackLeftProgress"></div>
        <div class="playbackTrackCenterProgress"></div>
        <div class="playbackTrackRightProgress"></div>
      </div>
    </div>
    <div class="volumeDiv">
      <div class="volumeIconDiv"></div>
      <div class="volumeTrackDiv">
        <div class="volumeKnobDiv"></div>
      </div>
    </div>
    <div class="shuffleLoopDiv">
      <div class="shuffleBtnDiv off"></div>
      <div class="loopBtnDiv off"></div>
    </div>
  </div>

  <div id="mediaDiv">
    <div id="videoDiv"></div>
  <div id="audioDiv">
    <audio class="mediaPlayer audio" width="0%" height="0%">
      <source src="static/Kalimba.mp3">
    </audio>
  </div>
</div>
</body>
</html>

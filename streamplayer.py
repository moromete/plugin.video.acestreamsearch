import xbmc, xbmcgui

#import glob
from common import addon_log, addon
#from default import DISABLE_SCHEDULE, load_active_event

from settings import SETTINGS
from resources.acestreamsearch.channels import Channels
from resources.acestreamsearch.channel import Channel

# if SETTINGS.DISABLE_SCHEDULE != 'true':
#   from schedule import epg

class streamplayer(xbmc.Player):
  def __init__( self , *args, **kwargs):
    self.callback = None

    self.stream_online = None
    self.player_status = None
    # addon_log('INIT PLAYER')
    self.url = None

  def play(self, url, listitem):
    self.player_status = 'play'
    self.url = url
    super(streamplayer, self).play(url, listitem)
    self.keep_allive()

  def onPlayBackStarted(self):
    addon_log('-----------------------> START PLAY')

  def onPlayBackEnded(self):
    addon_log('----------------------->END PLAY')
    self.player_status = 'end'

    try:
      if(self.callback != None):
        self.callback()
    except: pass

    if(self.stream_online != True) :
      self.isOffline()

  def onPlayBackStopped(self):
    addon_log('----------------------->STOP PLAY')
    self.player_status = 'stop'
    
    # addon_log(self.callback)
    try:
      if(self.callback != None):
        self.callback()
    except: pass
    
  def keep_allive(self):
    xbmc.sleep(1000)

    #KEEP SCRIPT ALLIVE
    while (self.player_status=='play'):
      addon_log('ALLIVE')
      xbmc.sleep(500)
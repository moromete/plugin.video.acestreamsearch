import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import sys, os, os.path
import urllib

import time
from datetime import datetime, timedelta

from settings import SETTINGS
from common import addon_log, addon

# if SETTINGS.DISABLE_SCHEDULE != 'true':
#   #from schedule import grab_schedule, load_schedule
#   from schedule import epg

from streamplayer import streamplayer
from play_ace import acestream

from resources.acestreamsearch.channels import Channels
from resources.acestreamsearch.channel import Channel

addon_id = 'plugin.video.acestreamsearch'
settings = xbmcaddon.Addon(id=addon_id)
fileslist = xbmc.translatePath(settings.getAddonInfo('profile')).decode('utf-8')

def get_params():
  param=[]

  paramstring=sys.argv[2]

  if len(paramstring)>=2:
    params=sys.argv[2]
    cleanedparams=params.replace('?','')
    if (params[len(params)-1]=='/'):
      params=params[0:len(params)-2]
    pairsofparams=cleanedparams.split('&')
    param={}
    for i in range(len(pairsofparams)):
      splitparams={}
      splitparams=pairsofparams[i].split('=')
      if (len(splitparams))==2:
        param[splitparams[0]]=splitparams[1]
  return param

def addDir(name, cat_id, url, mode):
  name = name.encode('utf8')
  contextMenuItems = []

  plugin=sys.argv[0]

  u=plugin+"?mode=4"
  contextMenuItems.append(( 'Refresh Channel List', "XBMC.RunPlugin("+u+")", ))

  u = plugin+"?"+"mode="+str(mode) + \
      "&name="+urllib.quote_plus(name) + \
      "&cat_id="+cat_id + "&url="+urllib.quote_plus(url)
  ok = True

  liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png",thumbnailImage="")
  liz.addContextMenuItems(contextMenuItems)
  liz.setInfo( type="Video", infoLabels={ "Title": name })
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
  return ok

def addLink(name, url, id=None):
  name = name.encode('utf8')
  
  contextMenuItems = []

  if(id == None):
    u=sys.argv[0]+"?mode=4"
    contextMenuItems.append(( addon.getLocalizedString(30052), "XBMC.RunPlugin("+u+")", )) #Add to main list
  
  # u=sys.argv[0]+"?mode=7&ch_id=" + str(ch_id)
  # contextMenuItems.append(( addon.getLocalizedString(30407), "XBMC.RunPlugin("+u+")", )) #Delete Channel

  liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=None)
  liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": ''} )

  u = sys.argv[0] + "?mode=2&url=%s&name=%s" % (urllib.quote_plus(url), urllib.quote_plus(name))
  
  # liz.addContextMenuItems(contextMenuItems)
  addon_log(name)
  addon_log(u)
  addon_log(sys.argv[1])

  return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
  

def CHANNEL_LIST():
  
  #add search link
  liz=xbmcgui.ListItem('[B][COLOR green]'+addon.getLocalizedString(30402)+'[/COLOR][/B]', iconImage="DefaultFolder.png", thumbnailImage=None)
  liz.setInfo( type="Video", infoLabels={ "Title": None } )
  liz.setProperty('IsPlayable', 'false')
  url = sys.argv[0] + "?mode=1"
  xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=liz, isFolder=True)


  # loadUnverified = False 
  # if((mode!=None) and (int(mode)==101)):
  #   loadUnverified = True

  # channels = Channels(catId = cat_id)
  # arrChannels = channels.loadChannels(loadUnverified)
  # for ch in arrChannels:
  #   if (((SETTINGS.SHOW_OFFLINE_CH=='true') and (int(ch.status)==ch.STATUS_OFFLINE)) or (int(ch.status)!=ch.STATUS_OFFLINE)): #if we show or not offline channels based on settings
  #     if (ch.my == 1): 
  #       name_formatted = "[I]%s[/I]" % ch.name
  #     else:
  #       name_formatted = "[B]%s[/B]" % ch.name
  #     name_formatted += " [[COLOR yellow]%s[/COLOR]]" % ch.protocol
       
  #     if int(ch.status)==ch.STATUS_OFFLINE: 
  #       name_formatted += " [COLOR red]%s[/COLOR]" % addon.getLocalizedString(30063)  #Offline
      
  #     addLink(ch.id, name_formatted, ch.name, ch.address.strip(), ch.protocol.strip(),
  #             ch.id_cat, 2, '', "", len(arrChannels))

def LIST_SEARCH(arrChannels):
  # addon_log(arrChannels)
  for ch in arrChannels:
    addLink(name = ch['name'], url=ch['url'])

def STREAM(name, url, ch_id):
  listitem = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage="DefaultVideo.png")
  listitem.setInfo('video', {'Title': name})

  player = streamplayer(ch_id=None)
    
  if(SETTINGS.ACE_ENGINE_TYPE == 1): #use plexus
    try:
      addon_log('plexus')
      xbmc.executebuiltin('XBMC.RunPlugin(plugin://program.plexus/?mode=1&url='+url+'&name='+name+'&iconimage='+iconimage+')')
    except Exception as inst:
      addon_log(inst)
      xbmc.executebuiltin("Notification(%s,%s,%i)" % (addon.getLocalizedString(30303), "", 10000))
  elif(SETTINGS.ACE_ENGINE_TYPE == 0): #use external
    #play with acestream engine started on another machine or on the localhost
    ace = acestream(player=player, url=url, listitem=listitem)
    ace.engine_connect()

#######################################################################################################################
#######################################################################################################################
#######################################################################################################################

addon_log('------------- START -------------')

params=get_params()
try:
  mode=int(params["mode"])
except:
  mode=None

addon_log('MODE = ' + str(mode))
if (mode==None):  #list channels
  CHANNEL_LIST()
elif mode==1:  #search
  channels = Channels() 
  arrChannels = channels.search()
  LIST_SEARCH(arrChannels = arrChannels)
  pass
elif mode==2:  #play stream
  if xbmc.Player().isPlaying():
    xbmc.Player().stop()
  STREAM(name=params["name"], url=urllib.unquote_plus(params["url"]), ch_id=None)
elif mode==3:  #add to main list
  pass
elif (mode==7): #delete stream
  channels = Channels() 
  channels.deleteStream(ch_id)
  
addon_log('------------- END ---------------')
xbmcplugin.endOfDirectory(int(sys.argv[1]))
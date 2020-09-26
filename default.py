import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import sys, os, os.path
import urllib

from settings import SETTINGS
from common import addon_log, addon

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

def addLink(name, url, id=None):
  if(name != None):
    name = name.encode('utf8')
    contextMenuItems = []

    if(id == None):
      u=sys.argv[0]+"?mode=3&url=%s&name=%s" % (urllib.quote_plus(url), urllib.quote_plus(name))
      contextMenuItems.append(( addon.getLocalizedString(30052), "XBMC.RunPlugin("+u+")", )) #Add to main list
    else:
      u=sys.argv[0]+"?mode=5&id=" + str(id)
      contextMenuItems.append(( addon.getLocalizedString(30408), "XBMC.RunPlugin("+u+")", )) #Update Channel
      u=sys.argv[0]+"?mode=6"
      contextMenuItems.append(( addon.getLocalizedString(30411), "XBMC.RunPlugin("+u+")", )) #Update all channels
      u=sys.argv[0]+"?mode=4&id=" + str(id)
      contextMenuItems.append(( addon.getLocalizedString(30407), "XBMC.RunPlugin("+u+")", )) #Delete Channel

    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=None)
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": ''} )

    u = sys.argv[0] + "?mode=2&url=%s&name=%s" % (urllib.quote_plus(url), urllib.quote_plus(name))
    
    liz.addContextMenuItems(contextMenuItems)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
  

def CHANNEL_LIST():
  #add search link
  if(addon.getSetting('search') == 'true'):
    liz=xbmcgui.ListItem('[B][COLOR green]'+addon.getLocalizedString(30402)+'[/COLOR][/B]', iconImage="DefaultFolder.png", thumbnailImage=None)
    liz.setInfo( type="Video", infoLabels={ "Title": None } )
    liz.setProperty('IsPlayable', 'false')
    url = sys.argv[0] + "?mode=1"
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=liz, isFolder=True)

  channels = Channels()
  arrChannels = channels.loadChannels()
  for ch in arrChannels:
    # if ch.status and int(ch.status)==ch.STATUS_OFFLINE: 
    #   name_formatted += " [COLOR red]%s[/COLOR]" % addon.getLocalizedString(30063)  #Offline
      
    addLink(id = ch.id, name = ch.name, url = ch.address)

def LIST_SEARCH(arrChannels):
  addon_log(arrChannels)
  if(arrChannels):
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
  channels = Channels()
  channels.migrateDb()
  CHANNEL_LIST()
elif mode==1:  #search
  channels = Channels() 
  arrChannels = channels.search()
  LIST_SEARCH(arrChannels = arrChannels)
  pass
elif mode==2:  #play stream
  if xbmc.Player().isPlaying():
    xbmc.Player().stop()
  STREAM(name=urllib.unquote_plus(params["name"]), url=urllib.unquote_plus(params["url"]), ch_id=None)
elif mode==3:  #add to main list
  channels = Channels() 
  if(channels.add(name=urllib.unquote_plus(params["name"]), url=urllib.unquote_plus(params["url"]))):
    xbmc.executebuiltin("Notification(%s,%s,%i)" % (addon.getLocalizedString(30405), "", 1))
  pass
elif (mode==4): #delete stream
  channels = Channels() 
  channels.deleteStream(params["id"])
elif (mode==5): #update stream
  channels = Channels() 
  if(channels.updateStream(params["id"])):
    xbmc.executebuiltin("Notification(%s,%s,%i)" % (addon.getLocalizedString(30409), "", 1))
  xbmc.executebuiltin("Container.Refresh")
elif (mode==6): #update all streams
  channels = Channels() 
  if(channels.updateAllStreams()):
    xbmc.executebuiltin("Notification(%s,%s,%i)" % (addon.getLocalizedString(30409), "", 1))
  xbmc.executebuiltin("Container.Refresh")
  
addon_log('------------- END ---------------')
xbmcplugin.endOfDirectory(int(sys.argv[1]))
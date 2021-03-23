import xbmc, xbmcaddon

addon = xbmcaddon.Addon('plugin.video.acestreamsearch')

def addon_log(string):
  DEBUG = addon.getSetting('debug')
  ADDON_VERSION = addon.getAddonInfo('version')
  if DEBUG == 'true':
    # if isinstance(string, unicode):
    #   string = string.encode('utf-8')
    xbmc.log("[plugin.video.acestreamsearch-%s]: %s" %(ADDON_VERSION, string))

from contextlib import contextmanager
@contextmanager
def busy_dialog():
  xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
  try:
    yield
  finally:
    xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
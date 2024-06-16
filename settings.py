import xbmcvfs
import os
from common import addon

class SETTINGS(object):

  ADDON_PATH = addon.getAddonInfo('path')
  PROFILE = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
   
  CHANNELS_DB = os.path.join(PROFILE,'channels.sqlite')
  
  ########################################################## acestream
  #PRODUCT_KEY='kjYX790gTytRaXV04IvC-xZH3A18sj5b1Tf3I-J5XVS1xsj-j0797KwxxLpBl26HPvWMm' #free
  PRODUCT_KEY='n51LvQoTlJzNGaFxseRK-uvnvX-sD4Vm5Axwmc4UcoD-jruxmKsuJaH0eVgE' #aceproxy
  ACE_HOST = addon.getSetting('ace_host')
  ACE_PORT = int(addon.getSetting('ace_port'))
  ACE_ENGINE_TYPE = int(addon.getSetting('ace_engine_type'))
##########################################################
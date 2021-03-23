import xbmc, xbmcgui

import sys
import sqlite3
import os

from settings import SETTINGS
from common import addon, addon_log
from resources.acestreamsearch.channel import Channel
from resources.acestreamsearch.scrapper import Scrapper

class Channels():
  # def __init__( self , **kwargs):
  #   pass

  def migrateDb(self):
    addon_log("""Run database migrations.""")

    if(not os.path.isdir(SETTINGS.PROFILE)):
      os.mkdir(SETTINGS.PROFILE)

    def get_script_version(path):
        return int(path.split('_')[0])

    db = sqlite3.connect(SETTINGS.CHANNELS_DB)
    current_version = db.cursor().execute('pragma user_version').fetchone()[0]

    addon_log(current_version)

    migrations_path = os.path.join(SETTINGS.ADDON_PATH, 'resources/acestreamsearch/migrations/')
    migration_files = list(os.listdir(migrations_path))
    for migration in sorted(migration_files):
        scriptFile = "{0}".format(migration)
        migration_version = get_script_version(scriptFile)
        scriptPath = os.path.join(SETTINGS.ADDON_PATH, 'resources/acestreamsearch/migrations/', scriptFile)

        if migration_version > current_version:
            addon_log("applying migration {0}".format(migration_version))
            with open(scriptPath, mode='r') as f:
                 db.cursor().executescript(f.read())
                 addon_log("database now at version {0}".format(migration_version))
        else:
            addon_log("migration {0} already applied".format(migration_version))

  def search(self):
    kb = xbmc.Keyboard('', addon.getLocalizedString(30403))

    #url
    kb.doModal()
    if (kb.isConfirmed()):
      name = kb.getText()
      name = name.title()
      name = name
      if name == '' : sys.exit(0)
      else:
        scrapper = Scrapper()
        return scrapper.execute(name=name)
  
  def add(self, name, url):
    ch = Channel(name = name,
                 address = url)
    if(ch.checkAddrExist()):
      return ch.update(name = name)
    else: 
      if(ch.checkNameExist()):
        return ch.update(address = url)
      else :
        return ch.insert()
          
  def deleteStream(self, chId):
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('', addon.getLocalizedString(30410))

    if(ret):
      ch = Channel()
      ch.findOne(chId)
      ch.delete()
      xbmc.executebuiltin("Container.Refresh")

  def loadChannels(self):
    db_connection=sqlite3.connect(SETTINGS.CHANNELS_DB)
    db_cursor=db_connection.cursor()

    sql = 'SELECT id, name, status, address \
           FROM channels \
           ORDER BY name'
    
    db_cursor.execute( sql )
    rec=db_cursor.fetchall()
    
    arrChannels = []
    if len(rec)>0:
      for id, name, status, address in rec:
        ch = Channel(id=id, 
                     name=name,
                     status=status,
                     address=address)
        arrChannels.append(ch)
    db_connection.close()
    return arrChannels

  def markStream(self, chId, status):
    ch = Channel()
    ch.findOne(chId)
    ch.setStatus(status)
    # xbmc.executebuiltin("Container.Refresh")

  def updateStream(self, id):
    ch = Channel()
    ch.findOne(id)

    scrapper = Scrapper()
    arrChannels = scrapper.execute(name=ch.name)

    if(arrChannels):
      for chFound in arrChannels:
        if(ch.name == chFound['name']):
          return ch.update(address = chFound['url'])

  def updateAllStreams(self):
    pDialog = xbmcgui.DialogProgress()
    pDialog.create(addon.getLocalizedString(30412))

    arrChannels = self.loadChannels()
    
    i=1
    for ch in arrChannels:
      self.updateStream(id = ch.id)
      percent = round(i * 100 / len(arrChannels))
      pDialog.update(percent, ch.name)
      i = i + 1

    

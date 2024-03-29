import xbmc, xbmcgui

import socket
import re
import hashlib
import random
import json
import urllib
import time
# import select

import glob
from common import addon_log, addon, busy_dialog
from settings import SETTINGS
from resources.acestreamsearch.channels import Channels
from resources.acestreamsearch.channel import Channel

class acestream():
  buffer_size = 1024
  start_time = None
  timeout = 10

  def __init__( self , *args, **kwargs):
    self.player=kwargs.get('player')
    url=kwargs.get('url')
    self.listitem=kwargs.get('listitem')

    self.player_started = None

    self.pid = url.replace('acestream://', '')
    self.pid = self.pid.replace('/', '')
    
    addon_log('INIT ACESTREAM')

  def read_lines(self, sock, recv_buffer=4096, delim='\n'):
    buffer = ''
    data = True
    while data:

      # ready = select.select([sock], [], [], self.timeout)
      # if ready[0]:
      #   data = sock.recv(recv_buffer)
      # else:
      #   addon_log('timeout')
      #   self.send("STOP")
      #   self.send("SHUTDOWN")
      #   # self.shutdown()
      #   # self.sock.close()
      #   xbmc.executebuiltin("Notification(%s,%s,%i)" % (addon.getLocalizedString(30057), "", 10000))
      #   return
      try: 
        data = sock.recv(recv_buffer)
      except Exception as inst:
        addon_log(inst)
        xbmc.executebuiltin("Notification(%s,%s,%i)" % (addon.getLocalizedString(30057), "", 10000))
        return
            
      buffer += data.decode()

      while buffer.find(delim) != -1:
        line, buffer = buffer.split('\n', 1)
        yield line
    return

  def engine_connect(self):
    with busy_dialog():
      try:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((SETTINGS.ACE_HOST, SETTINGS.ACE_PORT))
        self.sock.settimeout(self.timeout)
      except Exception as inst:
        addon_log(inst)
        DEBUG = addon.getSetting('debug')
        if DEBUG == 'true': xbmc.executebuiltin("Notification(%s,%s,%i)" % (str(type(inst)), str(inst), 5))
        return False

      cmd = "HELLOBG version=3"
      addon_log(cmd)
      self.send(cmd)
      player_url = self.ace_read()

    if(player_url != None):
      addon_log (player_url)
      self.player.callback = self.shutdown
      self.listitem.setInfo('video', {'Title': self.filename})
      self.player.play(player_url, self.listitem)
      self.player_started = True

  def auth(self, data):
    p = re.compile('\skey=(\w+)\s')
    m = p.search(data)
    REQUEST_KEY=m.group(1)
    key = REQUEST_KEY + SETTINGS.PRODUCT_KEY
    key = key.encode()
    signature = hashlib.sha1(key).hexdigest()
    response_key = SETTINGS.PRODUCT_KEY.split ("-") [0] + "-" + signature

    cmd = "READY key="+response_key
    addon_log(cmd)
    self.send(cmd)

  def ch_open(self):
    request_id = random.randint(1, 100)
    cmd = 'LOADASYNC ' + str(request_id) + ' PID ' + self.pid
    self.send(cmd)
    addon_log(cmd)
    return request_id

  def ch_start(self):
    self.send('START PID ' + self.pid + " 0")
    self.start_time = time.time()

  def shutdown(self):
    addon_log("SHUTDOWN")
    self.send("SHUTDOWN")

  def send(self, cmd):
    try:
      cmd = cmd + "\r\n"
      cmd = cmd.encode()  
      self.sock.send(cmd)
    except Exception as inst:
      addon_log(inst)

  def ace_read(self):
    for line in self.read_lines(self.sock):

      # if ((self.start_time!=None) and ((time.time() - self.start_time) > self.timeout)):
      #   self.shutdown()
      #   xbmc.executebuiltin("Notification(%s,%s,%i)" % (addon.getLocalizedString(30057), "", 10000))

      addon_log(line)
      if line.startswith("HELLOTS"):
        self.auth(line)
      elif line.startswith("AUTH"):
        self.request_id = self.ch_open()
      elif line.startswith("LOADRESP"):
        response = line.split()[2:]
        response = ' '.join(response)
        response = json.loads(response)

        if response.get('status') == 100:
          addon_log("LOADASYNC returned error with message: %s" % response.get('message'))
          xbmc.executebuiltin("Notification(%s,%s,%i)" % (response.get('message'), "", 10000))
          return False

        # infohash = response.get('infohash')
        #self.sock.send('GETADURL width = 1328 height = 474 infohash = ' + infohash + ' action = load'+"\r\n")
        #self.sock.send('GETADURL width = 1328 height = 474 infohash = ' + infohash + ' action = pause'+"\r\n")

        # self.filename = urllib.parse.unquote(response.get('files')[0][0].encode('ascii')).decode('utf-8')
        self.filename = urllib.parse.unquote(response.get('files')[0][0])
        addon_log(self.filename)
        self.ch_start()

      elif line.startswith("START"):
        self.start_time = None

        # try: xbmc.executebuiltin("Dialog.Close(all,true)")
        # except: pass

        try:
          player_url = line.split()[1]
          #return player_url

          # addon_log (player_url)
          # self.player.callback = self.shutdown
          # self.listitem.setInfo('video', {'Title': self.filename})
          # self.player.play(player_url, self.listitem)
          # self.player_started = True
        except IndexError as e:
          player_url = None

        #p = re.compile('(http://)[\w\W]+?(\:[0-9]+/)')
        #player_url = url
        #player_url = p.sub(r"\1" + self.ace_host + r"\2", url)
        #addon_log (player_url)
        #self.player.play(player_url, self.listitem)

        #self.sock.send("PAUSE"+"\r\n")
        #self.sock.send("RESUME"+"\r\n")
        #self.sock.send("STOP"+"\r\n")
        #self.sock.send("SHUTDOWN"+"\r\n")

      elif line.startswith("SHUTDOWN"):
        self.sock.close()
        break

      #IDLE
      elif line.startswith("STATE 0"):
        self.shutdown()

      #DOWNLOADING
      elif line.startswith("STATE 2"):
        return player_url
      
      #messages
      elif line.startswith("STATUS"):
        tmp = line.split(';')
        if(2 < len(tmp)):
          addon_log(tmp[2])
          # xbmc.executebuiltin("Notification(%s,%s,%i)" % (tmp[2], "", 10000))
            
      #INFO 1;Cannot find active peers
      elif line.startswith("INFO"):
        tmp = line.split(';')
        info_status = tmp[0].split()[1]
        if(info_status == '1'): #INFO 1;Cannot find active peers
          info_msg = tmp[1]
          self.shutdown()
          xbmc.executebuiltin("Notification(%s,%s,%i)" % (info_msg, "", 10000))

      elif line.startswith("EVENT"):
        #print line
        pass
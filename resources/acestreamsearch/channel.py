import sqlite3
import uuid

from settings import SETTINGS
from common import addon, addon_log

class Channel():
  STATUS_ONLINE   = 1
  STATUS_OFFLINE  = -1

  def __init__( self , *args, **kwargs):
    self.id = kwargs.get('id')
    self.name = kwargs.get('name')
    self.address = kwargs.get('address')
    self.status = kwargs.get('status')
    
    self.db_connection=sqlite3.connect(SETTINGS.CHANNELS_DB)
    self.db_cursor=self.db_connection.cursor()
 
  def findOne(self, id):
    sql = "SELECT name, address, status \
           FROM channels \
           where id = ?"
    self.db_cursor.execute( sql, (id, ) )
    rec=self.db_cursor.fetchone()
    if rec != None:
      self.id          = id
      self.name        = rec[0]
      self.address     = rec[1]
      self.status      = rec[2]
      return True
  
  def save(self):
    if(self.id):
      return self.update()
    else:
      if(self.checkAddrExist() == False):
        self.id  = str(uuid.uuid1())
        return self.insert()
      else:
        return False

  def checkAddrExist(self):
    sql = "SELECT id \
           FROM channels \
           where address = ?"
    self.db_cursor.execute( sql, (self.address, ) )
    rec=self.db_cursor.fetchone()
    if(rec != None):
      self.id = rec[0]
      return True
    else:
      return False
    
  def insert(self):
    sql = "INSERT INTO channels \
           (id, name, address, status) \
           VALUES(?, ?, ?, ?)"
    st = self.db_cursor.execute(sql, (self.id,
                                      self.name,
                                      self.address,
                                      self.status
                                     ))
    self.db_connection.commit()
    return st

  def update(self, **kwargs):
    sql = "UPDATE channels SET "
    values = []
    count = 1
    for key, value in kwargs.items():
      values.append(value)
      if(count > 1):
        sql += ", "
      sql += " %s = ? " % key
      count = count + 1
    sql += " WHERE id = ? "
    values.append(self.id)
    #addon_log(sql)
    #addon_log(values)
    st = self.db_cursor.execute(sql, values)
    self.db_connection.commit()
    return st

  def setStatus(self, status):
    self.status = status
    sql = "UPDATE channels \
           SET status = ? \
           WHERE id = ?"
    st = self.db_cursor.execute(sql, (self.status, self.id))
    self.db_connection.commit()
    return st
      
  def delete(self, softDelete=False):
    sql = "DELETE FROM channels \
          WHERE id = ?"
    st = self.db_cursor.execute(sql, (self.id, ))
    self.db_connection.commit()
    return st
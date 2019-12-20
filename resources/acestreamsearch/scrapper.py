import urllib2
from bs4 import BeautifulSoup

from common import addon_log

class Scrapper():
  url = 'https://acestreamsearch.net/en/'
  headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'identity',
    'Accept-Language': 'en-US,en;q=0.5', 
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'
  }

  def execute(self, name):
    url = self.url + "?q=" + name
    self.opener = urllib2.build_opener()
    request = urllib2.Request(url, None, self.headers)
    response = self.opener.open(request)
    html = response.read()
    
    soup = BeautifulSoup(html, "html.parser")
    items = soup.find_all('li', class_="list-group-item")

    channels = []
    for item in items:
      soup = BeautifulSoup(str(item.contents), "html.parser")
      #url
      chLink = soup.find('a', href=True)
      chUrl = chLink['href']
      #name
      chName = chLink.text
      chName = chName.strip()
      channels.append({'name': chName,
                       'url': chUrl})
    return channels
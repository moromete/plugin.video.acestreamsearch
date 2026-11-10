import json
import urllib.parse
import urllib.request

class Scrapper():
  url = 'https://search-ace.stream/search'
  headers = {
    'Accept': 'application/json',
    'Accept-Encoding': 'identity',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'
  }

  def execute(self, name):
    url = self.url + "?query=" + urllib.parse.quote_plus(name)
    self.opener = urllib.request.build_opener()
    request = urllib.request.Request(url, None, self.headers)
    response = self.opener.open(request, timeout=30)
    results = json.loads(response.read().decode('utf-8'))

    channels = []
    seen = set()
    for item in results:
      chName = item.get('name')
      contentId = item.get('content_id')
      if not (chName and contentId):
        continue
      key = (chName, contentId)
      if key in seen:
        continue
      seen.add(key)
      channels.append({'name': chName,
                       'url': 'acestream://' + contentId})

    return channels

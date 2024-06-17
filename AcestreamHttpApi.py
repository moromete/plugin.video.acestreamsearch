import urllib.request
import json

class AcestreamHttpApi():
    def __init__( self , *args, **kwargs):
        self.aceHost = kwargs.get('aceHost')
        self.acePort = kwargs.get('acePort')
        url=kwargs.get('url')
        self.contentId = url.replace('acestream://', '').replace('/', '')

    def getPlayInfo(self):
        response = urllib.request.urlopen("http://" + self.aceHost + ":" + str(self.acePort) +
            "/ace/manifest.m3u8?format=json&content_id=" + self.contentId)
        json_data = self.readJson(response)

        # self.infohash = json_data['response']['infohash']
        self.command_url = json_data['response']['command_url']
        self.playback_url = json_data['response']['playback_url']
        # self.playback_session_id = json_data['response']['playback_session_id']

        return json_data
    
    def stop(self):
        response = urllib.request.urlopen(self.command_url + "?method=stop")
        return self.readJson(response)

    def readJson(self, response):
        data = response.read()
        str_data = data.decode()
        return json.loads(str_data)

 
    
    
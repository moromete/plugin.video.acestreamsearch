from AcestreamHttpApi import AcestreamHttpApi
import unittest

class AcestreamHttpApiTest(unittest.TestCase):
    def testGetPlayInfo(self):
        acestreamHttpApi = AcestreamHttpApi(url='acestream://bba1905fcd1c4975aec544047bf8e4cd23ce3fe0', aceHost='127.0.0.1', acePort='6878')
        info = acestreamHttpApi.getPlayInfo()
        print(info)
        self.assertIsNotNone(info['response']['infohash'])
        self.assertIsNotNone(info['response']['command_url'])
        self.assertIsNotNone(info['response']['playback_url'])
        self.assertIsNotNone(info['response']['playback_session_id'])

    def testStop(self):
        acestreamHttpApi = AcestreamHttpApi(url='acestream://bba1905fcd1c4975aec544047bf8e4cd23ce3fe0', aceHost='127.0.0.1', acePort='6878')
        acestreamHttpApi.getPlayInfo()
        response = acestreamHttpApi.stop()
        self.assertEquals(response['response'], 'ok')
        print(response)
        

if __name__ == '__main__':
    unittest.main()

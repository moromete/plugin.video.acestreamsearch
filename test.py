from resources.acestreamsearch.scrapper import Scrapper

scrapper = Scrapper()
channels = scrapper.execute(name='hbo')
print(channels)
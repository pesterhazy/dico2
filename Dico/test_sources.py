import sources
from urllib2 import urlopen, HTTPError, Request
import pickle, re, unittest

class CachedPageStore:
    def __init__(self):
        self.loadDb()

    def loadDb(self):
        try:
            self.db = pickle.load(open("cache.db"))
        except IOError:
            self.db = {}

    def dumpDb(self):
        pickle.dump(self.db,open("cache.db","w"))

    def getPage(self,url):
        try:
            return self.db[url]
        except KeyError:
            headers = { 
                'User-Agent': 'Pywikipediabot/1.0',
                'Accept-Charset': 'utf-8'
            }
            content = urlopen(Request(url,None,headers)).read()
            self.db[url] = content
            self.dumpDb()
            return self.db[url]

class TestReferenceDotComSource(unittest.TestCase):
    def get(self,word):
        source = sources.ReferenceDotComSource()
        url = source.getUrl(word)
        data = pageStore.getPage(url)
        result = source.processPage(data)
        return result

    def test_tantrum(self):
        result = self.get("tantrum")
        assert re.search("violent demonstration", result)
        assert re.search("bad temper", result)
#        assert not re.search("<script", result)
        assert not re.search("New Millennium", result) # no information on dicts
        assert not re.search("britannica.com|cancerweb", result, re.IGNORECASE)
    
    def test_bead(self):
        result = self.get("bead")
        assert re.search("usually round object of glass", result)

    def test_noentry(self):
        self.assertRaises(sources.NoEntry,self.get,"john f. kenndy")

    def test_spelling(self):
        result = self.get("distrbute")
        assert re.search("distribute", result)

class TestUrbanDictionarySource(unittest.TestCase):
    def get(self,word):
        source = sources.UrbanDictionarySource()
        url = source.getUrl(word)
        data = pageStore.getPage(url)

        result = source.processPage(data)
        return result

    def test_boredom(self):
        result = self.get("boredom")
        assert re.search("excessive amounts of definitions", result)
        assert not re.search("Urban Dictionary is the dictionary you wrote", result)
        #assert not re.search("<script", result)

    def test_anvik(self):
        self.assertRaises(sources.NoEntry,self.get,"anvik")
    
class TestTFDIdiomsSource(unittest.TestCase):
    def get(self,word):
        source = sources.TFDIdiomsSource()
        url = source.getUrl(word)
        data = pageStore.getPage(url)

        result = source.processPage(data)
        return result

    def test_chip(self):
        result = self.get("chip on his shoulder")
        assert re.search("bad attitude", result)

    def test_intheline(self):
        result = self.get("in the line of duty")
        assert re.search("as a part of your job", result)

    def test_anvik(self):
        self.assertRaises(sources.NoEntry,self.get,"anvik")
    
class TestWikipediaSource(unittest.TestCase):
    def get(self,word):
        source = sources.WikipediaSource()
        url = source.getUrl(word)
        try:
            data = pageStore.getPage(url)
        except HTTPError:
            raise sources.NoEntry

        result = source.processPage(data)
        return result

    def test_billyjoel(self):
        result = self.get("Billy Joel")

        assert re.search("singer-songwriter", result)

    def test_tjjasajs(self):
        self.assertRaises(sources.NoEntry,self.get,"tjjasajs")

class TestLeoSource(unittest.TestCase):
    def get(self,word):
        source = sources.LeoSource()
        url = source.getUrl(word)
        data = pageStore.getPage(url)

        result = source.processPage(data)
        return result

    def test_catholic(self):
        result = self.get("catholic")
        assert re.search("allumfassend", result)
        assert not re.search("Search tips", result)
        assert not re.search("LEO GmbH", result)
        #assert not re.search("<script", result)

    def test_anvik(self):
        self.assertRaises(sources.NoEntry,self.get,"anvik")

class TestMerriamWebsterSource(unittest.TestCase):
    def get(self,word):
        source = sources.MerriamWebsterSource()
        url = source.getUrl(word)
        data = pageStore.getPage(url)

        result = source.processPage(data)
        print result
        return result

    def test_catholic(self):
        result = self.get("catholic")
        assert re.search("cathol01", result)

    def test_doughnut(self):
        result = self.get("doughnut")
        assert re.search("doughnut", result)

    def test_anvik(self):
        self.assertRaises(sources.NoEntry,self.get,"anvik")

    def test_nurse(self):
        self.assertRaises(sources.NoEntry, self.get, "registered nurse")  # doesn't have a pronunciation

pageStore = CachedPageStore()

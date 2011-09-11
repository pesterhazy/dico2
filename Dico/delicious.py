import re, base64
from twisted.web import server
from twisted.web.client import getPage
from twisted.internet import defer
from twisted.persisted.dirdbm import Shelf
from urllib import quote

class NotFoundException(Exception):
    def __init__(self,word):
        self.word=word

    def __str__(self):
        return "Delicious tag not found: " + str(self.word)

class DeliciousAgent:
    re_post = re.compile('<post href="(.*?)"')
    re_amp = re.compile('&amp;')

    def __init__(self):
        self.shelf = Shelf("delicious-cache")

    def queryTag(self,query):
        try:
            result = self.shelf[query]
            return defer.succeed(result) # return result right away
        except KeyError:
            pass

        self.query = query
        url="https://api.del.icio.us/v1/posts/recent?count=1&tag=" + quote(self.query)
        user = "loevborg"
        password = "textor"

        d = self.getPageWithAuth(url,user,password)
        d.addCallback(self._cb_gotPage)
        d.addErrback(self._cb_err)
        return d

    def _cb_gotPage(self, xml):
        m=self.re_post.search(xml)
        if not m:
            raise NotFoundException(self.query)

        result = m.group(1)
        result = self.re_amp.sub('&', result)
        self.shelf[self.query] = result
        return result

    def _cb_err(self, err):
        raise NotFoundException(self.query)

    def getPageWithAuth(self,url,user,password):
        auth = base64.encodestring('%s:%s' % (
                    user, password))
        headers = {'Authorization':'Basic %s' % auth}

        d = getPage(url,headers=headers)
        return d

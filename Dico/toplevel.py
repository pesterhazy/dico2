# test

from twisted.web.resource import Resource
from twisted.web import static, server
import sys, re
import sources, lookup, delicious

class ToplevelResource(Resource):
    def __init__(self):
        Resource.__init__(self)
        f = static.File("static")
        self.putChild("",self)
        self.putChild("lookup",self)
        self.putChild("search",self)
        self.putChild("static",f)

    def getChild(self, name, request):
        if name == '':
            return self
        if name == 'go':
            return GoResource()
        return Resource.getChild(self, name, request)

    def render_GET(self, request):
        request.setHeader("Content-type", "text/html; charset=UTF-8")
        l = lookup.DictionaryLookup(request)

        try:
            word = str(request.args["q"][0])
        except KeyError:
            word = None

        return l.lookupWord(word)

class GoResource(Resource):
    isLeaf = True

    def render_GET(self, request):
        q = None
        d = delicious.DeliciousAgent()

        try:
            q = str(request.args["q"][0])
        except KeyError:
            m = re.match("/go/(.+)",request.path)
            if m:
                q = m.group(1)
            else:
                return self.showForm(request)

        deferred = d.queryTag(q)
        deferred.addCallback(self._cb_gotRespone, request)
        deferred.addErrback(self._cb_err, request)

        return server.NOT_DONE_YET

    def showForm(self, request):
        html = '<html><body><form method="GET">Go to: <input type="text" name="q" value=""/></form>'
        html += '</body></html>'

        request.write(html)
        request.finish()

    def _cb_gotRespone(self, url, request):
        request.setHeader("Location", url)
        request.setResponseCode(303, "See Other")
        request.finish()

    def _cb_err(self, failure, request):
        failure.trap(delicious.NotFoundException)
        request.write("<html><body><h1>Error</h1>Request failed. Error was: " + 
            str(failure.getErrorMessage()) + "</body></html>")
        request.finish()

from twisted.web import server
from twisted.web.client import getPage
from twisted.internet import defer
import twisted.web.error
import re
import sources

class DictionaryLookup:
    pretext = """
<html>
<head>
<link rel="stylesheet" href="/static/dico.css" type="text/css" media="all" />
<meta name="viewport" content="width=320; initial-scale=1.0; maximum-scale=1.0; user-scalable=0;" />
</head>
<body>
<script src="/static/dico.js" type="text/javascript"></script>
<script src="/static/cutstring.js" type="text/javascript"></script>
<form id="frm" method="GET" action="/search">
<div id="formEl">
<input id="frminput" type="text" name="q" value="$WORD" onfocus="this.select();"/>
<input type="submit"/>
</div>
</form>
"""
    def __init__(self, request):
        self.request = request

    def emptyForm(self):
        txt=self.pretext.replace("$WORD",'')
        txt+="</body></html>"
        return txt

    def lookupWord(self,word):
        if word == None:
            return self.emptyForm()

        self.request.n_results = 0

        txt=self.pretext.replace("$WORD",word)
        self.request.write(txt)

        sources_list = [
           sources.ReferenceDotComSource,
           sources.WikipediaSource,
           sources.UrbanDictionarySource,
           sources.LeoSource,
           sources.MerriamWebsterSource,
           sources.TFDIdiomsSource,
           ]

        list = []
        for src in sources_list:
            source = src()
            job = DictionaryJob(self.request, source)
            d = job.getAnswer(word)
            d.addCallback(self._cb_result)
            d.addErrback(self._cb_err)
            list.append(d)

        list = defer.DeferredList(list)
        list.addCallback(self._cb_lookupFinished)
        return server.NOT_DONE_YET

    def _cb_lookupFinished(self, value):
        if self.request.n_results == 0:
            self.request.write("<p>Search term not found.</p>")
        else:
            self.request.write("<p>Search returned %d result(s).</p>" % self.request.n_results)
        self.request.write("</body></html>")
        self.request.finish()

    def _cb_result(self, result):
        if result:
            self.request.write(result)
            self.request.n_results += 1

    def _cb_err(self, error):
        self.request.write("<p>The query failed: <pre>%s</pre></p>" % error.getTraceback())
        print "ERROR in getAnswer:", error.getTraceback()

class DictionaryJob:
    def __init__(self, request, source):
        self.request = request
        self.source = source

    def getAnswer(self,word):
        d = getPage(self.source.getUrl(word), timeout=10)
        d.addCallback(self._cb_getAnswer, word)
        d.addErrback(self._cb_err)
        return d

    def _cb_getAnswer(self, page, word):
        try:
            answer = self.source.processPage(page)
            text = "<div class=\"sourcename\"><a href=\""
            text += self.source.getUrl(word) + "\">" + self.source.name + "</a></div>"
            if self.request.n_results % 2:
                text += '<div class="answerAlt">'
            else:
                text += '<div class="answer">'
            text += str(answer)
            text += '</div>'
            text += "<span class=\"line\"/>"

            return text
        except sources.NoEntry:
            return None

    def _cb_err(self, error):
        if error.check(twisted.web.error.Error) and re.match('404',str(error.value)):
            self.source.handle404(error)
        else:
            error.raiseException()
        return None

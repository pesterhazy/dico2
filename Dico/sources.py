import re
import BeautifulSoup
from urllib import quote
from htmlstrip import htmltrim, htmlstrip
from uuid import uuid4

if BeautifulSoup.__version__ < "3.0.6":
    raise "BeautifulSoup version too old."

def dbg(st):
    f=file("debug.txt","w")
    f.write(st+"\n")

def wrap_in_collapse(text):
    id = str(uuid4())
    result = "<div id=\"" + id + "\">" + str(text) + "</div>"
    result += "<script type=\"text/javascript\">excerpt('" + id + "')</script>"
    return result

class NoEntry(Exception):
    pass

class AbstractSource:
    def handle404(self,error):
        error.raiseException()

class ReferenceDotComSource(AbstractSource):
    name="Reference.com"
    re1=re.compile('<span class="line"></span><span class="src">|<span class="src"><a href')
    re2=re.compile('<!-- end [\w-]* -->')
    re3=re.compile('<script.*?>.*?</script>',re.DOTALL)
    re4=re.compile('<span class="dic_helpLine">.*?</span>',re.DOTALL)
    re5=re.compile('cancerweb.ncl.ac.uk',re.DOTALL)
    re6=re.compile('Britannica.com',re.DOTALL)
    re_spelling=re.compile('<td>Dictionary suggestions:<br />(.*?)</td>',re.DOTALL)

    def getUrl(self,word):
        self.word = word
        return "http://dictionary.reference.com/browse/" + quote(self.word)

    def processPage(self,page):
        text = str(page)
        info = ""

        if not text.find('body class="dictionary"'): #sanity check
            raise NoEntry

        if text.find("No results found for") >= 0:
            soup = BeautifulSoup.BeautifulSoup(text)
            for table in soup.findAll("table"):
                s = str(table)
                if s.find("Dictionary suggestions") != -1 or s.find("spellLd") != -1:
                    s = s.replace("http://dictionary.reference.com/browse/","/search?q=")
                    return s

            raise NoEntry
        
        soup = BeautifulSoup.BeautifulSoup(text)

        divs = soup.findAll("div", attrs={'class':re.compile("lunatext")} )
        if len(divs) == 0:
            file('/tmp/test.txt','w').write(text)
            raise NoEntry

        for div in divs:
           info += str(div)

        info=self.__class__.re3.sub('',info)
        info=self.__class__.re4.sub('',info)
        info=info.replace('<a href="/browse/','<a href="/search?q=')
        return wrap_in_collapse(info)

class UrbanDictionarySource(AbstractSource):
    name="Urban Dictionary"
    re_noscript=re.compile('<script.*?>.*?</script>',re.DOTALL)

    def getUrl(self,word):
        return 'http://www.urbandictionary.com/define.php?term=' + quote(word)

    def processPage(self,page):
        if page.find("not_defined_yet") >= 0:
            raise NoEntry

        soup=BeautifulSoup.BeautifulSoup(page)
        el=soup.find(id="entries")
        el=str(el)
        el=self.re_noscript.sub('',el)
        return wrap_in_collapse(el)

class WikipediaSource(AbstractSource):
    name="Wikipedia"
    re_content=re.compile('<!-- bodytext -->(.*?)<!-- /bodytext -->',re.DOTALL)

    def getUrl(self,word):
        url = 'http://en.wikipedia.org/wiki/' + quote(word)
        return url

    def processPage(self,page):
        if page.find("Wikipedia does not have an article with this exact name") >= 0:
            raise NoEntry

        text = page
        text = self.re_content.search(text).group(1)

        s=BeautifulSoup.BeautifulSoup(text)
        for tag in s.findAll("table"):
            tag.extract()
        text = s.renderContents()

        text = text.replace('<a href="/wiki/','<a href="http://en.wikipedia.org/wiki/')

        return wrap_in_collapse(text)

    # override error handling as Wikipedia returns 404s
    def handle404(self, error):
        return None

class LeoSource(AbstractSource):
    name="Leo"
    re_noscript=re.compile('<script.*?>.*?</script>',re.DOTALL)

    def getUrl(self,word):
        return 'http://dict.leo.org/ende?lp=ende&lang=en&searchLoc=-1&cmpType=relaxed&sectHdr=on&spellToler=on&chinese=both&pinyin=diacritic&search=%s&relink=off' % quote(word)

    def processPage(self,page):
        if page.find("The dictionary does not contain any entries for") >= 0:
            raise NoEntry

        soup=BeautifulSoup.BeautifulSoup(page)
        el=soup.find(id="results")
        trs=el.findChildren(name='tr',recursive=False)
        result=''
        for tag in trs:
            st = str(tag)
            if st.find('<th>ENGLISH</th>')>=0:
                continue
            if st.find('colspan="5"')>=0:
                continue
            if st.find('colspan="3"')>=0:
                continue
            if st.find('colspan="4"')>=0:
                continue
            if st.find('savebutton')>=0:
                continue
            if st.find('class="sidebar"')>=0:
                continue

            cols = tag.contents

            out = cols[1].renderContents() + ': '
            out += cols[3].renderContents()

            result = result + out
            result = result + '<br/>'

        return wrap_in_collapse(result)

class MerriamWebsterSource(AbstractSource):
    name="Merriam Webster"

    def getUrl(self,word):
        return 'http://www.merriam-webster.com/dictionary/%s' % quote(word)

    def processPage(self,page):
        if page.find("The word you've entered isn't in the dictionary") >= 0:
            raise NoEntry

        # try two regex's
        r = re.findall("return au\('(.*?)', '(.*?)'\)",page)
        if len(r) == 0:
            r = re.findall("'/cgi-bin/audio.pl\?(.*?)=(.*?)'",page)

        if len(r) == 0:
            raise NoEntry

        result = ''
        result += 'Audio pronunciation for: '
        count = 0

        for match in r:
            url = 'http://www.merriam-webster.com/cgi-bin/audio.pl?' + match[0]
            word = match[1]

            if count > 0:
                result += '; '

            result += '%d. <a href="%s">%s</a>' % (count+1,url,word)
            count += 1

        return result

class TFDIdiomsSource(AbstractSource):
    name="The Free Dictionary Idioms"

    def getUrl(self,word):
        return 'http://idioms.thefreedictionary.com/%s' % quote(word)

    def processPage(self,page):
        if "is not available in the Idioms" in str(page):
            raise NoEntry

        soup=BeautifulSoup.BeautifulSoup(page)
        el=soup.find("div",id="MainTxt")
        el=str(el)
        el=el.replace('<a href="','<a href="/search?q=')
#        el=self.re_noscript.sub('',el)
        return wrap_in_collapse(el)


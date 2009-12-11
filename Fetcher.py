import pycurl
import StringIO
import htmllib
import formatter
import string
import urllib, urlparse
import pickle
import re
from urlparse import urljoin
from StripTags import StrippingParser
from RobotsFetcher import RobotsFetcher
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup, SoupStrainer


links = SoupStrainer('a')
anchor_remove = re.compile('#(.*)$') #regex to remove from url Ex: uol.com.br/index.php?oejea=aepokea#text

class Fetcher():
    def __init__(self):
        self.contenttype = ''
        self.http_code = 404
    def getNext(self):
        buffer = StringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, 'http://localhost:8888/contextgraph/page/getnext')
        c.setopt(c.REFERER,'')
        c.setopt(c.USERAGENT,'Curl')
        c.setopt(c.WRITEFUNCTION, buffer.write)
        c.perform()
        c.close()
        return buffer.getvalue()

    def treatHeader(self, buf):
        if re.match('Content-Type:', buf):
            m = re.search('Content-Type: ([a-z/]*);?', buf)
            if m:
                self.contenttype = m.group(1)

    def checkHeader(self):
        if self.contenttype!='application/xhtml+xml' and self.contenttype!='text/html':
            print '[Fetcher] . Not html'
            self.contenttype=''  #reset var
            return False
        if self.http_code == 404:
            print '[Fetcher] . 404 - Not Found!'
            self.http_code = 404
            return False
        return True


    def getPage(self, url):
        print '----', url, '----'
        print 'Checking robots.txt:'
        page_dict = {}
        page_dict['passed_robots']=True;
        page_dict['text'] = ''
        if not RobotsFetcher.can_fetch(url):
            page_dict['passed_robots']=False;
            print '[getPage] . PAGE REJECT BY ROBOTS.TXT'
            return page_dict;
        else:
            print "Fetching..."
            buffer = StringIO.StringIO()
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.REFERER,'')
            c.setopt(c.USERAGENT,'DBCrawler')
            c.setopt(c.FOLLOWLOCATION, 1)
            c.setopt(c.WRITEFUNCTION, buffer.write)
            c.setopt(c.HEADERFUNCTION, self.treatHeader)
            try:
                c.perform()
                self.http_code = c.getinfo(pycurl.HTTP_CODE)
            except pycurl.error, e:
                print "Error code: ", e[0]
                print "Error message: ", e[1]
                c.close()
                return page_dict
            c.close()

            if not self.checkHeader():       #check if header is ok (text and not 404 not found)
                return page_dict

            print "Parsing... "
#            print buffer.getvalue()
#            soup = BeautifulSoup(buffer.getvalue(), parseOnlyThese=links)
            soup = BeautifulSoup(buffer.getvalue(), parseOnlyThese=links, convertEntities=BeautifulSoup.HTML_ENTITIES)
            all_links = []
            for link in soup:
                if link.has_key('href'):
                    link = link['href'].strip() #strip - remove extra spaces
                    link = anchor_remove.sub('', link).lower()
                    if link.endswith('/'):
                        link = link[:-1]
                    link = link.lower()
                    if not link.startswith("http") :
                        if not link.startswith('javascript:') and not link.startswith('mailto:') and not link.startswith("ftp") and not link.startswith("aim"):
                            all_links.append(urljoin(url,link))
                    else:
                        all_links.append(link)
            page_dict["url"] = url
            page_dict["links"] = all_links
            parser = StrippingParser()
            html = str(BeautifulStoneSoup(buffer.getvalue(),convertEntities=BeautifulStoneSoup.HTML_ENTITIES))
            page_text = parser.strip(html)
            page_dict["text"] = page_text
            page_dict['passed_robots']=True;
    #        page_dict["title"] = p.title
            return page_dict

    def sendPageBack(self, page_dict):
        dict_serialized = pickle.dumps(page_dict)
        c = pycurl.Curl()
        c.setopt(c.URL, 'http://localhost:8888/contextgraph/page/sendback')
        c.setopt(c.POST, 1)
        c.setopt(c.POSTFIELDS, "page="+urllib.quote(dict_serialized))
        c.setopt(c.USERAGENT,'Curl')
        c.perform()

    def run(self):
        while True:
            url = self.getNext()
            if url=='Empty Queue':     #Empty queue stop fetcher
                break;
            page_dict = self.getPage(url)
            if page_dict['passed_robots'] and not page_dict['text']=='':
                self.sendPageBack(page_dict)
        print 'Fetcher Stopped'

if __name__ == '__main__':
    fetcher = Fetcher()
    fetcher.run()

#c = pycurl.Curl()
#c.setopt(c.URL, 'http://localhost:8888/contextGraph/getNext')
#c.setopt(c.COOKIEJAR, 'cookies.txt')
#c.setopt(c.COOKIEFILE, 'cookies.txt')
#
##c.setopt(c.POST, 1)
##c.setopt(c.POSTFIELDS, "User=smith&Password=password")
##c.setopt(c.VERBOSE, 1)
#c.setopt(c.REFERER,'')
#c.setopt(c.USERAGENT,'Curl')
#c.setopt(c.WRITEFUNCTION, buffer.write)
#c.setopt(c.SSL_VERIFYHOST, 0)
#c.setopt(c.SSL_VERIFYPEER, False)
#
##c.setopt(c.PROXY, proxyHostAndPort)
##c.setopt(c.PROXYUSERPWD, proxyAuthentication)
#
#c.perform()
#c.close()
#
#print buffer.getvalue()


# -*- coding: utf-8 -*-
import xml.dom.minidom
import time
from urllib import urlopen

class Bing():


    def __init__(self,url,npaginas):
        self.lista = []
        url = "\""+url+"\""
        print "Getting backlinks of:", url
        for offset in range(0,npaginas/10):
            self.lista+=(self.getBackLinks(url,10,offset))

    def getText(self,nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc

    def handleXML(self,xml):

        lista_url = []
        elements = (xml.getElementsByTagName("Url"))
        for e in elements:
            lista_url.append(self.getText(e.childNodes))

        return lista_url

    def getBackLinks(self,url,count=10,offset=0):
        lista = []

        query = "link:"+url+"-site:"+url

        bing_url = "http://api.search.live.net/xml.aspx?Appid=710700C8A14F8CBD1FF7BBEAB93317F4D5FECC8D&query="+query+"&sources=web&web.count="+`count`+"&web.offset="+`offset*10`

        doc = urlopen(bing_url).read()
    	#time.sleep(1) #10 por segundo
        doc = doc.replace("web:", "")

        dom = xml.dom.minidom.parseString(doc)

        lista = self.handleXML(dom)
#        print "FIM"
        return lista


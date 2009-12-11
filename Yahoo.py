# -*- coding: utf-8 -*-
import xml.dom.minidom
import time
from urllib import urlopen
import pycurl
import StringIO

class Yahoo():


    def __init__(self,url,npaginas):
        self.lista = []
        for offset in range(0,npaginas/10):
            self.lista+=(self.getBackLinks(url,10,offset))

    def getText(self,nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return str(rc)

    def handleXML(self,xml):

        lista_url = []
        elements = (xml.getElementsByTagName("url"))
        for e in elements:
#            print "."
#            print self.getText(e.childNodes)
            lista_url.append(self.getText(e.childNodes))

        return lista_url

    def getBackLinks(self,url,count=10,offset=0):

        lista = []
        yahoo_url = "http://boss.yahooapis.com/ysearch/se_inlink/v1/"+url+"?appid=kdbMnrDV34EDltvh4p4nEy8ed8v8bcSH9WYHzK7wOd2bOkgYjuSGtoSDe1YmxPMGLVTE&format=xml&count="+`count`+"&start="+`offset`
        page = urlopen(yahoo_url)
        if page.getcode()!=400:             #nao retornou bad request
            doc = page.read()
        else:
            print 'http 400 - bad request'
            return []
#        print doc
        time.sleep(3)
        dom = xml.dom.minidom.parseString(doc)
        lista = self.handleXML(dom)
        return lista

#if __name__ == "__main__":


#    yahoo = Yahoo("www.uol.com.br",300) #yahoo.lista eh uma lista, nao um cachorro!
#    print len(yahoo.lista)


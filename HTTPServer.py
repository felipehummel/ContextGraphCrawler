import tornado.httpserver
import tornado.ioloop
import tornado.web
import time
import pickle
import os
from ContextGraph import *
from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

context_graph = ContextGraph()

if os.path.exists('layer0.txt'):
    context_graph.readLayerZeroFile('layer0.txt')
else:
    context_graph.readLayerZeroFile(sys.argv[0])

if os.path.exists('seeds.txt'):
    context_graph.readSeedsFile('seeds.txt')
else:
    context_graph.readSeedsFile(sys.argv[1])

#page_dict = context_graph.fetcher.getPage('http://www.uol.com.br/')
#print page_dict
context_graph.initGraph()
context_graph.printLayers()
context_graph.fetchSeeds()
context_graph.trainClassifier()

#context_graph.addSeed(Page("http://esporte.uol.com.br/f1/", True))
#context_graph.addSeed(Page("http://globoesporte.globo.com/Esportes/Formula_1/01501100.html", True))
#context_graph.addSeed(Page("http://www.f1naweb.com.br/", True))
#context_graph.addSeed(Page("http://www.f1mania.net/noticias/categorias.php?cat=F%F3rmula%201", True))
#context_graph.addSeed(Page("http://esportes.terra.com.br/automobilismo/formula1/2009/", True))
#context_graph.addSeed(Page("http://quatrorodas.abril.com.br/grid/", True))
#context_graph.addSeed(Page("http://formula12009br.blogspot.com/", True))
#context_graph.addSeed(Page("http://esportes.terra.com.br/ultimas/0EI1298800.html", True))
#context_graph.addSeed(Page("http://www.portalf1.com/site/f1.asp", True))
#context_graph.addSeed(Page("http://www.gpbrasil.com.br/Sitegp/index.asp", True))




page_id=0

class NextPage(tornado.web.RequestHandler):
    def get(self):
        already_fetched=False
        while not already_fetched:
            page = context_graph.getNextQueuedPage()
            if page not in context_graph.visited_urls:
                context_graph.visited_urls.add(page)
                already_fetched=True
        print 'Sending to fetcher: ', page
        self.write(page)

class PageBack(tornado.web.RequestHandler):
    def post(self):
        global page_id
        page_dict = pickle.loads(self.request.arguments["page"][0])


#        """REMOVER ISSO AQUI"""
#        for link in page_dict['links']:
#            context_graph.addToQueue(2, link, 5)
#        """------------------"""


        if page_dict['passed_robots']:
            layer = context_graph.classify(page_dict)
            context_graph.store(page_dict, layer, page_id)
            page_id += 1
            print page_id
        else:
            print 'Rejected page'



class CrawlInfo(tornado.web.RequestHandler):
    def get(self):
        print 'Sending INFO PAGE'
        info = '<p>Pages Crawled: '+str(page_id)+'</p>'
        info += '<p>Queue 0 Size:'+str(len(context_graph.queues[0]))+' </p>'
        info += '<p>Queue 1 Size:'+str(len(context_graph.queues[1]))+' </p>'
        info += '<p>Queue 2 Size:'+str(len(context_graph.queues[2]))+' </p>'
        info += '<p>Queue 3 Size:'+str(len(context_graph.queues[3]))+' </p>'
        info += '<p>Queue 4 Size:'+str(len(context_graph.queues[4]))+' </p>'
        self.write(info)

if __name__ == "__main__":

    application = tornado.web.Application([ (r"/contextgraph/page/getnext", NextPage),
                                            (r"/contextgraph/page/sendback", PageBack),
                                            (r"/contextgraph/info", CrawlInfo) ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


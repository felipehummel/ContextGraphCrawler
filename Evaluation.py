# coding=latin-1

import os
import tornado.httpserver
import tornado.ioloop
import tornado.web
import random
from tornado.options import define, options
define("port", default=9999, help="run on the given port", type=int)

class Evaluator:
    def __init__(self, is_random):
        self.is_random = is_random
        self.layer0_path = 'crawl/0/'
        self.pages = []
        self.relevant_pages = []
        self.irrelevant_pages = []
        self.num_pages_evaluated = 0
        self.pages_fetched = 0
        self.current_page_index = 0
        self.evaluated_pages_set = set()
        self.experiments_file = open('experiments.txt', 'w')

    """Search all directories (of domains) in the layer0_path and pass to processDir method"""
    def init(self):
        for dir in os.listdir(self.layer0_path):
            self.processDir(self.layer0_path+dir)
        self.pages.sort(lambda x,y:cmp(x[0],y[0]))   #sorting list of tuples by page_id
        for page in self.pages:
            print page

    def processDir(self, dir):
        for file in os.listdir(dir):
            self.addFile(dir+'/'+file)

    def addFile(self, file_path):
        index = file_path.rfind('/')+1
        page_id = int(file_path[index:])
        page_file = open(file_path, 'r')
        url = page_file.readline().replace('\n', '')
        self.pages.append((page_id, url))

    """get a random page from the pages list of tuples"""
    def getRandomPage(self):
        index = random.randint(0,len(self.pages)-1)
        print index, ' tamanho: ', len(self.pages)
        page = self.pages[index]
        return page

    """Used to get another random page to be evaluated"""
    def nextRandom(self):
        page = self.getRandomPage()
        while page[0] in self.evaluated_pages_set:  #check if page_id is already in the evaluated_pages set
            page = self.getRandomPage()                    #page tuple
        self.evaluated_pages_set.add(page[0])
        return page

    """Used to get the next page in CRAWLING ORDER!"""
    def nextByIndex(self):
        page = self.pages[self.current_page_index]
        self.current_page_index += 1

    def getNext(self):
        if self.is_random:
            page = self.nextRandom()
        else:
            page = self.nextByIndex()
        return page

    def addEvaluation(self, page_id, relevant):
        page = self.pages[page_id]
        if relevant:
            self.relevant_pages.append(page)
            print "RELEVANTE: ", page
        else:
            self.irrelevant_pages.append(page)
            print "NÃO RELEVANTE: ", page
        self.storeFile(relevant, page)

    def storeFile(self, is_relevant, page_tuple):
        if self.is_random:
            self.experiments_file = open('experiments.txt', 'w')
            self.experiments_file.write('Relevant: '+str(len(self.relevant_pages))+' | Irrelevant: '+str(len(self.irrelevant_pages))+'\n')
        else:
            #TODO: ABrir experiments_file com APPEND NO FINAL DO ARQUIVO!!!
            self.experiments_file.write('\n')
        self.experiments_file.close()
        print self.num_pages_evaluated


class Evaluate(tornado.web.RequestHandler):
    def get(self):
        if 'page_id' in self.request.arguments:         #if GET is defined
            evaluator.num_pages_evaluated += 1
            if int(self.request.arguments['relevant'][0])==0:
                evaluator.addEvaluation(int(self.request.arguments['page_id'][0]), False)
            else:
                evaluator.addEvaluation(int(self.request.arguments['page_id'][0]), True)
        page_id, url = evaluator.getNext()
        iframe = '<p>'+url+'</p><CENTER><iframe src=\"'+url+'\" width=1000 height=800></iframe></CENTER>'
        links = '<a href=\"/evaluator/evaluate?page_id='+str(page_id)+'&relevant=1\">RELEVANTE</a> </br> <a href=\"/evaluator/evaluate?page_id='+str(page_id)+'&relevant=0\">NÃO RELEVANTE</a>'
        page = links+iframe+'</br>'
        self.write(str(page))
#        self.flush() N EH NECESSARIO


if __name__ == "__main__":
    print 'Initializing Evaluator'
    evaluator = Evaluator(True) #true = random, false = not random
    evaluator.init()
    application = tornado.web.Application([ (r"/evaluator/evaluate", Evaluate)])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


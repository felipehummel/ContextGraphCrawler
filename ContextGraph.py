from HeapQueue import LayerQueue
from Bing import Bing
from urlparse import urlparse
import os
from Fetcher import Fetcher
from Yahoo import Yahoo
import random
import pickle
from svmBD import QueueClassifier

class Page(object):
    def __init__(self, _url, _is_seed=False):
        self.url = _url
#        self.points_to = _points_to
        self.is_seed = _is_seed
        self.text = ""
    def isSeed(self):
        return self.is_seed

    def setText(self, _text):
        self.text = _text

    def setPageDict(self, _dict):
        self.page_dict = _dict

    def __str__(self):
        return self.url+" | Texto do documento: "+self.text

class ContextGraph(object):

    def __init__(self):
        self.queues = []
        self.layers = []
        self.layers.append([])
        self.layers.append([])
        self.layers.append([])
        self.layers.append([])
        self.layers.append([])

        self.queues.append(LayerQueue())
        self.queues.append(LayerQueue())
        self.queues.append(LayerQueue())
        self.queues.append(LayerQueue())
        self.queues.append(LayerQueue())
        self.queues.append(LayerQueue())

        self.fetcher = Fetcher()
        self.visited_urls = set()
        self.urls_already_in_layers = set()
    def addToQueue(self, queue, page, score):
        self.queues[queue].putPage(page, score)

    def getNextQueuedPage(self):
    	for queue in self.queues:
    		if not queue.isEmpty():
    			return queue.getPage()
    	else:
    		print "No urls in queue"
    		return 'Empty Queue'

    """Pega pagina, classifica bota na queue correta"""
    def classify(self, page_dict):
        layer = self.classifier.predictQueue(page_dict['text'])
        layer, score = self.classifier.predictQueue(page_dict['text'])
        #ele vai adicionar todos os links dessa pagina na queue classificada, n eh soh um addToQueue, sao varios
        for link in page_dict['links']:
            self.addToQueue(layer, link, score)
        return layer

    def store(self, page_dict, layer, page_id):
        crawl_directory = 'crawl/'
        path = crawl_directory+str(layer)
        self.check_dir(path)
        path = path+'/'+urlparse(page_dict['url']).netloc
        self.check_dir(path)
        path = path+'/'+str(page_id)
        page_store = open(path, 'w')
        page_store.write(page_dict['url']+'\n')
        page_store.write(page_dict['text']+'\n')

    def check_dir(self, path):
        if not os.path.exists(path):
            os.mkdir(path)

    def addSeed(self, _seed):
        self.layers[0].append(_seed)

    def addToLayer(self, layer, page):
        if not page.url in self.urls_already_in_layers:
            self.urls_already_in_layers.add(page.url)
            self.layers[layer].append(page)
#        +'/'+page.url.replace("s", " ")
#        file = open("layers/"+str(layer)+'/'+page.url.replace("/", "_"),"wb")
#        pickle.dump(page, file)

    """ layer = o layer da page passada """
    def constructGraph(self, seed, layer, num_backlinks):
        print "constructing layer:", layer, " of seed:", seed.url
        list_urls = self.getBackLinks(seed.url, num_backlinks, layer)
        if layer<=3:
            for url in list_urls:
                page = Page(url)      #points_to = seed
                print 'fetching backlink page: ', url
                page_dict = self.fetcher.getPage(url)
                page.setText(page_dict['text'])
                self.addToLayer(layer+1, page)

    def initGraph(self):
        """1 de cada"""
#        for seed in self.layers[0]:
#            self.constructGraph(seed, 0, 300)
#        for page in self.layers[1]:
#            self.constructGraph(page, 1, 1)
#        for page in self.layers[2]:
#            self.constructGraph(page, 2, 1)
#        for page in self.layers[3]:
#            self.constructGraph(page, 3, 1)
#        for page in self.layers[4]:
#            self.constructGraph(page, 4, 1)
        """aleatorio"""
        num_backlinks = 10
        num_each = 10
        for seed in self.layers[0]:
            self.constructGraph(seed, 0, num_backlinks)
        already_used= set()
        for num in range(0, num_backlinks):
            i = random.randint(0, len(self.layers[1])-1)
            while i in already_used:
                i = random.randint(0, len(self.layers[1])-1)
            already_used.add(i)
            self.constructGraph(self.layers[1][i], 1, num_each)
        already_used= set()
        for num in range(0, num_backlinks):
            i = random.randint(0, len(self.layers[2])-1)
            while i in already_used:
                i = random.randint(0, len(self.layers[2])-1)
            already_used.add(i)
            self.constructGraph(self.layers[2][i], 2, num_each)
        already_used= set()
        for num in range(0, num_backlinks):
            i = random.randint(0, len(self.layers[3])-1)
            while i in already_used:
                i = random.randint(0, len(self.layers[3])-1)
            already_used.add(i)
            self.constructGraph(self.layers[3][i], 3, num_each)
#        already_used= set()
#        for num in range(0, num_backlinks):
#            i = random.randint(0, len(self.layers[4])-1)
#            while i in already_used:
#                i = random.randint(0, len(self.layers[4])-1)
#            already_used.add(i)
#            self.constructGraph(self.layers[4][i], 4, num_each)

    def readLayerZeroFile(self, layer0_txt):
        layer0_txt = open(layer0_txt, 'r')
        for line in layer0_txt:
            line = line.replace("\n", "")
            if not line=="" and not line==" ":
                self.addSeed(Page(line.replace("\n", ""), True))

    def readSeedsFile(self, seeds_txt):
        seeds_txt = open(seeds_txt, 'r')
        for line in seeds_txt:
            line = line.replace("\n", "")
            if not line=="":
                self.addToQueue(5, line.replace("\n", ""), 1) #score = 1

    def getBackLinks(self, page_url, num, layer):
        print 'Getting ', page_url, 'backlinks...'
        yahoo = Yahoo(page_url, num)
        return yahoo.lista
#        lista = []
#        for pos in range(0, num):
#            url = 'www.backlink'+str(pos)+'.com?layer='+str(layer)
#            lista.append(url)
#        return lista


    def trainClassifier(self):
        #gera lista de listas
        list_layers = []
        for layer in self.layers:
            current_layer = []
            for page in layer:
                current_layer.append(page.text)
            list_layers.append(current_layer)
        self.classifier = QueueClassifier(list_layers)
        print self.classifier.predictQueue("ei ou are one")

    def fetchSeeds(self):
        for page in self.layers[0]:
            page_dict = self.fetcher.getPage(page.url)
            page.setText(page_dict['text'])

    def printLayers(self):
        for i in range(0,5):
            print "Layer", i, ' - Size: ', len(self.layers[i])
            for page in self.layers[i]:
                if not page.isSeed():
                    pass
#                    print "[",i,"] -", page.url, "| points_to:", page.points_to.url, "| Seed?= ", page.isSeed()
                else:
                    pass
#                    print "[",i,"] -", page.url, "| Seed?= ", page.isSeed()

if __name__ == "__main__":
    cg = ContextGraph()
    cg.addSeed(Page("http://esporte.uol.com.br/f1/", True))
    cg.addSeed(Page("http://globoesporte.globo.com/Esportes/Formula_1/01501100.html", True))
    cg.addSeed(Page("http://www.f1naweb.com.br/", True))
    cg.addSeed(Page("http://www.f1mania.net/noticias/categorias.php?cat=F%F3rmula%201", True))
    cg.addSeed(Page("http://esportes.terra.com.br/automobilismo/formula1/2009/", True))
    cg.addSeed(Page("http://quatrorodas.abril.com.br/grid/", True))
    cg.addSeed(Page("http://formula12009br.blogspot.com/", True))
    cg.addSeed(Page("http://esportes.terra.com.br/ultimas/0EI1298800.html", True))
    cg.addSeed(Page("http://www.portalf1.com/site/f1.asp", True))
    cg.addSeed(Page("http://www.gpbrasil.com.br/Sitegp/index.asp", True))

    cg.initGraph()
    cg.fetchSeeds()
    cg.trainClassifier()
    cg.printLayers()


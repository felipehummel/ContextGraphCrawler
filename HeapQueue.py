from heapq import heappush,heappop

class LayerQueue(object):
    """Creates a priority queue using a heap data structure"""
    def __init__(self,layer=None):
        self.__heap = []
        self.layer = layer

    def putPage(self,url=None,score=0):
        """Puts an URL with an determinated score value in the heap queue"""
        heappush(self.__heap,(-1*score,url))

    def getPage(self):
        """Pops an URL with an determinated score value in the heap queue"""
        return heappop(self.__heap)[1]

    def isEmpty(self):
        if len(self.__heap)==0:
            return True
        else:
            return False
    def __len__(self):
        return len(self.__heap)

if __name__ == "__main__":
    # Simple sanity test
    queue = HeapQueue(1)
    queue.putUrl("guilherme",35)
    queue.putUrl("hummel",24)
    queue.putUrl("william",11)
    queue.putUrl("mirel",48)
    queue.putUrl("everlin",17)
    print queue.getUrl()
    print queue.layer


import threading
import ExitQueue

class work:
    """Base class for doin' all the work
       It's used to enqueue the thing and do the work in some worker threads"""
    def doIt(self):
        pass

class worker:
    def __init__(self, num):
        self.queue = ExitQueue.Queue()
        for i in range(num):
            t = threading.Thread(target=self.worker)
            t.start()

    def worker(self):
        try:
            while True:
                item = self.queue.get()
                item.doIt()
                self.queue.task_done()
        except ExitQueue.Exit:
            pass

    def put(self, item):
        self.queue.put(item)
    
    def __del__(self):
        self.queue.close()

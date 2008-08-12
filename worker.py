import threading
import Queue

class work:
    """Base class for doin' all the work
       It's used to enqueue the thing and do the work in some worker threads"""
    def doIt(self):
        pass

class worker:
    def __init__(self, num):
        self.queue = Queue.Queue()
        self.num = num

    def worker(self):
        while True:
            item = self.queue.get()
            item.doIt()
            self.queue.task_done()

    def put(self, item):
        self.queue.put(item)

    def serve_forever(self):
        for i in range(self.num):
            t = threading.Thread(target=self.worker)
            t.setDaemon(True)
            t.start()

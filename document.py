from __future__ import with_statement
import threading, time
import os,sys
import Queue

class document:
    """Class representing a document"""
    def __init__(self, config, targetfile=None, format="pdf"):
        self.config = config
        r, w = os.pipe()
        self.pid = os.fork()
        if self.pid:
            os.close(r)
            self.cmd = os.fdopen(w, 'w')
        else:
            import pyx
            from PIL import Image
            def worker():
                while True:
                    item = queue.get()
                    image = Image.open(item[0])
                    if format == "pdf":
                        c = pyx.canvas.canvas()
                        c.insert(pyx.bitmap.bitmap(0,0,image,pyx.document.paperformat.A4.width,pyx.document.paperformat.A4.height,compressmode=item[1],dctquality=int(item[2]),flatecompresslevel=int(item[3])))
                        pages[item[4]] = pyx.document.page(c)
                    else:
                        filename = "%s-%d.%s" % targetfile, item[4], format
                        image.save(filename)
                        os.chmod(filename, 0664)
                    os.unlink(item[0])
                    del image
                    queue.task_done()
                
            os.close(w)
            cmd = os.fdopen(r, 'r')
            if targetfile == None:
                targetfile="%s/scan-%d" % (config.destination, int(time.time()))
            pages          = []
            pagenumber     = 0
            in_conversion  = 0
            queue = Queue.Queue()
            for i in range(config.num_worker_threads):
                t = threading.Thread(target=worker)
                t.setDaemon(True)
                t.start()
            for command in cmd:
                command=command.strip()
                if command == 'finish':
                    break
                else:
                    pages.append(None)
                    queue.put(command.rsplit(' ',3)+[pagenumber])
                    pagenumber = pagenumber + 1
            queue.join()
            if format == 'pdf':
                d = pyx.document.document(pages)
                filename = "%s.%s" % (targetfile, format)
                d.writePDFfile(filename)
                os.chmod(filename,0664)
            cmd.close()
            os._exit(0)


    def process_image(self, im, compressmode='DCT', dct_quality=None, flatecompresslevel=None):
        if dct_quality == None:
            dct_quality = self.config.default_dct_quality
        if flatecompresslevel == None:
            flatecompresslevel = self.config.default_flatecompresslevel
        self.cmd.write(im+' '+compressmode+' '+str(dct_quality)+' '+str(flatecompresslevel)+'\n')


    def finish(self):
        t = threading.Thread(target=self.__finish)
        t.start()

    def __finish(self):
        self.cmd.write('finish\n')
        self.cmd.close()
        os.waitpid(self.pid,0)


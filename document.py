from __future__ import with_statement
import threading, time
import os,sys

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
            def worker():
                while True:
                    item = queue.get().rsplit(' ',4)
                    image = Image.open(item[0])
                    if format == "pdf":
                        c = pyx.canvas.canvas()
                        c.insert(pyx.bitmap.bitmap(0,0,image,pyx.document.paperformat.A4.width,pyx.document.paperformat.height,compressmode=item[1],dctquality=int(item[2]),flatecompresslevel=int(item[3]))
                        p=pyx.document.page(c)
                        #insert
                    else:
                        image.save(
                
            os.close(w)
            cmd = os.fdopen(r, 'r')
            if targetfile == None:
                targetfile="%s/scan-%d" % (config.destination, int(time.time()))
            pages          = []
            pagenumber     = 0
            in_conversion  = 0
            conversion_condition = threading.Condition()
            for command in cmd:
                command=command.strip()
                if command == 'finish':
                    cmd.close()
                    sys.exit(0)
                else:
                    print command

    def filename(self, page=None):
        if page == None:
            return "%s.%s" % (self.targetfile,self.format)
        else:
            return "%s-%d.%s" % (self.targetfile,page,self.format)

    def process_image(self, im, compressmode='DCT', dct_quality=None, flatecompresslevel=None):
        if dct_quality == None:
            dct_quality = self.config.default_dct_quality
        if flatecompresslevel == None:
            flatecompresslevel = self.config.default_flatecompresslevel
        self.cmd.write(im+' '+compressmode+' '+str(dct_quality)+' '+str(flatecompresslevel)+'\n')
#        if self.format == "pdf":
#            w = pdf.picture2pdf(im, self, self.pagenumber, compressmode, dct_quality, flatecompresslevel)
#            self.pages.append(None)
#        else:
#            w = conversion.picture2file(im, self, self.pagenumber+1)
#        self.pagenumber = self.pagenumber + 1
#        with self.conversion_condition:
#            if self.maxconversion:
#                while self.in_conversion >= self.maxconversion:
#                    self.conversion_condition.wait()                
#            self.in_conversion = self.in_conversion + 1

    def insert(self, pagenumber, page):
        pass
#        self.pages[pagenumber] = page
#        with self.conversion_condition:
#            self.in_conversion = self.in_conversion - 1
#            self.conversion_condition.notifyAll()

    def finalize(self):
        pass
#        with self.conversion_condition:
#            while self.in_conversion:
#                self.conversion_condition.wait()
#            pdf.makepdf(self.filename(), self.pages)
#            os.chmod(self.filename(), 0664)
#            del self.pages
    def finish(self):
        self.cmd.write('finish\n')
        self.cmd.close()
        os.waitpid(self.pid,0)


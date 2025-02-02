
from queue import Queue 
from utils.config import globalconfig  
from threading import Thread
import os,time
from traceback import print_exc


class basetrans:
     
    @property
    def srclang(self):
        try:
            return globalconfig['fanyi'][self.typename]['lang'][[1,2][globalconfig['srclang']]] 
        except:
            return ''
    @property
    def tgtlang(self):
        try:
            return globalconfig['fanyi'][self.typename]['lang'][[0,2][globalconfig['tgtlang']]] 
        except:
            return ''
    @classmethod
    def settypename(self,typename):
        self.typename=typename
    def __init__(self) : 
        self.queue=Queue() 
        try: 
            self.inittranslator() 
        except:
            print_exc()
        self.lastrequeststime=0
        self._cache={}
        self._MAXCACHE = 512
        self.t=Thread(target=self.fythread) 
        self.t.setDaemon(True)
        self.t.start()
        
        self.newline=None
    def gettask(self,content):
        self.queue.put((content))
     
    def inittranslator(self):
        pass
    def translate(self,content):
        pass
      
    def cached_translate(self,contentsolved):
        langkey=(self.srclang,self.tgtlang)
        if langkey not in self._cache:
            self._cache[langkey]={}
        try:
            return self._cache[langkey][contentsolved]
        except KeyError:
            pass
        
        if len(self._cache[langkey]) >= self._MAXCACHE:
            # Drop the oldest item
            try:
                del self._cache[langkey][next(iter(self._cache))]
            except  :
                pass
        try:
            res=self.translate(contentsolved)
            self._cache[langkey][contentsolved] = res
        except:
            print_exc()
            res=''
        return res
    def fythread(self):
        while True:  
            t=time.time()
            if self.typename not in ['jbj7','kingsoft','dreye','rengong','premt','rengong_vnr','rengong_msk'] and t-self.lastrequeststime <globalconfig['transtimeinternal']:
                time.sleep(t-self.lastrequeststime)
            self.lastrequeststime=t
            while True:
                contentraw,(contentsolved,mp),skip=self.queue.get()
                self.newline=contentraw
                if self.queue.empty():
                    break
            
            if globalconfig['fanyi'][self.typename]['use']==False:
                 
                break
            if skip:
                continue
            
            try: 
                if self.typename in ['jbj7','kingsoft','dreye','rengong','premt','rengong_vnr','rengong_msk']:
                    res=self.translate(contentraw)
                else:
                    
                    res=self.cached_translate(contentsolved)
                    
            except:
                print_exc()
                try:
                    self.inittranslator()
                except:
                    print_exc()
                res=None 
                
            
            if res is not None  and self.queue.empty() and contentraw==self.newline:
                self.show(contentraw,(self.typename,res,mp))

    

            
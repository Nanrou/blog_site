# Python168的学习笔记7

## 多线程

关于多线程操作。

对于IO操作，如访问网站，写入磁盘这种需要时间等待响应的操作，多个cpu也几乎不能提高效率。

对于CPU密集型操作，如这个格式转换，可以通过多个cpu同时去进行。

但是对于python来讲，python存在GIL全局解释器的锁，导致只有一个python线程能被解释器接收。所以等于python只能对IO操作使用线程操作。

```python
import csv
from xml.etree.ElementTree import Element,ElementTree
import requests
from StringIO import StringIO
from test_retractxml import pretty

def download(url):
    # IO操作很慢，因为不能直接得到数据。如这步：是发送请求，等待数据，在等待的过程中让出CPU，自己睡眠。
    response = requests.get(url,timeout=3)
    if response.ok:
        return StringIO(response.content)

def csvToxml(scsv,fxml):
    # 这是CPU密集型操作，多个CPU可以同时操作
    reader = csv.reader(scsv)
    headers = reader.next()
    headers = map(lambda h:h.replace(' ',''),headers)
    
    root = Element('Data')
    for row in reader:
        eRow = Element('Row')
        root.append(eRow)
        for tag,text in zip(headers,row):
            e = Element(tag)
            e.text = text
            eRow.append(e)
            
    pretty(root)
    et = ElementTree(root)
    et.write(fxml)
    
    
def handle(sid):
    print 'Download ...(%d)' % sid
    url = 'http://table.finance.yahoo.com/table.csv?s=%s.sz'
    url %= str(sid).rjust(6,'0')
    rf = download(url)
    if rf is None:return
    
    print 'Convert to XML...(%d)' % sid
    fname = str(sid).rjust(6,'0')+'.xml'
    with open(fname,'wb') as wf:
        csvToxml(rf, wf)
        
from threading import Thread

'''
t = Thread(target=handle,args=(1,))
t.start()

print 'main thread'
'''
class MyThread(Thread):
    def __init__(self,sid):
        Thread.__init__(self)
        self.sid = sid
        
    def run(self):
        handle(self.sid)

threads = []
for i in xrange(1,11):
    t = MyThread(i)
    threads.append(t)
    t.start()
    
for t in threads:
    t.join()
    
print 'main thread'
# t.join()#阻塞函数，保证主线程在所有子线程结束后再退出


'''
    #这是串行的方法
    for sid in xrange(1,11):
        print 'Download ...(%d)' % sid
        url = 'http://table.finance.yahoo.com/table.csv?s=%s.sz'
        url %= str(sid).rjust(6,'0')
        rf = download(url)
        if rf is None:continue
        
        print 'Convert to XML...(%d)' % sid
        fname = str(sid).rjust(6,'0')+'.xml'
        with open(fname,'wb') as wf:
            csvToxml(rf, wf)
'''
```

线程间通信，可以用全局变量，但是不够安全，可以用Queue.Queue来存储通信内容。Queue作为线程安全的队列。

```python
import requests
import csv
from xml.etree.ElementTree import Element,ElementTree
from test_retractxml import pretty
from threading import Thread
from StringIO import StringIO

from Queue import Queue


class DownloadThread(Thread):
    
    def __init__(self,sid,queue):
        Thread.__init__(self)
        self.sid = sid
        self.url = 'http://table.finance.yahoo.com/table.csv?s=%s.sz'
        self.url %=str(sid).rjust(6,'0')
        self.queue = queue
    
    def download(self,url):
        response = requests.get(url,timeout=3)
        if response.ok:
            return StringIO(response.content)
        
    def run(self):
        print'download',self.sid
        data = self.download(self.url)
        self.queue.put((self.sid,data))
        
            
class ConverThread(Thread):
    def __init__(self,queue):
        Thread.__init__(self)
        self.queue = queue
        
    def csvToxml(self,rf,wf):
        reader = csv.reader(rf)
        headers = reader.next()
        headers = map(lambda h:h.replace(' ',''),headers)
        
        root = Element('Data')
        for row in reader:
            eRow = Element('Row')
            root.append(eRow)
            for tag,text in zip(headers,row):
                e = Element(tag)
                e.text = text
                eRow.append(e)
                
        pretty(root)
        et = ElementTree(root)
        et.write(wf)
        
    def run(self): 
        while True:
            sid,data = self.queue.get()
            print 'Convert', sid
            if sid  == -1:
                break
            if data:
                fname = str(sid).rjust(6,'0')+'.xml'
                with open(fname,'wb') as wf:
                    self.csvToxml(data, wf)        



q = Queue()
dThreads = [DownloadThread(i,q) for i in xrange(1,11)]
cThread = ConverThread(q)

for t in dThreads:  # 多个线程下载
    t.start()
    
cThread.start()  # 一个线程处理

for t in dThreads:
    t.join()

q.put((-1,None))
```

由于全局锁GIL的存在，无法用多个线程来对cpu密集操作，所以此例子中做的事情是：1，用多个线程来进行IO操作；2，将所有下载的内容传给1个线程进行转换。他们之间的交换是通过存入Queue这个安全队列里面。

 

而进程之间的的事件通知，需要调用thread库里的Event。事件的等待是Event.wait()，事件的响应是Event.set()，需要注意的是，set之后事件就不会再wait，需要Event.clear()来重新激活wait。要把等待，响应的逻辑弄清楚。

这节还引入了守护线程Daemon的概念，当其值为True时 ，其他线程结束时，自身也会结束。

```python
class DownloadThread(Thread):
	****

class ConverThread(Thread):
    def __init__(self,queue,cEvent,tEvent):
        Thread.__init__(self)
        self.queue = queue
        self.cEvent = cEvent
        self.tEvent = tEvent        
        
    def csvToxml(self,rf,wf):
      　　 ****

def run(self): 
        count = 0
        while True:
            sid,data = self.queue.get()
            print 'Convert', sid
            if sid  == -1:
                self.cEvent.set()
                self.tEvent.wait()
                break
            if data:
                fname = str(sid).rjust(6,'0')+'.xml'
                with open(fname,'wb') as wf:
                    self.csvToxml(data, wf)        
                count += 1
                if count == 5:  # 注意这里的逻辑
                    self.cEvent.set()  # 激活cEvent，表示转换完成
                    
                    self.tEvent.wait()  # 等待tEvent事件完成
                    self.tEvent.clear()  # 重新激活tEevent
                    count = 0
import tarfile
import os

class TarThread(Thread):
    def __init__(self,cEvent,tEvent):
        Thread.__init__(self)
        self.count = 0
        self.cEvent = cEvent
        self.tEvent = tEvent
        self.setDaemon(True)  # 守护线程，其他线程退出后，他也退出
        
    def tarXML(self):
        self.count += 1
        tfname = '%d.tgz'%self.count
        tf = tarfile.open(tfname,'w:gz')  # 打包命令，打包格式为gz
        for fname in os.listdir('.'):  # 遍历当前文件夹的文件
            if fname.endswith('.xml'):  # 找到.xml结尾的文件
                tf.add(fname)  # 添加到压缩包中
                os.remove(fname)  # 删除掉已添加的文件
        tf.close()
        
        if not tf.members:  # 如果打包文件为空，则删除
            os.remove(tfname)
            
    def run(self):
        while True:
            self.cEvent.wait()  # 等待cEvent事件
            self.tarXML()
            self.cEvent.clear()  # 重新激活等待
            
            self.tEvent.set()  # 激活tEvent，表示完成打包
            
            
if __name__ == '__main__':
    q = Queue()
    dThreads =[DownloadThread(i,q) for i in xrange(1,11)]
    
    cEvent = Event()
    tEvent = Event()
    
    cThread = ConverThread(q,cEvent,tEvent)
    tThread = TarThread(cEvent,tEvent)
    tThread.start()  # 注意这里要start线程
    
    for t in dThreads:
        t.start()
    cThread.start()
    
    for t in dThreads:
        t.join()
        
    q.put((-1,None))
    print 'main thread'
```


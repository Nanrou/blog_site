import os
import time
import random
import asyncio
from asyncio import Queue

import requests

URI = 'http://lab.crossincode.com/proxy/get/?num=10'


def get_proies():
    proxy_list = []
    resp = requests.get(URI, timeout=5)
    for item in resp.json()['proxies']:
        proxy_list.append(item['http'])
    return proxy_list


class AsyncFakeRequest(object):

    def __init__(self, proxy_list, max_tasks=5, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop
        self._q = Queue(loop=self._loop)
        self._max_tasks = max_tasks
        
        for proxy in proxy_list:
            self._q.put_nowait(proxy)

    async def crawl(self):  # 生产工人
        workers = [asyncio.Task(self.work(), loop=self._loop)
                   for _ in range(self._max_tasks)]
        await self._q.join()
        for w in workers:
            w.cancel()

    async def work(self):
        try:
            while True:
                proxy = await self._q.get()
                await self.worker(proxy)
                self._q.task_done()
        except asyncio.CancelledError:
            pass

    async def worker(self, proxy):
        uris = ['http://m.superxiaoshuo.com/']
        for _ in range(random.randint(1, 3)):  # 随机书
            info_num = str(random.randint(1,20))
            uris.append('http://m.superxiaoshuo.com/info/{}/'.format(info_num))
            for _ in range(random.randint(5, 10)):  # 随机章节
                uris.append('http://m.superxiaoshuo.com/book/{info_num}/{chapter}'.format(
                    info_num=info_num, chapter=info_num + '0' + str(random.randint(1, 800))))
        for uri in uris:
            # await asyncio.sleep(random.randint(10, 30))
            cmd = 'phantomjs.exe --output-encoding=gb2312 --proxy={proxy} req.js {uri}'.format(uri=uri, proxy=proxy)
            print(cmd)
            await os.system(cmd)
        # await asyncio.sleep(5)
    
if __name__ == '__main__':
    proxy_list = get_proies()
    # proxy_list = ['127.0.0.1:80', '111.13.109.27:80']
    loop = asyncio.get_event_loop()
    dd = AsyncFakeRequest(proxy_list, loop=loop)
    loop.run_until_complete(dd.crawl())
    loop.close()

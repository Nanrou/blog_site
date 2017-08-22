# -*- coding:utf-8 -*-

import requests
from lxml import etree


# from crawler.my_crawler import XpathCrawler


Info_RULE = {
    'uri': '//div[@class="postTitle"]/a/@href'
}

DETAIL_RULE = {
    'title': '//h1[@class="postTitle"]/a/text()',
    'content': '//div[@id="cnblogs_post_body"]',
    'timestamp': '//div[@class="postDesc"]/span/text()',
}


def get_all_uri():
    for i in range(1, 6):
        uri = 'http://www.cnblogs.com/nanrou/default.html?page={}'.format(i)
        resp = requests.get(uri)
        body = etree.HTML(resp.text)
        uris = body.xpath(Info_RULE['uri'])
        with open('info_uri', 'a') as af:
            af.write('\n'.join(uris))


if __name__ == '__main__':
    get_all_uri()

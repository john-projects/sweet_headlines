#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Maoyong
# Time: 2018/8/14 16:52
# description:
import sys
sys.path.append("/john/dreams/sweet_headlines")
sys.path.append(r"C:\Users\66439\Desktop\dreams\sweet_headlines")
from spiders.tx_spider.tx_spider import TXSpider
from spiders.wy_spider.wy_spider import WYSpider
import asyncio


if __name__ == "__main__":
    import time
    start_time = time.time()
    loop = asyncio.get_event_loop()

    tx_url = "http://news.qq.com/"
    wy_url = "http://www.163.com/"

    tx_spider = TXSpider()
    wy_spider = WYSpider()

    tasks = [tx_spider.run(tx_url, loop), wy_spider.run(wy_url, loop)]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
    print("Time:{}".format(time.time()-start_time))

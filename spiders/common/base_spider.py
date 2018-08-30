"""
@author: my
@license: (C) Copyright 2013-2017
@time: 2018/6/28
@software: PyCharm
@desc:
"""
import requests
from bs4 import BeautifulSoup
import datetime
import uuid
import os
from app.init_server import get_logging, get_db_session
from app.model.news import NewsInfo, NewsText
import aiohttp


logging = get_logging("spider_base.log")


class BaseSpider(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4'
        }
        self.db_session = get_db_session()
        self.http_session = requests.session()

    def get_soup_html_old(self, url):
        try:
            result = self.http_session.get(url=url, headers=self.headers, timeout=5, stream=True)
            soup = BeautifulSoup(result.text, "html.parser")
        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError) as err:
            logging.warning(err)
            return False

        return soup

    async def get_soup_html(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                text = await resp.text(errors='ignore')
                soup = BeautifulSoup(text, "html.parser")
                return soup

    async def get_body_html(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                text = await resp.text(errors='ignore')
                return text

    async def save_img(self, img_url):
        """
        保存抓取的图片

        :param img_url:
        :return:
        """
        img_suffix = img_url.split(".")[-1]
        # 如果找到后缀不是图片后缀则设置为默认值 jpg
        if img_suffix.lower() not in ("jpg", "gif", "png"):
            img_suffix = "jpg"
        now_datetime = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        img_path = now_datetime.strftime("img/%Y%m/%d/")
        img_name = img_path + "111%s." % str(uuid.uuid4()).replace('-', '') + img_suffix

        if not os.path.exists(img_path):
            os.makedirs(img_path)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(img_url) as resp:
                    content = await resp.read()
                    if resp.status == 200:
                        with open(img_name, "wb") as fp:
                            fp.write(content)
                        return img_name
                    else:
                        return ""
        except Exception as err:
            return ""

    def get_news_introduction(self, news_text_p_list):
        """
        获取新闻简介：
            如果一个 P 标签内的内容不超过250个字符，则直接保存，如果超过，则取前240个字符，后面内容以 ... 代替
        :param news_text_p_list:
        :return:
        """
        if not news_text_p_list or not isinstance(news_text_p_list, list):
            return ''

        first_p = news_text_p_list[0]
        if 0 <= len(first_p) <= 250:
            if first_p.endswith("</p>"):
                return first_p

        first_p_list = first_p.split("</p>", 1)
        first_p = first_p_list[0][:240] + '...' + '</p>'
        return first_p

    def save_news(self, news_dict):
        news_info = NewsInfo(
            add_time=int(time.time()),
            news_time=int(time.time()),
            news_id=news_dict.get("news_id", ""),
            title=news_dict.get("title", ""),
            news_web_source=news_dict.get("news_web_source", ""),
            news_web_source_url=news_dict.get("news_url", ""),
            ep_source=news_dict.get("ep_source", ""),
            editor=news_dict.get("editor", ""),
            news_introduction=news_dict.get("news_introduction", ""),
        )

        news_text = NewsText(
            news_id=news_dict.get("news_id", ""),
            news_text=news_dict.get("news_text")
        )

        self.db_session.add(news_info)
        self.db_session.add(news_text)

    def commit(self):
        self.db_session.commit()


if __name__ == "__main__":
    import time, asyncio
    start_time = time.time()

    url = "https://news.163.com/18/0828/02/DQ8UHBO100018AOP.html"
    # url = "http://www.163.com/"
    wy_spider = BaseSpider()
    loop = asyncio.get_event_loop()
    tasks = [wy_spider.get_soup_html(url)]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    print("Time:{}".format(time.time()-start_time))

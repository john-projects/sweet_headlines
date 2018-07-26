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
import time
import uuid
import os
from app.init_server import get_logging, get_db_session, news_id_set
from app.model.news import NewsInfo, NewsText

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

    def get_soup_html(self, url):
        try:
            result = requests.get(url=url, headers=self.headers, timeout=5, stream=True)
            soup = BeautifulSoup(result.text, "html.parser")
        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError) as err:
            logging.warning(err)
            return False

        return soup

    def get_body_html(self, url):
        try:
            result = requests.get(url=url, headers=self.headers, timeout=5, stream=True)
            return result
        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError) as err:
            logging.warning(err)
            return False

    def save_img(self, img_url):
        """
        保存抓取的图片

        :param img_url:
        :return:
        """
        now_datetime = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        img_path = now_datetime.strftime("img/%Y%m/%d/")
        img_name = img_path + "%s.jpg" % str(uuid.uuid4()).replace('-', '')

        if not os.path.exists(img_path):
            os.makedirs(img_path)

        try:
            html_source = requests.get(url=img_url, headers=self.headers, timeout=5, stream=True)
        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError) as err:
            logging.warning(err)
            return ''

        if not html_source:
            return ''

        if html_source.status_code == 200:
            with open(img_name, "wb") as fp:
                fp.write(html_source.content)
            return img_name
        return ''

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

    # def _save_news(self, title, news_url, ep_source, editor, news_text):
    def save_news(self, news_dict):
        url_list = news_dict.get("news_url", "").split("/")
        if len(url_list) < 3:
            return

        if url_list[-3] == "a":
            news_id = url_list[-2] + url_list[-1].split(".")[0]
        elif url_list[-3] == "omn":
            news_id = url_list[-1].split(".")[0]
        else:
            return

        if news_id in news_id_set:
            return

        news_info = NewsInfo(
            add_time=int(time.time()),
            news_time=int(time.time()),
            news_id=news_id,
            title=news_dict.get("title", ""),
            news_web_source=news_dict.get("news_web_source", ""),
            news_web_source_url=news_dict.get("news_url", ""),
            ep_source=news_dict.get("ep_source", ""),
            editor=news_dict.get("editor", ""),
            news_introduction=news_dict.get("news_introduction", ""),
        )

        news_text = NewsText(
            news_id=news_id,
            news_text=news_dict.get("news_text")
        )

        self.db_session.add(news_info)
        self.db_session.add(news_text)

    def commit(self):
        self.db_session.commit()

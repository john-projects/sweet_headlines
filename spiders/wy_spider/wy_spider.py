#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Maoyong
# Time: 
# description:
import requests
import logging
import re
import datetime
import uuid
import os
from bs4 import BeautifulSoup


class WYSpider(object):
    def __init__(self):
        self.index_url = "http://www.163.com/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/48.0.2564.116 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4'
        }

    def _get_html_source(self, url):
        try:
            result = requests.get(url=url, headers=self.headers, timeout=5, stream=True)
            soup = BeautifulSoup(result.text, "html.parser")
        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError) as err:
            logging.warning(err)
            return False

        return soup

    def get_index_news(self):
        soup = self._get_html_source(url=self.index_url)
        if not soup:
            return
        yao_wen_news = soup.find("div", "yaowen_news")
        # print(yao_wen_news)
        news_url_li_list = yao_wen_news.find_all("li")
        # print(news_url_li_list)
        index_news_dict = {}

        for news_url_li in news_url_li_list:
            news_url = news_url_li.a.get("href")
            title = news_url_li.a.string
            url_info = re.search(r"http://news.163.com/(\d{2})/(\d{4})/(\d{2})/(\w*?).html", news_url)
            if url_info:
                index_news_dict[title] = news_url

        return index_news_dict

    def get_news_info(self, news_dict):

        if not isinstance(news_dict, dict):
            return

        for title, url in news_dict.items():
            print("Starting -- url: %s" % url)
            news_url = url
            news_info_soup = self._get_html_source(url)
            if not news_info_soup:
                continue
            news_info_div = news_info_soup.find("div", "post_content_main")
            news_title = str(news_info_div.h1)
            news_text_div = news_info_div.find("div", "post_text")
            news_text_div_p = news_text_div.find_all("p")
            news_text_p_list = []
            for news_text_p in news_text_div_p:
                attrs_dict = news_text_p.attrs
                if attrs_dict.get("class") == ['f_center']:
                    replace_str = re.search(r'src="(.*?)"', str(news_text_p))
                    if replace_str:
                        img_path = self._save_img(replace_str.group(1))
                        news_text_p = re.sub(replace_str.group(1), 'http://www.sweeth.cn/' + img_path, str(news_text_p))
                    news_text_p_list.append(news_text_p)
                    continue
                if news_text_p.string:
                    news_text_p_list.append(str(news_text_p))

            ep_source_div = news_text_div.find("div", "ep-source")
            if ep_source_div:
                ep_source_div_span = ep_source_div.find_all("span")
            if len(ep_source_div_span) == 2:
                ep_source = ep_source_div_span[0].text
                editor = ep_source_div_span[1].text
            else:
                ep_source = "My"
                editor = "My"

            self._save_news(title=news_title, news_url=news_url, ep_source=ep_source, editor=editor,
                            news_text=''.join(news_text_p_list))

    def _save_img(self, img_url):
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

    @staticmethod
    def _save_news(title, news_url, ep_source, editor, news_text):
        sql = 'INSERT INTO news_info (`timestamp`, `title`, `news_web_source`, `news_web_source_url`, `ep_source`, ' \
              '`editor`, `news_text`) VALUES (%s, %s, %s, %s, %s, %s, %s); '
        now_datetime = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        news_web_source = "WY"

        mysql.insert_one(sql, value=(now_datetime, title,  news_web_source, news_url, ep_source, editor, news_text))
        mysql.end()

    def run(self):
        index_news_dict = self.get_index_news()
        self.get_news_info(index_news_dict)


if __name__ == "__main__":
    wy_spider = WYSpider()
    wy_spider.run()
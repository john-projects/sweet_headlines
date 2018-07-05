# -*- coding:utf-8 -*-
# __author__: MaoYong
import requests
from bs4 import BeautifulSoup
import logging
import datetime
import re
import uuid
import os
import json
import sys
sys.path.append("/home/django_web/dream/")
from news_mysql_db import Mysql
# from dreams.news_mysql_db import Mysql


logging.basicConfig(level=logging.DEBUG,
                    format='%(thread)d %(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='tx_spider.log',
                    filemode='a')
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

mysql = Mysql()


class TXSpider(object):
    def __init__(self):
        self.index_url = "http://news.qq.com/"

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

        index_news_dict_list = []
        head_news = soup.find("div", "head")

        # 腾讯头条热点三条
        sub_hot_news = head_news.find(id="subHot")
        index_news_dict_list.append({
            "title": sub_hot_news.h2.a.string,
            "url": sub_hot_news.h2.a.get("href"),
        })
        sub_hot_news_div = sub_hot_news.find("div", "slist")
        sub_hot_news_div_li = sub_hot_news_div.find_all("li")
        for sub_hot_news_li in sub_hot_news_div_li:
            index_news_dict_list.append({
                "title": sub_hot_news_li.a.string,
                "url": sub_hot_news_li.a.get("href"),

            })

        # 其他头条
        news_em_list = head_news.find_all("em", "f14")
        for news_info_em in news_em_list:
            index_news_dict_list.append({
                "title": news_info_em.a.string,
                "url": news_info_em.a.get("href"),
            })

        return index_news_dict_list

    def get_news_info(self, news_dict_list):

        if not isinstance(news_dict_list, list):
            return

        for news_dict in news_dict_list:
            url = news_dict["url"]
            # title = news_dict["title"]

            print("Starting -- url: %s" % url)
            news_info_soup = self._get_html_source(url)
            if not news_info_soup:
                continue

            news_url_type_list = url.split("/")
            if news_url_type_list[3] == "a":

                news_info_dict = self._get_tx_news(news_info_soup)
            elif news_url_type_list[3] == "omn":
                news_id = news_url_type_list[4]
                api_url = 'http://openapi.inews.qq.com/getQQNewsNormalContent?id=%s&chlid=news_rss' \
                      '&refer=mobilewwwqqcom&ext_data=all&srcfrom=newsapp&callback=getNewsContentOnlyOutput' % news_id
                body = requests.get(api_url)
                if body.text == '{"ret":-1}':
                    news_info_soup = self._get_html_source(url)
                    news_info_dict = self._get_tx_omn_news(news_info_soup)
                else:
                    news_info_dict = self._get_tx_omn_news_js(body)
            else:
                return
            self._save_news(title=news_info_dict["title"], news_url=url,
                            ep_source=news_info_dict["news_source"], editor=news_info_dict["editor"],
                            news_text=''.join(news_info_dict["news_text_p_list"]))

    def _get_tx_news(self, news_info_soup):

        editor = news_info_soup.find(id="QQeditor").string
        news_info_div = news_info_soup.find("div", "qq_article")

        title_info = news_info_div.find("div", "hd")
        title = str(title_info.h1)
        news_type = title_info.find("span", "a_catalog").a.string
        try:
            news_source = title_info.find("span", "a_source").a.string
            news_source_url = title_info.find("span", "a_source").a.get("href")

        except AttributeError:
            news_source = title_info.find("span", "a_source").string
            news_source_url = ''

        news_text_div = news_info_div.find(id="Cnt-Main-Article-QQ")
        news_text_div_p = news_text_div.find_all("p")
        news_text_p_list = []
        for news_text_p in news_text_div_p:
            attrs_dict = news_text_p.attrs
            if attrs_dict.get("align") == 'center':
                replace_str = re.search(r'src="(.*?)"', str(news_text_p))
                if replace_str:
                    img_path = self._save_img(replace_str.group(1))
                    news_text_p = re.sub(replace_str.group(1), 'http://www.sweeth.cn/' + img_path, str(news_text_p))
                news_text_p_list.append(news_text_p)
                continue
            if news_text_p.string:
                news_text_p_list.append(str(news_text_p))

        return {
            "title": title,
            "editor": editor,
            "news_source": news_source,
            "news_source_url": news_source_url,
            "news_text_p_list": news_text_p_list,
            "news_type": news_type,
        }

    def _get_tx_omn_news(self, news_info_soup):
        news_info_div = news_info_soup.find("div", "LEFT")
        title = str(news_info_div.h1)

        news_text_div = news_info_div.find("div", "content-article")
        news_text_div_p = news_text_div.find_all("p")
        news_text_p_list = []
        for news_text_p in news_text_div_p:
            try:
                img_url = "http:" + news_text_p.img.get("src")
                img_name = self._save_img(img_url)
                img_path = 'http://www.sweeth.cn/' + img_name
                news_text_p = '<img src="%s">' % img_path
                news_text_p_list.append(news_text_p)
            except AttributeError:
                news_text_p_list.append(str(news_text_p))

        return {
            "title": title,
            "editor": '',
            "news_source": '',
            "news_source_url": '',
            "news_text_p_list": news_text_p_list,
            "news_type": '',
        }

    def _get_tx_omn_news_js(self, body):

        news_info_dict = json.loads(body.text)

        news_info_list = news_info_dict.get("content")
        if not news_info_list:
            return {}

        title = "<h1>%s</h1>" % news_info_dict.get("title")

        news_text_p_list = []
        for news_info_p_dict in news_info_list:
            if news_info_p_dict["type"] == 1:
                news_text_p_list.append("<p>%s</p>" % news_info_p_dict["value"])
            elif news_info_p_dict["type"] == 2:
                img_name = self._save_img(news_info_p_dict["value"])
                img_path = 'http://www.sweeth.cn/' + img_name
                news_text_p_list.append('<p><img alt src="%s"></p>' % img_path)

        return {
            "title": title,
            "editor": '',
            "news_source": '',
            "news_source_url": '',
            "news_text_p_list": news_text_p_list,
            "news_type": '',
        }

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
        news_web_source = "TX"

        mysql.insert_one(sql, value=(now_datetime, title,  news_web_source, news_url, ep_source, editor, news_text))
        mysql.end()

    def run(self):
        index_news_dict_list = self.get_index_news()
        # print(index_news_dict_list)
        # index_news_dict_list = [{'url': 'https://news.qq.com/a/20180404/027548.htm', 'title': '归去来兮――追忆天宫一号'}]
        # index_news_dict_list = [{'url': 'http://new.qq.com/omn/20180407A011ZP00', 'title': '朴槿惠一审被判24年 前总统是否已经穷途末路？'}]
        # index_news_dict_list = [{'url': 'https://news.qq.com/a/20180407/000499.htm', 'title': '朴槿惠一审被判24年 前总统是否已经穷途末路？'}]
        # index_news_dict_list = [{'url': 'http://new.qq.com/omn/20180407A01Q9Q00', 'title': '朴槿惠一审被判24年 前总统是否已经穷途末路？'}]

        self.get_news_info(index_news_dict_list)


if __name__ == "__main__":
    tx_spider = TXSpider()
    tx_spider.run()

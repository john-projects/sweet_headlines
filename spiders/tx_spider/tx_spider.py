# -*- coding:utf-8 -*-
# __author__: MaoYong
from spiders.common.base_spider import BaseSpider
import re
import json
import asyncio
from app.config.logging.default import get_logging


class TXSpider(BaseSpider):
    def __init__(self):
        super(TXSpider, self).__init__()
        self.omn_api_url = ('http://openapi.inews.qq.com/getQQNewsNormalContent?id={}&chlid=news_rss&refer='
                            'mobilewwwqqcom&ext_data=all&srcfrom=newsapp&callback=getNewsContentOnlyOutput')
        self.logging = get_logging(__name__)

    async def get_index_news(self, index_url):
        soup = await self.get_soup_html(url=index_url)
        if not soup:
            yield {}

        head_news = soup.find("div", "head")

        # 腾讯头条热点三条
        sub_hot_news = head_news.find(id="subHot")
        yield {
            "title": sub_hot_news.h2.a.string,
            "url": sub_hot_news.h2.a.get("href"),
        }
        sub_hot_news_div = sub_hot_news.find("div", "slist")
        sub_hot_news_div_li = sub_hot_news_div.find_all("li")
        for sub_hot_news_li in sub_hot_news_div_li:
            yield {
                "title": sub_hot_news_li.a.string,
                "url": sub_hot_news_li.a.get("href"),
            }

        # 其他头条
        news_em_list = head_news.find_all("em", "f14")
        for news_info_em in news_em_list:
            yield {
                "title": news_info_em.a.string,
                "url": news_info_em.a.get("href"),
            }

    async def get_news_info(self, news_dict):
        url = news_dict["url"]

        # 如果news已在数据库中存在，则排除掉此条url
        news_id = self.get_news_id(url)
        if not news_id:
            return

        self.logging.info("Starting -- url: %s" % url)
        news_info_soup = await self.get_soup_html(url)
        if not news_info_soup:
            return

        # 腾讯头条新闻有两种类型网页提供，分别做处理
        news_url_type_list = url.split("/")

        # url中带 "a" 的页面
        if news_url_type_list[3] == "a":
            news_info_dict = await self._get_a_news(news_info_soup)

        # url中带 "omn" 的页面
        # 形如：https://new.qq.com/omn/20180814/20180814A0L1IG.html
        elif news_url_type_list[3] == "omn":
            body = await self.get_body_html(self.omn_api_url.format(news_id))

            # "omn" 页面分两种，一种为网页形式，一种为 JS 形式
            # 处理网页新闻
            if body == '{"ret":-1}':
                news_info_soup = await self.get_soup_html(url)
                news_info_dict = await self._get_omn_news(news_info_soup)
            # 处理 JS 返回
            else:
                news_info_dict = await self._get_omn_news_js(body)
        else:
            return

        if not news_info_dict:
            return

        save_dict = {
            "title": news_info_dict["title"],
            "news_url": url,
            "news_id": news_id,
            "ep_source": news_info_dict["news_source"],
            "editor": news_info_dict["editor"],
            "news_introduction": self.get_news_introduction(news_info_dict["news_text_p_list"]),
            "news_text": ''.join(news_info_dict["news_text_p_list"]),
            "news_web_source": "TX"

        }
        self.save_news(save_dict)

    async def _get_a_news(self, news_info_soup):

        # 获取编辑者
        try:
            editor = news_info_soup.find(id="QQeditor").string
        except AttributeError:
            return False

        news_info_div = news_info_soup.find("div", "qq_article")

        title_info = news_info_div.find("div", "hd")
        title = str(title_info.h1)
        try:
            news_type = title_info.find("span", "a_catalog").a.string
        except AttributeError:
            news_type = ""
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
                    img_url = "https:" + replace_str.group(1)
                    img_path = await self.save_img(img_url)
                    news_text_p = re.sub(replace_str.group(1), 'http://www.sweeth.cn/' + img_path, str(news_text_p))
                news_text_p_list.append(str(news_text_p))
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

    async def _get_omn_news(self, news_info_soup):
        news_info_div = news_info_soup.find("div", "LEFT")
        title = str(news_info_div.h1)

        news_text_div = news_info_div.find("div", "content-article")
        news_text_div_p = news_text_div.find_all("p")
        news_text_p_list = []
        for news_text_p in news_text_div_p:
            try:
                img_url = "http:" + news_text_p.img.get("src")
                img_name = await self.save_img(img_url)
                img_path = 'http://www.sweeth.cn/' + img_name
                news_text_p = '<img src="%s">' % img_path
                news_text_p_list.append(news_text_p)
            except AttributeError:
                news_text_p_list.append(str(news_text_p))

        if not news_text_p_list:
            return False

        return {
            "title": title,
            "editor": '',
            "news_source": '',
            "news_source_url": '',
            "news_text_p_list": news_text_p_list,
            "news_type": '',
        }

    async def _get_omn_news_js(self, body):

        news_info_dict = json.loads(body)

        news_info_list = news_info_dict.get("content")
        if not news_info_list:
            return {}

        title = "<h1>%s</h1>" % news_info_dict.get("title")

        news_text_p_list = []
        for news_info_p_dict in news_info_list:
            if news_info_p_dict["type"] == 1:
                news_text_p_list.append("<p>%s</p>" % news_info_p_dict["value"])
            elif news_info_p_dict["type"] == 2:
                img_name = await self.save_img(news_info_p_dict["value"])
                img_path = 'http://www.sweeth.cn/' + img_name
                news_text_p_list.append('<p><img alt src="%s"></p>' % img_path)

        if not news_text_p_list:
            return False

        return {
            "title": title,
            "editor": '',
            "news_source": '',
            "news_source_url": '',
            "news_text_p_list": news_text_p_list,
            "news_type": '',
        }

    def get_news_id(self, news_url):
        url_list = news_url.split("/")
        if len(url_list) < 3:
            return

        if url_list[-3] == "a":
            news_id = url_list[-2] + url_list[-1].split(".")[0]
        elif url_list[-3] == "omn":
            news_id = url_list[-1].split(".")[0]
        else:
            return

        if news_id in self.news_id_list:
            return

        return news_id

    async def run(self, index_url, loop):
        news_dict_list = []

        async for news_dict in self.get_index_news(index_url):
            news_dict_list.append(news_dict)
            self.logging.info(news_dict)

        tasks = [loop.create_task(self.get_news_info(news_dict)) for news_dict in news_dict_list]
        await asyncio.wait(tasks)

        self.commit()


if __name__ == "__main__":
    import time
    start_time = time.time()
    url = "http://get_news.qq.com/"
    tx_spider = TXSpider()

    loop = asyncio.get_event_loop()
    tasks = [tx_spider.run(url, loop)]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    tx_spider.logging.info("Time:{}".format(time.time()-start_time))

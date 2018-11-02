#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Maoyong
# Time: 
# description:
import re
from spiders.common.base_spider import BaseSpider
import asyncio
from app.config.logging.default import get_logging


class WYSpider(BaseSpider):
    def __init__(self):
        super(WYSpider, self).__init__()
        self.logging = get_logging(__name__)

    async def get_index_news(self, index_url):
        soup = await self.get_soup_html(url=index_url)
        if not soup:
            yield {}

        yao_wen_news = soup.find("div", "news_default_yw")
        news_url_li_list = yao_wen_news.find_all("li")
        for news_url_li in news_url_li_list:
            news_url = news_url_li.a.get("href")
            title = news_url_li.a.string
            yield {
                "title": title,
                "url": news_url,
            }

    async def get_news_info(self, news_dict):
        url = news_dict["url"]

        # 如果news已在数据库中存在，则排除掉此条url
        news_id = self.get_news_id(url)
        if not news_id:
            return

        self.logging.info("Starting -- url: %s" % news_dict["url"])
        news_info_soup = await self.get_soup_html(url)
        if not news_info_soup:
            return

        news_info_div = news_info_soup.find("div", "post_content_main")
        news_title = str(news_info_div.h1)
        news_text_div = news_info_div.find("div", "post_text")
        news_text_div_p = news_text_div.find_all("p")
        news_text_p_list = []
        for news_text_p in news_text_div_p:
            attrs_dict = news_text_p.attrs
            if attrs_dict.get("class") == ['f_center']:
                replace_str = re.search(r' src="(.*?)"', str(news_text_p))
                if replace_str:
                    img_url = replace_str.group(1)
                    img_name = await self.save_img(img_url)
                    img_path = 'http://www.sweeth.cn/' + img_name
                    news_text_p = re.sub(replace_str.group(1), img_path, str(news_text_p))
                news_text_p_list.append(str(news_text_p))
                continue
            if news_text_p.string:
                news_text_p_list.append(str(news_text_p))

        ep_source_div = news_text_div.find("div", "ep-source")
        ep_source = "My"
        editor = "My"
        if ep_source_div:
            ep_source_div_span = ep_source_div.find_all("span")
            if len(ep_source_div_span) == 2:
                ep_source = ep_source_div_span[0].text
                editor = ep_source_div_span[1].text

        save_dict = {
            "title": news_title,
            "news_url": url,
            "news_id": news_id,
            "ep_source": ep_source,
            "editor": editor,
            "news_introduction": self.get_news_introduction(news_text_p_list),
            "news_text": ''.join(news_text_p_list),
            "news_web_source": "WY"

        }
        self.save_news(save_dict)

    def get_news_id(self, news_url):
        url_list = news_url.split("/")
        if len(url_list) != 7:
            return

        news_id = url_list[-1].split(".")[0]
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

    url = "http://www.163.com/"
    wy_spider = WYSpider()

    loop = asyncio.get_event_loop()
    tasks = [wy_spider.run(url, loop)]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    wy_spider.logging.info("Time:{}".format(time.time()-start_time))

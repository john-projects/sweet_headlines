# -*- coding: utf-8 -*-
"""
File Name   :GetNewsListService
Author      :MaoYong
date：      :2018/11/1 11:55
Description :获取新闻列表
"""

from app.service.base.BaseService import BaseService
from app.model.news import NewsInfo


class GetNewsListService(BaseService):
    def get_news_list(self, db_session, news_type, page, limit):
        try:
            if 0 < int(limit) < 50:
                limit = 10
        except TypeError:
            limit = 10

        try:
            page = int(page)
        except TypeError:
            page = 1

        news_info_obj_list = db_session.query(
            NewsInfo.news_id,
            NewsInfo.news_time,
            NewsInfo.title,
            NewsInfo.news_web_source,
            NewsInfo.news_web_source_url,
            NewsInfo.ep_source,
            NewsInfo.editor,
            NewsInfo.news_introduction,
        ).filter(NewsInfo.news_web_source == news_type).order_by(-NewsInfo.add_time)[(page-1)*limit:page*limit]

        news_info_list = list()
        for news_info in news_info_obj_list:
            news_info_dict = dict()
            for i in range(len(news_info.keys())):
                news_info_dict[news_info.keys()[i]] = news_info[i]

            news_info_list.append(news_info_dict)
        return news_info_list


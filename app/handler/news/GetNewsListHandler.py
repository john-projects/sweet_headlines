# -*- coding: utf-8 -*-
"""
File Name   :GetNewsListHandler
Author      :MaoYong
date：      :2018/11/1 11:08
Description :获取腾讯新闻
"""
from app.handler.base.BaseHander import BaseHander
from app.service.news.GetNewsListService import GetNewsListService


class GetNewsListHandler(BaseHander):
    def get(self):
        # 新闻类型
        news_type = self.get_argument('news_type', '')
        # 页码
        page = self.get_argument('page', 1)
        # 限制条数
        limit = self.get_argument('limit', 10)

        news_info_list = GetNewsListService().get_news_list(self.db_session, news_type, page, limit)
        self.render_data(info=news_info_list)


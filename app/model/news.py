"""
@author: my
@license: (C) Copyright 2013-2017
@time: 2018/6/28
@software: PyCharm
@desc:
"""

from sqlalchemy import Column
from sqlalchemy.types import Integer, String, Text
from app.init_server import BaseModel


class NewsInfo(BaseModel):
    __tablename__ = 'news_info'

    id = Column(Integer, primary_key=True, doc=u"")
    add_time = Column(Integer, default=0, doc=u"爬取时间")
    news_time = Column(Integer, default=0, doc=u"新闻时间")
    news_id = Column(String(25), default=0, doc=u"新闻ID")
    title = Column(String(250), default='', doc=u"新闻标题")
    news_web_source = Column(String(20), default='', doc=u"新闻爬取来源网站")
    news_web_source_url = Column(String(255), default='', doc=u"新闻爬取来源网站网址")
    ep_source = Column(String(255), default='', doc=u"新闻初始来源网站")
    editor = Column(String(50), default='', doc=u"新闻编辑")
    news_introduction = Column(String(255), default='', doc=u"新闻简介")


class NewsText(BaseModel):
    __tablename__ = 'news_text'

    id = Column(Integer, primary_key=True, doc=u"")
    news_id = Column(Integer, default=0, doc=u"新闻对应ID")
    news_text = Column(Text, doc=u"新闻详情")


if __name__ == "__main__":
    pass
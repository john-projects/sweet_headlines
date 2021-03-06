# -*- coding: utf-8 -*-
"""
File Name   :init_server
Author      :MaoYong
date：      :2018/11/1 15:12
Description :
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.config import DefaultDbConfig as config


# 初始化mysql连接
SQL_CONFIG = {
    'pool_size': config.SQLALCHEMY_POOL_SIZE,
    'echo': config.SQLALCHEMY_ECHO,
    'pool_recycle': config.SQLALCHEMy_POOL_RECYLE,
    'connect_args': {'charset': 'utf8'},
    'convert_unicode': True,
    'encoding': 'utf-8',
}

engine = create_engine(config.SQLALCHEMY_DATABASE_URI, **SQL_CONFIG)


def get_db_session():
    return scoped_session(sessionmaker(bind=engine))


def get_news_id_set():
    db_session = get_db_session()
    from app.model.news import NewsInfo
    news_id_list = [news_info.news_id for news_info in db_session.query(NewsInfo.news_id).all()]
    return set(news_id_list)


# BaseModel = declarative_base()
# news_id_set = get_news_id_set()
# print(news_id_set)

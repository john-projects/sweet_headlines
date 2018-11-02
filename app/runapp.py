# -*- coding: utf-8 -*-
"""
File Name   :runapp.py
Author      :MaoYong
date：      :2018/11/1 11:03
Description :启动程序
"""
import tornado.web
import tornado.ioloop
from app.handler.news.GetNewsListHandler import GetNewsListHandler


def make_app():
    return tornado.web.Application([
        (r'/new/get_news_list', GetNewsListHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(5555)
    tornado.ioloop.IOLoop.current().start()

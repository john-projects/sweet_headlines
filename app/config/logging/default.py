#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Maoyong
# Time: 2018/9/3 17:01
# description:
import logging
import os
import datetime


spider_path = "/john/dreams/sweet_headlines/"
if not os.path.exists(spider_path):
    spider_path = os.getcwd()

logging_path = spider_path+"/spider_log"
if not os.path.exists(logging_path):
    os.makedirs(logging_path)


def get_logging(filename):
    logging.basicConfig(level=logging.DEBUG,
                        format='%(thread)d %(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=logging_path+'/'+filename,
                        filemode='a')
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return logging


def get_img_path():
    now_datetime = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    img_path = now_datetime.strftime(spider_path + "/img/%Y%m/%d/")

    return img_path
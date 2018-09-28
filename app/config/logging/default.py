#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Maoyong
# Time: 2018/9/3 17:01
# description:
import logging
import os


current_path = os.getcwd()

spider_path = current_path+"/spider_log"
if not os.path.exists(spider_path):
    os.makedirs(spider_path)


def get_logging(filename):
    logging.basicConfig(level=logging.DEBUG,
                        format='%(thread)d %(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=spider_path+'/'+filename,
                        filemode='a')
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return logging

"""
@author: my
@license: (C) Copyright 2013-2017
@time: 2018/6/28
@software: PyCharm
@desc:
"""


class DefaultDbConfig(object):
    # mysql recyle
    SQLALCHEMy_POOL_RECYLE = 3600
    # mysql 链接池
    SQLALCHEMY_POOL_SIZE = 5
    SQLALCHEMY_ECHO = False
    # 本地连接测试数据库
    SQLALCHEMY_DATABASE_URI = "mysql://root:Mao664390905@127.0.0.1/news?charset=utf8"
    # SQLALCHEMY_DATABASE_URI = "mysql://root:Mao664390905@192.168.33.10/news?charset=utf8"

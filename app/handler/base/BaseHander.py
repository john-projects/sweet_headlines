"""
@author: my
@license: (C) Copyright 2013-2017
@time: 2018/6/28
@software: PyCharm
@desc:
"""
import tornado.web


class BaseHander(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super(BaseHander, self).__init__(*args, **kwargs)
        self.db_session = self.get_db_session()

    @staticmethod
    def get_db_session():
        from app.init_server.init_server import get_db_session
        return get_db_session()

    def render_data(self, code=0, info=None, msg='ok'):
        response_dict = dict()
        response_dict['code'] = code
        response_dict['msg'] = msg
        response_dict['info'] = info
        self.write(response_dict)
        self.finish()

    def on_finish(self):
        if self.db_session:
            self.db_session.close()

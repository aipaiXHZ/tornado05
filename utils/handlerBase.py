import tornado.web
from tornado.concurrent import dummy_executor

from pycket.session import SessionMixin

from dbs.connect import Session

class HandlerBase(tornado.web.RequestHandler,SessionMixin):
    executor = dummy_executor

    def get_current_user(self):
        return self.session.get('user', None)
    def initialize(self):
        self.db=Session()
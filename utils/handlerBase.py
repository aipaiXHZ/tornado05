import tornado.web
from pycket.session import SessionMixin

from dbs.connect import Session

class HandlerBase(tornado.web.RequestHandler,SessionMixin):
    def get_current_user(self):
        return self.session.get('user', None)
    def initialize(self):
        self.db=Session()
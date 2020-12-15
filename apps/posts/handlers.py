import tornado.web

from utils.handlerBase import HandlerBase

class IndexHandler(HandlerBase):
    @tornado.web.authenticated
    async def get(self):
        await self.render('posts/index.html')
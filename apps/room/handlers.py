import tornado.web
import tornado.websocket
import tornado.escape
from tornado.concurrent import run_on_executor
from tornado.ioloop import IOLoop
from tornado.gen import coroutine
from tornado.httpclient import AsyncHTTPClient

from utils.handlerBase import HandlerBase
from apps.users.models import Users
from apps.posts.models import Posts

import uuid
import json
from uuid import uuid4
from PIL import Image
from datetime import datetime

class RoomHandler(HandlerBase):
    @run_on_executor
    def get_messages(self):
        messages = []
        keys = self.application.redis.keys()
        for key in keys:
            try:
                messages.append(json.loads(self.application.redis.get(key)))
            except:
                pass
        for i in range(len(messages)):
            messages[i]['created'] = datetime.strptime(messages[i]['created'], '%Y-%m-%d %H:%M:%S.%f')
        for j in range(len(messages) - 1, 0, -1):
            for i in range(j):
                if messages[i]['created'] > messages[i + 1]['created']:
                    messages[i], messages[i + 1] = messages[i + 1], messages[i]
        return messages

    @tornado.web.authenticated
    async def get(self):
        messages = await self.get_messages()
        await self.render('room/room.html',messages=messages)

class AsyncSaveHandler(HandlerBase):
    @coroutine
    def get(self):
        save_url=self.get_argument('save_url','')
        username=self.get_argument('name','')
        user=self.db.query(Users).filter_by(is_deleted=False,username=username).first()
        client=AsyncHTTPClient()
        resp=yield client.fetch(save_url,request_timeout=180)
        name = uuid4().hex + '.jpg'
        thrumb_name = 'thrumb_{}'.format(name)
        save_path = 'static/files/{}'.format(name)
        with open(save_path, 'wb') as f:
            f.write(resp.body)
        im = Image.open(save_path)
        im.thumbnail((200, 200))
        im.save('static/files/thrumb/thrumb_{}'.format(name), 'JPEG')
        try:
            post = Posts(image_url='files/{}'.format(name),thrumb_url='files/thrumb/thrumb_{}'.format(name),user=user)
            self.db.add(post)
            self.db.commit()
            post_id = post.id
        except Exception as e:
            self.db.rollback()
            print(e)
            self.finish({'errmsg':'创建post数据失败'})
            return
        msg='user {} post:http://{}/post/{}'.format(username,self.request.host,post_id)
        chat = {
            'id': str(uuid.uuid1()),
            'body': msg,
            'username': username,
            'created':str(datetime.now()),
            'img_url':'files/thrumb/thrumb_{}'.format(name),
            'post_id':post_id
        }
        chat['html'] = tornado.escape.to_basestring(self.render_string
                                                    ('room/message.html', chat=chat))
        self.application.redis.set(chat['id'], json.dumps(chat),60)
        ChatWSHandler.history.append(chat)
        for w in ChatWSHandler.waiters:
            w.write_message(chat)

class ChatWSHandler(tornado.websocket.WebSocketHandler,HandlerBase):
    '''
    处理和响应Websocket连接
    '''
    waiters=set()
    history=[]
    def get_current_user(self):
        return self.session.get('user',None)
    @tornado.web.authenticated
    def open(self):
        ChatWSHandler.waiters.add(self)
        print('new ws connecttion:{}'.format(self))
        chat = {
            'id': str(uuid.uuid1()),
            'body': "%s进入教室"%self.current_user,
            'username': self.current_user,
            'img_url':None,
            'post_id':None
        }
        chat['html'] = tornado.escape.to_basestring(self.render_string
                                                    ('room/message.html', chat=chat))
        # self.application.redis.set(chat['id'],json.dumps(chat),300)
        for w in ChatWSHandler.waiters:
            w.write_message(chat)

    @tornado.web.authenticated
    def on_message(self, message):
        print('got message:{}'.format(message))
        # parsed=tornado.escape.json_decode(message)
        # msg=parsed['body']
        msg=message
        if msg.startswith('http://') or msg.startswith('https://'):
            client=AsyncHTTPClient()
            save_api_url='http://{}/save?save_url={}&name={}'.format(self.request.host,msg,
                                                                                 self.current_user)
            IOLoop.current().spawn_callback(client.fetch,
                                            save_api_url,
                                            request_timeout=180)
            reply_msg='user {},url={} is processing'.format(self.current_user,msg)
            chat = {
                'id': str(uuid.uuid1()),
                'body': reply_msg,
                'username': self.current_user,
                'created': str(datetime.now()),
                'img_url':None,
                'post_id': None
            }
            chat['html'] = tornado.escape.to_basestring(self.render_string('room/message.html', chat=chat))
            self.application.redis.set(chat['id'], json.dumps(chat),120)
            ChatWSHandler.history.append(chat)
            for w in ChatWSHandler.waiters:
                w.write_message(chat)
        else:
            chat={
                'id':str(uuid.uuid1()),
                'body':msg,
                'username':self.current_user,
                'created': str(datetime.now()),
                'img_url':None,
                'post_id': None
            }
            chat['html']=tornado.escape.to_basestring(self.render_string
            ('room/message.html',chat=chat))
            self.application.redis.set(chat['id'], json.dumps(chat),120)
            ChatWSHandler.history.append(chat)
            for w in ChatWSHandler.waiters:
                w.write_message(chat)

    @tornado.web.authenticated
    def on_close(self):#客户端断开连接时触发这个，当然了，我们也可以在js里用代码ws.close()去主动关闭连接
        ChatWSHandler.waiters.remove(self)
        print('cloce ws connecttion:{}'.format(self))
        chat = {
            'id': str(uuid.uuid1()),
            'body': "%s退出教室" % self.current_user,
            'username': self.current_user,
            'img_url': None,
            'post_id': None
        }
        chat['html'] = tornado.escape.to_basestring(self.render_string
                                                    ('room/message.html', chat=chat))
        # self.application.redis.set(chat['id'], json.dumps(chat), 300)
        for w in ChatWSHandler.waiters:
            w.write_message(chat)
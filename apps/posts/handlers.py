import tornado.web
from tornado.concurrent import run_on_executor
from sqlalchemy_pagination import paginate
from sqlalchemy import desc

import os
import logging
from uuid import uuid4
from PIL import Image

from apps.users.models import Users
from apps.posts.models import Posts
from utils.handlerBase import HandlerBase

class IndexHandler(HandlerBase):
    @tornado.web.authenticated
    async def get(self):
        user=self.db.query(Users).filter(Users.is_deleted==False,Users.username==self.current_user).first()
        posts=self.db.query(Posts).filter(Posts.is_deleted==False,Posts.user==user).order_by(desc(Posts.update_time),desc(Posts.id))
        await self.render('posts/index.html',posts=posts)

class UploadHandler(HandlerBase):
    @tornado.web.authenticated
    async def get(self):
        self.render('posts/upload.html')
    async def post(self):
        file_metas = self.request.files.get('file', [])
        for meta in file_metas:
            file_name = meta['filename']
            name=await self.file_save(file_name,meta['body'])
            user = self.db.query(Users).filter_by(username=self.current_user).first()
            try:
                post = Posts(image_url='files/{}'.format(name), thrumb_url=
                'files/thrumb/thrumb_{}'.format(name), user=user)
                self.db.add(post)
                self.db.commit()
                post_id = post.id
            except Exception as e:
                self.db.rollback()
                logging.info(e)
                self.finish({'errmsg': '创建post数据失败'})
                return
            self.redirect('/post/{}'.format(post_id))
    @run_on_executor
    def file_save(self,file_name,content):
        _, ext = os.path.splitext(file_name)
        name = uuid4().hex + ext
        with open('static/files/{}'.format(name), 'wb') as f:
            f.write(content)
        im = Image.open('static/files/{}'.format(name))
        im.thumbnail((200, 200))
        ext = ext.split('.')[-1]
        if ext in ['jpg', 'jpeg']:
            ext = 'JPEG'
        im.save('static/files/thrumb/thrumb_{}'.format(name), ext)
        return name

class PostsHandler(HandlerBase):
    async def get(self,id):
        post=self.db.query(Posts).filter(Posts.id==id,Posts.is_deleted==False).first()
        if not post:
            await self.render('404.html')
        await self.render('posts/post.html',post=post)

class ExploreHandler(HandlerBase):
    async def get(self):
        page=self.get_argument('page','1').strip()
        if not page:
            page=1
        try:
            page=int(page)
        except:
            page=1
        number = self.get_argument('number', '3').strip()
        if not number:
            number=3
        try:
            number=int(number)
        except:
            number=3
        posts=self.db.query(Posts).filter(Posts.is_deleted==False).order_by(desc(Posts.update_time),desc(Posts.id))
        try:
            pg = paginate(posts, page, number)
        except:
            pg = paginate(posts, 1, 3)
        await self.render('posts/explore.html',posts=pg.items,number=number,pg=pg,page_number=int(page))

class ProfileHandler(HandlerBase):
    @tornado.web.authenticated
    async def get(self):
        user=self.db.query(Users).filter(Users.is_deleted==False,Users.username==self.current_user).first()
        posts=self.db.query(Posts).filter(Posts.is_deleted==False,Posts.user==user).order_by(desc(Posts.update_time),desc(Posts.id))
        name = self.get_query_argument('name', '').strip()
        if name:
            user = self.db.query(Users).filter(Users.is_deleted == False, Users.username == name).first()
            posts = self.db.query(Posts).filter(Posts.is_deleted == False, Posts.user == user).order_by(
                desc(Posts.update_time), desc(Posts.id))
        else:
            name=self.current_user
        await self.render('posts/profile.html',posts=posts,name=name)
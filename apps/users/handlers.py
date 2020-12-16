import tornado.web

from apps.users.models import Users
from utils.handlerBase import HandlerBase

import re
import logging

class LoginHandler(HandlerBase):
    async def get(self):
        msg=self.get_query_argument('msg','').strip()
        await self.render('users/login.html',msg=msg)
    async def post(self):
        next=self.get_query_argument('next',None)
        username=self.get_body_argument('username','').strip()
        if not username:
            if next:
                self.redirect('/login?next=%s&msg=用户名不能为空'%next)
                return
            else:
                self.redirect('/login?msg=用户名不能为空')
                return
        if not re.match('^\w{5,20}$',username):
            if next:
                self.redirect('/login?next=%s&msg=请输入5-20个字符的用户名'%next)
                return
            else:
                self.redirect('/login?msg=请输入5-20个字符的用户名')
                return
        if not self.db.query(Users).filter(Users.username==username,Users.is_deleted==False).first():
            if next:
                self.redirect('/login?next=%s&msg=用户不存在'%next)
                return
            else:
                self.redirect('/login?msg=用户不存在')
                return
        password=self.get_body_argument('password','').strip()
        if not password:
            if next:
                self.redirect('/login?next=%s&msg=密码不能为空'%next)
                return
            else:
                self.redirect('/login?msg=密码不能为空')
                return
        if len(password) < 6 or len(password) > 20:
            if next:
                self.redirect('/login?next=%s&msg=密码的长度需在6～20位以内'%next)
                return
            else:
                self.redirect('/login?msg=密码的长度需在6～20位以内')
                return
        user=self.db.query(Users).filter(Users.username==username,Users.is_deleted==False).first()
        if password != user.password:
            if next:
                self.redirect('/login?next=%s&msg=密码错误'%next)
                return
            else:
                self.redirect('/login?msg=密码错误')
                return
        self.session.set('user',username)
        if next:
            self.redirect(next)
        else:
            self.redirect('/')

class LogoutHandler(HandlerBase):
    async def get(self):
        self.session.delete('user')
        self.redirect('/login')

class RegisterHandler(HandlerBase):
    async def get(self):
        msg=self.get_query_argument('msg','').strip()
        await self.render('users/register.html',msg=msg)
    async def post(self):
        username=self.get_body_argument('username','').strip()
        if not username:
            self.redirect('/register?msg=用户名不能为空')
            return
        if not re.match('^\w{5,20}$', username):
            self.redirect('/register?msg=请输入5-20个字符的用户名')
            return
        if self.db.query(Users).filter(Users.username==username,Users.is_deleted==False).first():
            self.redirect('/register?msg=用户已存在')
            return
        password=self.get_body_argument('password','').strip()
        if not password:
            self.redirect('/register?msg=密码不能为空')
            return
        if len(password) < 6 or len(password) > 20:
            self.redirect('/register?msg=密码的长度需在6～20位以内')
            return
        password_repeat = self.get_body_argument('password2', '').strip()
        if not password_repeat:
            self.redirect('/register?msg=重复密码不能为空')
            return
        if len(password_repeat) < 6 or len(password_repeat) > 20:
            self.redirect('/register?msg=重复密码的长度需在6～20位以内')
            return
        if password!=password_repeat:
            self.redirect('/register?msg=密码和确认密码不一致')
            return
        try:
            user=Users(username=username,password=password)
            self.db.add(user)
            self.db.commit()
        except Exception as e:
            self.session.rollback()
            logging.info(e)
            await self.finish({'errmsg':'创建user数据失败'})
            return
        self.session.set('user',username)
        self.redirect('/')
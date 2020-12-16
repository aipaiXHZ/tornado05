from dbs.modelBase import ModelBase

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class Posts(ModelBase):
    __tablename__='tb_posts'
    image_url=Column(String(150),nullable=False)
    thrumb_url=Column(String(150),nullable=False)
    user_id=Column(Integer,ForeignKey('tb_users.id'))
    user=relationship('Users',backref='posts')

    def __repr__(self):
        return '<Posts-id:%s>'%self.id
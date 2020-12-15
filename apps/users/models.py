from dbs.modelBase import ModelBase

from sqlalchemy import Column,Integer,String,DateTime,Boolean

class Users(ModelBase):
    __tablename__='tb_users'
    username = Column(String(20), nullable=False, unique=True)
    password = Column(String(20), nullable=False)

    def __repr__(self):
        return '<Users-id:%s>'%self.id
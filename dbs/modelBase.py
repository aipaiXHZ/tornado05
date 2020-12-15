from .connect import Base

from sqlalchemy import Column,Integer,String,DateTime,Boolean

from datetime import datetime

class ModelBase(Base):
    __abstract__=True
    id = Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column(DateTime, default=datetime.now(), index=True)
    update_time = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    is_deleted = Column(Boolean, default=False)
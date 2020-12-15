#这些可以放在一个connect的py文件里
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
HOSTNAME='127.0.0.1'
PORT='3306'
DATABASE='tornado05'
USERNAME='admin'
PASSWORD='Root110qwe'
db_url='mysql+pymysql://{}:{}@{}/{}?charset=utf8'.format(
	USERNAME,
	PASSWORD,
	HOSTNAME,
	DATABASE
)
engine=create_engine(db_url)#第二个参数可以打印sql语句，你在pycharm里执行的sql语句，会在控制台打印出来
Base=declarative_base(engine)
Session=sessionmaker(engine)#创建数据库会话管理类
session=Session()#获取一个数据库会话
if __name__=='__main__':
	print(dir(Base))
	print(dir(session))
#生产环境配置，正常情况下是不能放私密信息，密码之类的，密码必须要放instance.py，k8s环境下应该设置secret进行加密

import  os
import logging
from redis import Redis
from datetime import timedelta

SECRET_KEY = b'b7d681235bab78a5'

DEBUG = False
REDIS_HOST='192.168.11.200'
REDIS_PORT=6689
SESSION_REDIS =  Redis(host=REDIS_HOST,port=REDIS_PORT)

#设置静态页面缓存时间
SEND_FILE_MAX_AGE_DEFAULT = timedelta(hours=24)

DIALECT = 'mysql'
MYSQL_DRIVER = 'pymysql'
MYSQL_HOST = '192.168.11.200'
# MYSQL_USERNAME='dev_user'
# MYSQL_PASSWORD='abc123456'
MYSQL_PORT = 52100
MYSQL_DATABASE = 'tutorial'

# SQLALCHEMY_DATABASE_URI ="mysql+pymysql://dev_user:abc123456@192.168.11.200:52100/flask-admin?charset=utf8"
# SQLALCHEMY_DATABASE_URI = '{}+{}://{}:{}@{}:{}/{}?charset=utf8'.format(
#     DIALECT,MYSQL_DRIVER,MYSQL_USERNAME,MYSQL_PASSWORD,MYSQL_HOST,MYSQL_PORT,MYSQL_DATABASE
# )
LOG_LEVEL = logging.DEBUG
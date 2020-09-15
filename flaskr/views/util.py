from flask import session,current_app
import os,json
from datetime import date, datetime
import decimal
import pymysql 
import base64
import threading
import pytz
from DBUtils.PooledDB import PooledDB
import requests

import logging
from jaeger_client import Config
from flask_opentracing import FlaskTracer
from flask import _request_ctx_stack as stack
from jaeger_client import Tracer,ConstSampler
from jaeger_client import Tracer, ConstSampler
from jaeger_client.reporter import NullReporter
from jaeger_client.codecs import B3Codec
from opentracing.ext import tags
from opentracing.propagation import Format
from opentracing_instrumentation.request_context import get_current_span,span_in_context

def init_tracer(service):
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            # 'local_agent': {
            #     'reporting_host': '192.168.11.142',
            #     'reporting_port': '6831',
            # },
            'local_agent': {
                'reporting_host': 'zipkin.istio-system',
                'reporting_port': '9411',
            },
            'logging': True,
            'propagation': 'b3',
        },
        service_name=service,
    )
    # this call also sets opentracing.tracer
    return config.initialize_tracer()

#注入header
def getForwardHeaders(request=None,cluster_name=None,tracing=None):
    headers = {}
    span = get_current_span()
    carrier = {}
    tracing.tracer.inject(
        span_context= span.context,
        format=Format.HTTP_HEADERS,
        carrier = carrier
    )
    headers.update(carrier)
    current_app.logger.debug("after headers inject: {}".format(headers))

    if 'user_name' in session:
        headers['user'] = session['user_name']

    if cluster_name:
        headers['cluster_name'] = cluster_name
        # headers = {"cluster_name":cluster_name}
        current_app.logger.debug("headers:{}".format(headers))

    incoming_headers = ['x-request-id', 'x-datadog-trace-id', 'x-datadog-parent-id', 'x-datadog-sampled']

    # Add user-agent to headers manually
    if 'user-agent' in request.headers:
        headers['user-agent'] = request.headers.get('user-agent')

    for ihdr in incoming_headers:
        val = request.headers.get(ihdr)
        if val is not None:
            headers[ihdr] = val
    # current_app.logger.debug("after headers add incoming_headers: {}".format(headers))
    return headers

def get_object_with_tracer(url=None,headers=None,namespace=None,name=None,timeout=None):
    current_app.logger.debug("get_object_with_tracer传入的header:{}".format(headers))
    data = ""
    if namespace:
        data=json.dumps({"namespace":namespace,"name":name})
    if timeout == None:
        timeout = 5
    try:
        res = requests.get(url,data=data,headers=headers,timeout=timeout)
    except Exception as e:
        current_app.logger.error(e)
        res = None
    if res and res.status_code == 200:
        # bytes
        # print(type(res.content))
        return 200,res.json()
    else:
        # status = res.status_code if res is not None and res.status_code else 500
        if res is not None and res.status_code:
            status = res.status_code
        else:
            status = 500
        return status, {'error': 'Sorry, service are currently unavailable.'}

dir_path = os.path.dirname(os.path.abspath(__file__))

# 处理接收的json数据，如果前端传的不是整形数据，进一步转化需要再调用str_to_int()
def handle_input(obj):
    # print("{}数据类型{}".format(obj,type(obj)))
    if obj == None:
        return None
    elif isinstance(obj,str):
        return (obj.strip())
    elif isinstance(obj,int):
        return obj
    else:
        print("未处理类型{}".format(type(obj)))
        return(obj.strip())
def simple_error_handle(msg):
    return jsonify({"error":msg})

def get_db_conn():
    conn = None
    try:
        mysql_host = current_app.config.get('MYSQL_HOST')
        mysql_port = int(current_app.config.get('MYSQL_PORT'))
        mysql_username = current_app.config.get('MYSQL_USERNAME')
        mysql_password = current_app.config.get('MYSQL_PASSWORD')
        mysql_database = current_app.config.get('MYSQL_DATABASE')  
        conn = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_username,password=mysql_password,
            db=mysql_database,charset='utf8')
        # dbinfo = db_info(mysql_host,mysql_port,mysql_username,mysql_password,mysql_database)
    except Exception as e:
        error = "数据库地址获取失败:{}".format(e)
        current_app.logger.error(error)
    return conn

def my_encode(a):
    return base64.b64encode(a.encode('utf-8')) 

def my_decode(a):
    return base64.b64decode(a).decode("utf-8")

def str_to_int(str):    
    # return str=="" ? 1 : int(str)  
    return 1 if str=="" else int(str)

def str_to_float(str):    
    return 1 if str=="" else float(str)

#参数是datetime
def time_to_string(dt):
    tz_sh = pytz.timezone('Asia/Shanghai')
    return  dt.astimezone(tz_sh).strftime("%Y-%m-%d %H:%M:%S")

def utc_to_local(utc_time_str, utc_format='%Y-%m-%dT%H:%M:%S.%fZ'):
    local_tz = pytz.timezone('Asia/Shanghai')
    local_format = "%Y-%m-%d %H:%M:%S"
    utc_dt = datetime.strptime(utc_time_str, utc_format)
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    time_str = local_dt.strftime(local_format)
    return time_str

class SingletonDBPool(object):
    _instance_lock = threading.Lock()

    def __init__(self):
        print("单例数据库连接初始化")
        mysql_host = current_app.config.get('MYSQL_HOST')
        mysql_port = int(current_app.config.get('MYSQL_PORT'))
        mysql_username = current_app.config.get('MYSQL_USERNAME')
        mysql_password = current_app.config.get('MYSQL_PASSWORD')
        mysql_database = current_app.config.get('MYSQL_DATABASE')
        self.pool = PooledDB(creator=pymysql,
                             maxconnections=50,
                             mincached=2,
                             maxcached=5,
                             maxshared=3,
                             blocking=True,
                             maxusage=None,
                             setsession=[],
                             ping=0,
                             host=mysql_host,
                             port=mysql_port,
                             user=mysql_username,
                             password=mysql_password,
                             database=mysql_database,
                             charset='utf8')

    def __new__(cls, *args, **kwargs):
        if not hasattr(SingletonDBPool, "_instance"):
            with SingletonDBPool._instance_lock:
                if not hasattr(SingletonDBPool, "_instance"):
                    SingletonDBPool._instance = object.__new__(cls, *args, **kwargs)
        return SingletonDBPool._instance

    def connect(self):
        return self.pool.connection()

    
def get_object_by_url(url=None,cluster_name=None,namespace=None,name=None,timeout=None,method=None):
    # headers = ""
    headers = {}
    # 获取session的id
    user_name = session.get('user_name')
    print('user_name: {}'.format(user_name))
    if cluster_name:
        headers = {"cluster_name":cluster_name,"user":user_name}
        # headers = {"cluster_name":cluster_name}
        current_app.logger.debug("headers:{}".format(headers))
    data = ""
    if namespace:
        data=json.dumps({"namespace":namespace,"name":name})
    if timeout == None:
        timeout = 5
    try:
        if method=='post':
            res = requests.post(url,data=data,headers=headers,timeout=timeout)
        else:
            res = requests.get(url,data=data,headers=headers,timeout=timeout)
    except Exception as e:
        current_app.logger.error(e)
        res = None
    if res and res.status_code == 200:
        # bytes
        # print(type(res.content))
        return 200,res.json()
    else:
        # status = res.status_code if res is not None and res.status_code else 500
        if res is not None and res.status_code:
            status = res.status_code  
        else: 
            status = 500
        return status, {'error': 'Sorry, service are currently unavailable.'}



    
import functools

from flask import Blueprint, render_template, abort,\
    request,flash,redirect,url_for,session,g,current_app,jsonify,make_response
from flask_cors import *
from jinja2 import TemplateNotFound

# # from werkzeug.security import check_passsord_hash, generate_password_hash
import json,base64,sys
# from flaskr.models.db import db
# from flaskr.models.models import User,Post
from flaskr.models.db import db
from flaskr.models.user import User
from flaskr.models.post import Post
from flaskr.models.k8s import Cluster

auth = Blueprint('auth', __name__, url_prefix='/auth',template_folder='templates')

CORS(auth, supports_credentials=True, resources={r'/*'})

@auth.after_app_request
def after(resp):
    # print("after is called,set cross")
    resp = make_response(resp)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS,PATCH,DELETE'
    resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with,Content-Type,cluster_name,user,user_id,X-B3-TraceId,X-B3-SpanId,X-B3-Sampled'
    return resp

def my_encode(a):
    return base64.b64encode(a.encode('utf-8')) 

def my_decode(a):
    return base64.b64decode(a).decode("utf-8")

@auth.route('/register',methods=('GET','POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        error = None
        if not username or  not password:
            error = "Username or password is required"
        # if not username:
        #     error = "Username is required"
        # elif not password:
        #     error = "Password is required"
        else:
            user = User.query.filter(User.username == username).first() 
            #是一个类
            # current_app.logger.debug(type(user))
            if user is not None:
                error = 'User {} is already registered.'.format(username)
        
        if error == None:
            user = User(username=username,password= my_encode(password))
            db.session.add(user)
            db.session.commit()
            # return "注册成功"
            return redirect(url_for('auth.login'))
        
        flash(error)
    current_app.logger.debug("what's up")
    try:
        return render_template('auth/register.html')
    except TemplateNotFound:
        abort(404)

# #客户端输入账号密码登录
# #比对账号密码 有 就登录成功，跳转到index，没有则提示用户没注册，跳转注册页面
# #账号密码错误，停留在本页，提示用户重新输入
@auth.route('/login',methods=('GET','POST'))
def login():
    if request.method == 'POST':
        # username = request.form['username']
        # password = request.form['password']
        data = json.loads(request.get_data().decode('utf-8'))
        current_app.logger.debug("login收到的数据:{}".format(data))
        username = data.get("username").strip()
        password = data.get("password").strip()

        current_app.logger.debug("输入的用户名:{}".format(username))
        current_app.logger.debug("输入的密码:{}".format(password))
        sql = User.query.filter(User.username==username)
        current_app.logger.debug(sql)
        user =sql.first()

        # current_app.logger.debug("查询到账号{},密码:{}".format(user.username,user.password))
        # current_app.logger.debug("数据中心密码解码：{}".format(my_decode(user.password)))
        error = None
            
        if user is None:
            error = 'Incorrect username.'
        elif password != my_decode(user.password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            session['user_name'] = user.username
            #设置集群
            return jsonify({'msg':'ok'})
            # return redirect(url_for('index'))
        return jsonify({'msg':'fail','reason':'账号密码验证失败'})
        # flash(error) 
    
    # return render_template("auth/login.html")

@auth.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    current_app.logger.debug("检查用户登录:{}".format(user_id))
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view
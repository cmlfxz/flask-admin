from flask import Blueprint,flash,g,redirect,render_template,request,url_for,session,current_app

from werkzeug.exceptions import abort

from flaskr.views.auth import login_required
from flaskr.models.db import db
from flaskr.models.user import User
from flaskr.models.post import Post
from .util import handle_input
# from flaskr.models.models import User,Post
import json

blog = Blueprint('blog',__name__)

# @blog.route('/')
# def index():
#     user_id = None
#     try:
#         user_id = int(session['user_id'])
#     except KeyError as e:
#         current_app.logger.error(e)
#     except Exception as e: 
#         current_app.logger.error("session异常:{}".format(e))
#     sql = None
#     #这里需要考虑admin的情况吗
#     admin = User.query.filter(User.username == 'admin').first()
    
#     if user_id and user_id != admin.id:
#         current_app.logger.debug("index 用户id:{}".format(user_id))
#         sql = db.session.query(User.username,Post.id,Post.title,Post.body,Post.created,Post.author_id).\
#             join(User,Post.author_id==User.id).filter(User.id==user_id).order_by(Post.created.desc())
#     else:
#         sql = db.session.query(User.username,Post.id,Post.title,Post.body,Post.created,Post.author_id).\
#             join(User,Post.author_id==User.id).order_by(Post.created.desc())
#     posts = sql.all()    
#     return render_template('blog/index.html',posts=posts)

@blog.route('/blog/create',methods={'GET','POST'})
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None 
        if not title:
            error = 'Title is required'
        if error is not None:
            flask(error)
        else:
            post = Post(title=title,body=body,author_id=g.user.id)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('blog.index'))
    return render_template("blog/create.html")

@blog.route('/blog/add',methods={'GET','POST'})
def add():
    if request.method == 'POST':
        data = json.loads(request.get_data().decode('utf-8'))
        current_app.logger.debug('blog.add收到的数据:{}'.format(data))
        title = handle_input(data.get('title'))
        body = handle_input(data.get('body'))
        username = handle_input(data.get('username'))
        user = User.query.filter(User.username == username).first() 
        if user:
            post = Post(title=title,body=body,author_id=user.id)
            db.session.add(post)
            db.session.commit()
            return json.dumps({"ok":"添加文章成功"})
        return json.dumps({"fail":"添加文章失败"})

@blog.route('/blog/update', methods=('GET', 'POST'))
def update():
    data = json.loads(request.get_data().decode('utf-8'))
    current_app.logger.debug('blog.add收到的数据:{}'.format(data))
    id = handle_input(data.get('id'))
    title = handle_input(data.get('title'))
    body = handle_input(data.get('body'))
    try:
        Post.query.filter(Post.id==id).update({'title':title,'body':body})
        db.session.commit()
        return json.dumps({"ok":"更新文章成功"})
    except Exception as e:
        return json.dumps({"fail":"更新文章失败","error":e})

def get_post(id,check_author=True):
    sql = db.session.query(User.username,Post.id,Post.title,Post.body,Post.created,Post.author_id).\
        join(User,Post.author_id==User.id).filter(Post.id==id)
    post = sql.first()
    admin = User.query.filter(User.username == 'admin').first()
    if check_author and post.author_id != g.user.id and g.user.id != admin.id:
        abort(403)
        
    return post

@blog.route('/blog/delete', methods=('GET', 'POST'))
def delete():
    data = json.loads(request.get_data().decode('utf-8'))
    current_app.logger.debug('blog.delete收到的数据:{}'.format(data))
    id = handle_input(data.get('id'))
    try:
        post = Post.query.filter(Post.id==id).first()
        db.session.delete(post)
        db.session.commit()
        return json.dumps({"ok":"删除文章成功"})
    except Exception as e:
        return json.dumps({"fail":"删除文章失败","error":e})

@blog.route('/blog/detail',methods={'GET','POST'})
# @login_required
def detail():
    data = json.loads(request.get_data().decode('utf-8'))
    id = data.get('id')
    print(type(id))
    sql = Post.query.filter(Post.id==id)
    result = sql.first()
    print(result)
    post = {
        # "user":result.username,
        "id":result.id,
        "title":result.title,
        "content":result.body,
        "create_time":result.created.strftime( '%Y-%m-%d %H:%M:%S'),       
    } 
    return json.dumps(post,indent=4)


@blog.route('/blog/list',methods={'GET','POST'})
def list():
    data = json.loads(request.get_data().decode('utf-8'))
    current_app.logger.debug('blog.list收到的数据:{}'.format(data))
    username = data.get('username')
    # admin 用户可以看到所有的文章，其他用户只能看自己写的文章
    sql = None
    if username=='admin':
        sql = db.session.query(User.username,Post.id,Post.title,Post.body,Post.created,Post.author_id).\
            join(User,Post.author_id==User.id).order_by(Post.created.desc())
    else:
        sql = db.session.query(User.username,Post.id,Post.title,Post.body,Post.created,Post.author_id).\
            join(User,Post.author_id==User.id).filter(User.username==username).order_by(Post.created.desc())
    post_list = []
    results = sql.all()  
    # print(results,type(results))
    if len(results) >0:
        for result in results:
            post = {
                "user":result.username,
                "id":result.id,
                "title":result.title,
                "content":result.body,
                "create_time":result.created.strftime( '%Y-%m-%d %H:%M:%S'),       
            } 
            post_list.append(post)
    return json.dumps(post_list)
    
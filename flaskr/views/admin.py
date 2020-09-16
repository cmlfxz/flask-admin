from flask import Blueprint, render_template, abort,\
    request,flash,redirect,url_for,session,g,current_app,jsonify,make_response

from functools import update_wrapper
from jinja2 import TemplateNotFound
import flask_sqlalchemy 
# from flask_sqlalchemy import first_or_404
import requests
import simplejson as json
from flaskr.views.auth import login_required
from flaskr.models.db import db
from flaskr.models.k8s import Cluster,Env,Project
from .util import my_decode,my_encode
from .util import handle_input
from .util import simple_error_handle
# from .util import get_object_by_url
import base64,sys,os
import requests,json
from datetime import datetime


admin = Blueprint('admin',__name__,url_prefix='/admin')

def result_to_list(obj):
    print(type(obj))
    lists = []
    for item in obj:
        elem = item[0]
        lists.append(elem)
    return lists


@admin.route('/get_cluster_name_list',methods=('GET','POST'))
def get_cluster_name_list():
    results  = db.session.query(Cluster.cluster_name).filter(Cluster.status==1).all()
    cluster_names = result_to_list(results)
    current_app.logger.debug(cluster_names)
    return json.dumps(cluster_names)

@admin.route('/cluster_list',methods=('GET','POST'))
# @login_required
def cluster_list():
    sql = db.session.query(Cluster).order_by(Cluster.create_time.desc())
    result = sql.all()
    cluster_list = []
    for item in result:
        cluster_list.append(item.to_json())
    return json.dumps(cluster_list)

@admin.route('/cluster_disable',methods=('GET','POST'))
# @login_required
def cluster_disable():
    data = json.loads(request.get_data().decode('utf-8'))
    current_app.logger.debug("cluster_disable收到数据:{}".format(data))
    id = handle_input(data.get('id'))
    cluster = Cluster.query.filter(Cluster.id == id)
    cluster.update({'status':0})
    db.session.commit()
    return jsonify({"msg":"ok"})

@admin.route('/cluster_enable',methods=('GET','POST'))
# @login_required
def cluster_enable():
    data = json.loads(request.get_data().decode('utf-8'))
    current_app.logger.debug("cluster_disable收到数据:{}".format(data))
    id = handle_input(data.get('id'))
    cluster = Cluster.query.filter(Cluster.id == id)
    cluster.update({'status':1})
    db.session.commit()
    return jsonify({"msg":"ok"})

@admin.route('/cluster_create',methods=('GET','POST'))
# @login_required
def cluster_create():
    current_app.logger.debug('进入')
    if request.method == 'POST':
        f = request.files.get('cluster_config')   
        cluster_name = request.form['cluster_name']
        cluster_type= request.form['cluster_type']
        current_app.logger.debug("cluster_name:{}, cluster_type:{}".format(cluster_name,cluster_type))
        if not f or not cluster_name or not cluster_type:
            return jsonify({'msg':'fail','error':'配置文件,名字,类型不允许为空'})
        path =  "upload/cluster/"
        if(not os.path.exists(path)):
            os.makedirs(path)
        file_path = os.path.join(path,cluster_name+".config")
        f.save(file_path)
        
        with open(file_path, mode='r', encoding='UTF-8') as file:
            cluster_config = my_encode(file.read())
            
        sql = Cluster.query.filter(Cluster.cluster_name==cluster_name)
        if sql.first():
            try:
                sql.update({'update_time':datetime.now(),'cluster_config':cluster_config,'cluster_type':cluster_type})
                db.session.commit()
            except Exception as e:
                print(e)
                return jsonify({'msg':'fail','异常':"{}".format(e)})
        else:
            cluster = Cluster(cluster_name=cluster_name,cluster_config=cluster_config,cluster_type=cluster_type,update_time=datetime.now(),status=0)
            try:
                db.session.add(cluster)
                db.session.commit()
            except Exception as e:
                print(e)
                return jsonify({'msg':'fail','异常':"{}".format(e)})
    return jsonify({'msg':'ok','file_path':file_path})

# create_namespace 和 flask-gateway重名 改为get_project_env
@admin.route('/get_project_env',methods=('GET','POST'))
# @login_required
def get_project_env():
    results  = db.session.query(Project.name).distinct().all()
    project_names = []
    for item in results:
        project_name = item.name
        project_names.append(project_name)  
    # 获取第一个project的环境
    first_project_name = project_names[0]
    print("项目:{}".format(first_project_name))
    results = db.session.query(Project.env_name).filter(Project.name==first_project_name).distinct().all()
    env_name_list = []
    for env in results:
        env_name = env.env_name
        env_name_list.append(env_name)
    return json.dumps({"project_names":project_names,"env_name_list":env_name_list})

#未检验
@admin.route('/get_env_by_project_name',methods=('GET','POST'))
def get_env_by_project_name():
    data = json.loads(request.get_data().decode('utf-8'))
    project_name =  handle_input(data.get('project_name'))
    results = db.session.query(Project.env_name).filter(Project.name==project_name).distinct().all()
    env_name_list = []
    for env in results:
        env_name = env.env_name
        env_name_list.append(env_name)
    return json.dumps(env_name_list,indent=4)

# 根据环境变量获取集群名称列表
@admin.route('/get_cluster_by_env_name',methods=('GET','POST'))
def get_cluster_by_env_name(): 
    data = json.loads(request.get_data().decode('utf-8'))
    env_name =  handle_input(data.get('env_name'))
    results = db.session.query(Env.clusters).filter(Env.name == env_name).distinct().first_or_404()
    cluster_names = results[0].split(',')
    return json.dumps(cluster_names,indent=4)
    
@admin.route('/get_env_list',methods=('GET','POST'))
# @login_required
def get_env_list():
    results  = db.session.query(Env).all()
    env_list = []
    for item in results:
        env_list.append(item.to_json())
    return json.dumps(env_list)

@admin.route('/get_project_list',methods=('GET','POST'))
# @login_required
def get_project_list():
    results  = db.session.query(Project).all()
    project_list = []
    for item in results:
        project_list.append(item.to_json())
    return json.dumps(project_list)

    
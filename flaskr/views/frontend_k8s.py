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
from .util import get_object_by_url
import base64,sys,os
import requests,json
from datetime import datetime


frontend_k8s = Blueprint('frontend_k8s',__name__,url_prefix='/frontend_k8s')

def result_to_list(obj):
    print(type(obj))
    lists = []
    for item in obj:
        elem = item[0]
        lists.append(elem)
    return lists

# gateway = "http://flask-gateway:8000"
# get_namespace_name_list_url =  gateway + "/k8s"+"/get_namespace_name_list"
# get_node_name_list_url =  gateway + "/k8s"+"/get_node_name_list" 
# get_pod_detail_url =  gateway + "/k8s"+"/get_pod_detail"
# get_node_detail_list_v2_url  = gateway + "/k8s"+"/get_node_detail_list_v2"
# get_deployment_detail_url = gateway + "/k8s"+ "/get_deployment_detail"
# get_cm_detail_url  = gateway + "/k8s"+"/get_cm_detail" 
# get_secret_detail_url = gateway + "/k8s" +"/get_secret_detail"

# # storage
# get_storage_class_url = gateway + "/k8s"+"/get_storageclass_list"
# get_pvc_list_url = gateway + "/k8s"+"/get_pvc_list"

def get_k8s_namesapce_name(cluster_name=None):
    return get_object_by_url(get_namespace_name_list_url,cluster_name)

def check_status(status):
    if status != 200 :
        flash("状态码:{} {}".format(status,"service is not available"))

def get_cluster():
    results  = db.session.query(Cluster.cluster_name).filter(Cluster.status==1).all()
    cluster_names = result_to_list(results)
    current_app.logger.debug(cluster_names)
    return cluster_names

@frontend_k8s.route('/get_cluster_name_list',methods=('GET','POST'))
def get_cluster_name_list():
    results  = db.session.query(Cluster.cluster_name).filter(Cluster.status==1).all()
    cluster_names = result_to_list(results)
    current_app.logger.debug(cluster_names)
    return json.dumps(cluster_names)

@frontend_k8s.route('/cluster_list',methods=('GET','POST'))
# @login_required
def cluster_list():
    sql = db.session.query(Cluster).order_by(Cluster.create_time.desc())
    result = sql.all()
    cluster_list = []
    for item in result:
        cluster_list.append(item.to_json())
    return json.dumps(cluster_list)
    # return render_template('k8s/cluster/cluster_list.html',cluster_list=cluster_list)

@frontend_k8s.route('/cluster_disable',methods=('GET','POST'))
# @login_required
def cluster_disable():
    data = json.loads(request.get_data().decode('utf-8'))
    current_app.logger.debug("cluster_disable收到数据:{}".format(data))
    id = handle_input(data.get('id'))
    cluster = Cluster.query.filter(Cluster.id == id)
    cluster.update({'status':0})
    db.session.commit()
    return jsonify({"msg":"ok"})
    # return redirect(url_for('frontend_k8s.cluster_list'))

@frontend_k8s.route('/cluster_enable',methods=('GET','POST'))
# @login_required
def cluster_enable():
    data = json.loads(request.get_data().decode('utf-8'))
    current_app.logger.debug("cluster_disable收到数据:{}".format(data))
    id = handle_input(data.get('id'))
    cluster = Cluster.query.filter(Cluster.id == id)
    cluster.update({'status':1})
    db.session.commit()
    return jsonify({"msg":"ok"})
    # return redirect(url_for('frontend_k8s.cluster_list'))

@frontend_k8s.route('/cluster_create',methods=('GET','POST'))
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
    # return render_template('k8s/cluster/cluster.html')

    #     return jsonify({'file_path':file_path})
    # return render_template('k8s/cluster/cluster.html')

# @frontend_k8s.route('/node_detail',methods=('GET','POST'))
# def node_detail():
#     cluster_names = get_cluster()
#     return render_template('k8s/cluster/node_detail.html',cluster_names=cluster_names)

# @frontend_k8s.route('/cluster_detail',methods=('GET','POST'))
# def cluster_detail():
#     cluster_names = get_cluster()
#     return render_template('k8s/cluster/cluster_detail.html',cluster_names=cluster_names)

# @frontend_k8s.route('/node_detail_v2',methods=('GET','POST'))
# def node_detail_v2():
#     cluster_names = get_cluster()
#     try:
#         cluster_name = request.args.get('cluster_name').strip()
#     except:
#         cluster_name = cluster_names[0]
#     status, node_list =  get_object_by_url(url=get_node_detail_list_v2_url,cluster_name=cluster_name,method='post')
#     check_status(status)
#     return render_template('k8s/cluster/node_detail_v2.html',cluster_names=cluster_names,cluster_select=cluster_name,node_list=node_list)     
        

# @frontend_k8s.route('/deployment_list',methods=('GET','POST'))
# @login_required
# def deployment_list():
#     cluster_names = get_cluster()
#     status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
#     check_status(status)
#     return render_template('k8s/workload/deployment_list.html',cluster_names=cluster_names,namespaces=namespaces)   

# @frontend_k8s.route('/virtual_service_list',methods=('GET','POST'))
# @login_required
# def virtual_service_list():
#     cluster_names = get_cluster()
#     status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
#     check_status(status)
#     return render_template('k8s/istio/virtual_service_list.html',cluster_names=cluster_names,namespaces=namespaces)     

# @frontend_k8s.route('/get_all_in_namespace',methods=('GET','POST'))
# @login_required
# def get_all_in_namespace():
#     cluster_names = get_cluster()
#     status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
#     check_status(status)
#     return render_template('k8s/workload/get_all_in_namespace.html',cluster_names=cluster_names,namespaces=namespaces)    

# create_namespace 和 flask-gateway重名 改为get_project_env
@frontend_k8s.route('/get_project_env',methods=('GET','POST'))
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
    # return render_template('k8s/cluster/create_namespace.html',project_names=project_names,env_name_list=env_name_list)

#未检验
@frontend_k8s.route('/get_env_by_project_name',methods=('GET','POST'))
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
@frontend_k8s.route('/get_cluster_by_env_name',methods=('GET','POST'))
def get_cluster_by_env_name(): 
    data = json.loads(request.get_data().decode('utf-8'))
    env_name =  handle_input(data.get('env_name'))
    results = db.session.query(Env.clusters).filter(Env.name == env_name).distinct().first_or_404()
    cluster_names = results[0].split(',')
    return json.dumps(cluster_names,indent=4)
    
@frontend_k8s.route('/get_env_list',methods=('GET','POST'))
# @login_required
def get_env_list():
    results  = db.session.query(Env).all()
    env_list = []
    for item in results:
        env_list.append(item.to_json())
    return json.dumps(env_list)
    # return render_template('k8s/get_env_list.html',env_list=env_list)    

@frontend_k8s.route('/get_project_list',methods=('GET','POST'))
# @login_required
def get_project_list():
    results  = db.session.query(Project).all()
    project_list = []
    for item in results:
        project_list.append(item.to_json())
    return json.dumps(project_list)
    # return render_template('k8s/get_project_list.html',project_list=project_list)    

# @frontend_k8s.route('/k8s_namespace',methods=('GET','POST'))
# @login_required
# def k8s_namespace():
#     cluster_names = get_cluster()
#     return render_template('k8s/cluster/k8s_namespace.html',cluster_names=cluster_names)  

# @frontend_k8s.route('/get_storage_class',methods=('GET','POST'))
# @login_required
# def get_storage_class():
#     # cluster_names = get_cluster()
#     # return render_template('k8s/k8s_storage_class.html',cluster_names=cluster_names)  
#     cluster_names = get_cluster()
#     try:
#         cluster_name = request.args.get('cluster_name').strip()
#     except:
#         cluster_name = cluster_names[0]
#     status, storage_class_list =  get_object_by_url(url=get_storage_class_url,cluster_name=cluster_name,method='post')
#     print(storage_class_list)
#     check_status(status)
#     return render_template('k8s/storage/k8s_storage_class.html',
#                            cluster_names=cluster_names,
#                            cluster_select=cluster_name,
#                            storage_class_list=storage_class_list)     

# @frontend_k8s.route('/k8s_pv_manage',methods=('GET','POST'))
# @login_required
# def k8s_pv_manage():
#     cluster_names = get_cluster()
#     return render_template('k8s/storage/k8s_pv_manage.html',cluster_names=cluster_names)  

# @frontend_k8s.route('/k8s_pvc_manage',methods=('GET','POST'))
# @login_required
# def k8s_pvc_manage():
#     cluster_names = get_cluster()
#     status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
#     check_status(status)
#     return render_template('k8s/storage/k8s_pvc_manage.html',cluster_names=cluster_names,namespaces=namespaces)  


# @frontend_k8s.route('/api_test',methods=('GET','POST'))
# @login_required
# def api_test():
#     cluster_names = get_cluster()
#     status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
#     check_status(status)
#     return render_template('k8s/api_test.html',cluster_names=cluster_names,namespaces=namespaces)  

# @frontend_k8s.route('/k8s_pod_list',methods=('GET','POST'))
# @login_required
# def k8s_pod_list():
#     cluster_names = get_cluster()
#     status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
#     check_status(status)
#     status,nodes = get_object_by_url(get_node_name_list_url,cluster_names[0])
#     check_status(status)
#     return render_template('k8s/workload/k8s_pod_list.html',cluster_names=cluster_names,namespaces=namespaces,nodes=nodes)  

# @frontend_k8s.route('/k8s_pod_detail',methods=('GET','POST'))
# @login_required
# def k8s_pod_detail():
#     name = request.args.get('name')
#     namespace = request.args.get('namespace')
#     cluster_name = request.args.get('cluster_name')
#     if name == None or namespace == None or cluster_name == None:
#         return simple_error_handle("name,namesapce,cluster_name不能为空")
#     if namespace=='all':
#         return simple_error_handle("namespace不能为all，请选择具体命名空间")
#     status,pod_detail = get_object_by_url(get_pod_detail_url,cluster_name,namespace,name)
#     check_status(status)
#     event_list = None
#     if 'event_list' in pod_detail.keys():
#         event_list = json.loads(pod_detail['event_list'])
#     return render_template('k8s/workload/pod_detail.html',pod_detail=pod_detail,event_list=event_list)

# # 详情页
# @frontend_k8s.route('/k8s_deployment_detail',methods=('GET','POST'))
# @login_required
# def k8s_deployment_detail():
#     cluster_name = request.args.get('cluster_name')
#     namespace = request.args.get('namespace')
#     name = request.args.get('name')
#     if name == None or namespace == None or cluster_name == None:
#         return simple_error_handle("name,namesapce,cluster_name不能为空")
#     if namespace=='all':
#         return simple_error_handle("namespace不能为all，请选择具体命名空间")
#     status,deployment_detail = get_object_by_url(get_deployment_detail_url,cluster_name,namespace,name)
#     print(deployment_detail)
#     check_status(status)
#     event_list = json.loads(deployment_detail['event_list'])
#     return render_template('k8s/workload/deployment_detail.html',deployment_detail=deployment_detail,event_list=event_list)

# @frontend_k8s.route('/k8s_gateway_list',methods=('GET','POST'))
# @login_required
# def k8s_gateway_list():
#     cluster_names = get_cluster()
#     status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
#     check_status(status)
#     return render_template('k8s/istio/k8s_gateway_list.html',cluster_names=cluster_names,namespaces=namespaces)  

# @frontend_k8s.route('/k8s_ingress_list',methods=('GET','POST'))
# @login_required
# def k8s_ingress_list():
#     cluster_names = get_cluster()
#     status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
#     check_status(status)
#     return render_template('k8s/service/k8s_ingress_list.html',cluster_names=cluster_names,namespaces=namespaces)  

# @frontend_k8s.route('/k8s_service_list',methods=('GET','POST'))
# @login_required
# def k8s_service_list():
#     # bug 刷新的话 并没有按cookie保存的cluster_name去发起请求
#     cluster_names = get_cluster()
#     status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
#     check_status(status)
#     return render_template('k8s/service/k8s_service_list.html',cluster_names=cluster_names,namespaces=namespaces)  

# @frontend_k8s.route('/k8s_destination_rule_list',methods=('GET','POST'))
# @login_required
# def k8s_destination_rule_list():
#     cluster_names = get_cluster()
#     status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
#     check_status(status)
#     return render_template('k8s/istio/k8s_destination_rule_list.html',cluster_names=cluster_names,namespaces=namespaces)  

# @frontend_k8s.route('/daemonset_list',methods=('GET','POST'))
# @login_required
# def daemonset_list():
#     cluster_names = get_cluster()
#     status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
#     check_status(status)
#     return render_template('k8s/workload/daemonset_list.html',cluster_names=cluster_names,namespaces=namespaces)  

# @frontend_k8s.route('/statefulset_list',methods=('GET','POST'))
# @login_required
# def statefulset_list():
#     cluster_names = get_cluster()
#     status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
#     check_status(status)
#     return render_template('k8s/workload/statefulset_list.html',cluster_names=cluster_names,namespaces=namespaces)  

# @frontend_k8s.route('/configmap_list',methods=('GET','POST'))
# @login_required
# def configmap_list():
#     cluster_names = get_cluster()
#     status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
#     check_status(status)
#     return render_template('k8s/config/configmap_list.html',cluster_names=cluster_names,namespaces=namespaces)  
 
# @frontend_k8s.route('/k8s_configmap_detail',methods=('GET','POST'))
# @login_required
# def k8s_configmap_detail():
#     name = request.args.get('name')
#     namespace = request.args.get('namespace')
#     cluster_name = request.args.get('cluster_name')
#     if name == None or namespace == None or cluster_name == None:
#         return simple_error_handle("name,namesapce,cluster_name不能为空")
#     if namespace=='all':
#         return simple_error_handle("namespace不能为all，请选择具体命名空间")
#     status,configmap_detail = get_object_by_url(get_cm_detail_url,cluster_name,namespace,name)
#     check_status(status)
#     data = configmap_detail['data']
#     cm_data = []
#     if data != None:
#         for k,v in data.items():
#             item = {"key":k,"value":v}
#             cm_data.append(item)
#     # current_app.logger.debug(type(data))
#     return render_template('k8s/config/configmap_detail.html',configmap_detail=configmap_detail,cm_data=cm_data)

# @frontend_k8s.route('/secret_list',methods=('GET','POST'))
# @login_required
# def secret_list():
#     cluster_names = get_cluster()
#     status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
#     if status != 200 :
#         flash("状态码:{} {}".format(status,"service is not available"))
#     return render_template('k8s/config/secret_list.html',cluster_names=cluster_names,namespaces=namespaces)  

# @frontend_k8s.route('/k8s_secret_detail',methods=('GET','POST'))
# @login_required
# def k8s_secret_detail():
#     name = request.args.get('name')
#     namespace = request.args.get('namespace')
#     cluster_name = request.args.get('cluster_name')
#     if name == None or namespace == None or cluster_name == None:
#         return simple_error_handle("name,namesapce,cluster_name不能为空")
#     if namespace=='all':
#         return simple_error_handle("namespace不能为all，请选择具体命名空间")
#     status,secret_detail = get_object_by_url(url=get_secret_detail_url,cluster_name=cluster_name,namespace=namespace,name=name)
#     check_status(status)
#     # current_app.logger.debug(secret_detail)
#     secret_data = secret_detail['data']
#     return render_template('k8s/config/secret_detail.html',secret_detail=secret_detail,secret_data=secret_data)

# @frontend_k8s.route('/k8s_hpa_list',methods=('GET','POST'))
# @login_required
# def k8s_hpa_list():
#     cluster_names = get_cluster()
#     status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
#     check_status(status)
#     return render_template('k8s/workload/k8s_hpa_list.html',cluster_names=cluster_names,namespaces=namespaces)  

# @frontend_k8s.route('/k8s_job_list',methods=('GET','POST'))
# @login_required
# def k8s_job_list():
#     cluster_names = get_cluster()
#     status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
#     check_status(status)
#     return render_template('k8s/task/k8s_job_list.html',cluster_names=cluster_names,namespaces=namespaces)  

# @frontend_k8s.route('/k8s_cronjob_list',methods=('GET','POST'))
# @login_required
# def k8s_cronjob_list():
#     cluster_names = get_cluster()
#     status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
#     check_status(status)
#     return render_template('k8s/task/k8s_cronjob_list.html',cluster_names=cluster_names,namespaces=namespaces)  

# @frontend_k8s.route('/k8s_event_list',methods=('GET','POST'))
# @login_required
# def k8s_event_list():
#     cluster_names = get_cluster()
#     status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
#     check_status(status)
#     return render_template('k8s/cluster/k8s_event_list.html',cluster_names=cluster_names,namespaces=namespaces)  

# @frontend_k8s.route('/k8s_component_status_list',methods=('GET','POST'))
# @login_required
# def k8s_component_status_list():
#     cluster_names = get_cluster()
#     return render_template('k8s/cluster/k8s_component_status_list.html',cluster_names=cluster_names)  

@frontend_k8s.route('/k8s_sa_list',methods=('GET','POST'))
@login_required
def k8s_sa_list():
    cluster_names = get_cluster()
    status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
    check_status(status)
    return render_template('k8s/auth/k8s_sa_list.html',cluster_names=cluster_names,namespaces=namespaces)  

@frontend_k8s.route('/k8s_cluster_role_list',methods=('GET','POST'))
@login_required
def k8s_cluster_role_list():
    cluster_names = get_cluster()
    return render_template('k8s/auth/k8s_cluster_role_list.html',cluster_names=cluster_names)  


@frontend_k8s.route('/k8s_cluster_role_binding_list',methods=('GET','POST'))
@login_required
def k8s_cluster_role_binding_list():
    cluster_names = get_cluster()
    return render_template('k8s/auth/k8s_cluster_role_binding_list.html',cluster_names=cluster_names)  

@frontend_k8s.route('/k8s_role_list',methods=('GET','POST'))
@login_required
def k8s_role_list():
    cluster_names = get_cluster()
    status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
    check_status(status)
    return render_template('k8s/auth/k8s_role_list.html',cluster_names=cluster_names,namespaces=namespaces)  
    
    
@frontend_k8s.route('/k8s_role_binding_list',methods=('GET','POST'))
@login_required
def k8s_role_binding_list():
    cluster_names = get_cluster()
    status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
    check_status(status)
    return render_template('k8s/auth/k8s_role_binding_list.html',cluster_names=cluster_names,namespaces=namespaces)  

# @frontend_k8s.route('/k8s_network_policy_list',methods=('GET','POST'))
# @login_required
# def k8s_network_policy_list():
#     cluster_names = get_cluster()
#     status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
#     check_status(status)
#     return render_template('k8s/security/k8s_network_policy_list.html',cluster_names=cluster_names,namespaces=namespaces)  

# @frontend_k8s.route('/istio_policy_list',methods=('GET','POST'))
# @login_required
# def istio_policy_list():
#     cluster_names = get_cluster()
#     status, namespaces = get_k8s_namesapce_name(cluster_name=cluster_names[0])
#     check_status(status)
#     return render_template('k8s/security/istio_policy_list.html',cluster_names=cluster_names,namespaces=namespaces)     

    
    
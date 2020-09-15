from flaskr.models.db import db
from datetime import datetime
class Namespace(db.Model):
    __tablename__='namespace'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),unique=True)
    create_time = db.Column(db.DateTime,nullable=False,default=datetime.now)
    labels = db.Column(db.Text)
    cluster_name = db.Column(db.String(50))

class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50))
    env_name = db.Column(db.String(50))
    create_time = db.Column(db.DateTime,nullable=False,default=datetime.now)
    create_user = db.Column(db.String(50))
    def to_json(self):
        return {
            'id':self.id,
            'name':self.name,
            'env_name':self.env_name,
            'create_user':self.create_user,                
            'create_time':self.create_time.strftime( '%Y-%m-%d %H:%M:%S'),   
        }
    
class Env(db.Model):
    __tablename__ = 'env'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),unique=True)
    create_time = db.Column(db.DateTime,nullable=False,default=datetime.now)
    create_user = db.Column(db.String(50))
    clusters = db.Column(db.Text)
    def to_json(self):
        return {
            'id':self.id,
            'name':self.name,
            'clusters':self.clusters,
            'create_user':self.create_user,                
            'create_time':self.create_time.strftime( '%Y-%m-%d %H:%M:%S'),   
        }

class Cluster(db.Model):
    __tablename__ = 'cluster'
    id = db.Column(db.Integer,primary_key=True)
    cluster_name = db.Column(db.String(50),unique=True)
    create_time = db.Column(db.DateTime,nullable=False,default=datetime.now)
    update_time = db.Column(db.DateTime,nullable=False,default=datetime.now)
    cluster_config = db.Column(db.Text)
    cluster_type = db.Column(db.String(20),comment='集群类型,1、私有云 2、阿里云 3、AWS 4、Azure 5、青云 6、华为云 7、腾讯云')
    status = db.Column(db.Integer,comment="1:启用,0:禁用")
    def __init__(self,cluster_name=None,create_time=None,update_time=None,cluster_config=None,cluster_type=None,status=None):
        self.cluster_name = cluster_name
        # self.create_time = create_time
        self.update_time = update_time
        self.cluster_config = cluster_config
        self.cluster_type = cluster_type
        self.status = status
    def to_json(self):
        return {
            'id':self.id,
            'cluster_name':self.cluster_name,
            'create_time':self.create_time.strftime( '%Y-%m-%d %H:%M:%S'),
            'update_time':self.update_time.strftime( '%Y-%m-%d %H:%M:%S'),     
            'cluster_config':self.cluster_config,
            'cluster_type':self.cluster_type,
            'status':self.status,    
        }
    # create_user = db.Column(db.String(50))
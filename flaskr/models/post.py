from flaskr.models.db import db
from datetime import datetime
class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer,primary_key=True)
    author_id  = db.Column(db.Integer)
    created = db.Column(db.DateTime,nullable=False,default=datetime.now)
    title = db.Column(db.String(100))
    body = db.Column(db.Text)
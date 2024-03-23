from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Post_communications(db.Model):
    PostID = db.Column(db.String(300),primary_key=True)
    replyed_by = db.Column(db.String(300))
    reply_no = db.Column(db.Integer)
    reply_text = db.Column(db.String(300))
    reply_date = db.Column(db.DateTime)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Post_contents(db.Model):
    userid = db.Column(db.String(300),index=True)
    postid = db.Column(db.String(300),primary_key=True)
    imageURL = db.Column(db.String(300))
    description = db.Column(db.String(150))
    Good_no = db.Column(db.Integer)
    post_date = db.Column(db.DateTime)


from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Relations(db.Model):
    relarion_id = db.Column(db.Integer,primary_key=True)
    followed_by = db.Column(db.String(300),index=True)
    follow_to = db.Column(db.String(300),index=True)

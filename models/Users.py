from extensions import db

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(50),index=True, unique=False)
    password = db.Column(db.String(300))
    description = db.Column(db.String(300))
    thumbnail_url = db.Column(db.String(120), unique=False)


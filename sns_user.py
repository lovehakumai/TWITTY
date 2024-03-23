from flask import Flask, redirect, session
from flask import Response 
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import models.Users as models_users
import sqlite3

# ログイン処理 - 入力されたIDとパスワードが一致しているかを確認する
def try_login(form):
    user_id = form.get('user_id')
    password=form.get('password')
    
    ok = check_user_match(user_id, password)

    if not ok:
        return False
    session['login'] = user_id
    return True

def check_user_match(user_id,password):
    # Usersテーブルから入力されたIDに対するレコードを取得する
    users_id_record = select('SELECT id,password FROM Users WHERE id=?',user_id)
    if len(users_id_record)==0:
        return None
    ok = models_users.check_password_hash(users_id_record[1])
    if not ok:
        return None
    return ok


# ログイン必須を処理するデコレーターを定義
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not is_login():
            return redirect('/login')
        return func(*args, **kwargs)
    return wrapper

    
# ログインしているかの確認
def is_login():
    return 'login' in session


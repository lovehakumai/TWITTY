from flask import Flask, redirect, session
from flask import Response 
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import models.Users as models_users
import sqlite3
import user_sqlite
import bcrypt

# アカウント作成処理
def try_create_account(form):
    user_id = form.get('user_id')
    password = form.get('password')
    # パスワードをハッシュ化
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    # データベースにユーザを追加
    conn = sqlite3.connect(user_sqlite.USER_FILE)
    c = conn.cursor()
    c.execute('INSERT INTO users (user_id, password) VALUES(?,?)',(user_id, hashed_password))
    conn.commit()
    conn.close()
    print(f"User {user_id} is created")

# ログイン処理 - 入力されたIDとパスワードが一致しているかを確認する
def try_login(form):
    user_id = form.get('user_id')
    password=form.get('password')
    
    # ユーザー名に基づいてハッシュ化されたパスワードを取得
    conn = sqlite3.connect(user_sqlite.USER_FILE)
    c = conn.cursor()
    c.execute('SELECT password FROM Users where user_id=?',(user_id,))
    result = c.fetchone()

    if result is None:
        print('user is not found')
        return False
    else:
        hashed_password = result[0]
        # 入力されたパスワードがデータベースのハッシュと一致するかを検証
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            print('Login Sucessful')
            session['login'] = user_id
            return True
        else:
            print('Password is Incorrect')
            return False


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


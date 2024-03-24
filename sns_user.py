from flask import Flask, redirect, session,render_template
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

    # ユーザーIDに重複がないかを確認する
    conn = sqlite3.connect(user_sqlite.USER_FILE)
    c = conn.cursor()
    c.execute('SELECT user_id FROM users where user_id=?',(user_id,))
    result = c.fetchone()
    if result is not None: # レコードがみつかった場合
        conn.close()
        return render_template('create_account.html', msg="This Id is already used")
    else:
        # パスワードをハッシュ化
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        # データベースにユーザを追加
        c.execute('INSERT INTO users (user_id, password) VALUES(?,?)',(user_id, hashed_password))
        conn.commit()
        conn.close()
        session['login']=user_id
        return redirect('/')

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
        return render_template('create_account.html', msg="Id and Password is mandetory")
    else:
        hashed_password = result[0]
        # 入力されたパスワードがデータベースのハッシュと一致するかを検証
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            print('Login Sucessful')
            session['login'] = user_id
            return redirect('home/'+ user_id)
        else:
            print('Password is Incorrect')
            return render_template('/login',msg="Password or Id is wrong")


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


from flask import Flask, redirect, session,render_template,url_for
from flask import Response 
from functools import wraps
import models.Users as models_users
import sqlite3
import sqlite_func
import bcrypt

# アカウント作成処理
def try_create_account(form):
    user_id = form.get('user_id',"")
    password = form.get('password',"")
    if not user_id or not password:
        msg="Fill in Id&PASS both"
        return False,msg

    # ユーザーIDに重複がないかを確認する
    conn = sqlite3.connect(sqlite_func.DB_FILE)
    c = conn.cursor()
    c.execute('SELECT user_id FROM users where user_id=?',(user_id,))
    result = c.fetchone()
    if result is not None: # レコードがみつかった場合
        conn.close()
        msg="This Id is already used"
        return False,msg
    else:
        # パスワードをハッシュ化
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        # データベースにユーザを追加
        c.execute('INSERT INTO users (user_id, password) VALUES(?,?)',(user_id, hashed_password))
        conn.commit()
        conn.close()
        session['login']=user_id
        print("debug here : ", user_id, password)
        return True,"okey"

# ログイン処理 - 入力されたIDとパスワードが一致しているかを確認する
def try_login(form):
    user_id = form.get('user_id')
    password=form.get('password')
    
    # ユーザー名に基づいてハッシュ化されたパスワードを取得
    conn = sqlite3.connect(sqlite_func.DB_FILE)
    c = conn.cursor()
    # user_idが文字列として提供されている場合、文字列内の各文字が個別のバインディングとして解釈される可能性があります。例えば、user_idが"abcd"であれば、4つのバインディングが提供されたと解釈されます。
    # 正しい方法は、user_idを単一の要素を持つタプルとして渡すことです。タプルを使う場合は、カンマを忘れないようにしてください（カンマがないと、それはタプルとは認識されません）。
    c.execute('SELECT password FROM Users where user_id=?',(user_id,))
    result = c.fetchone()
    print("result : " , result)
    msg = ""
    if result is None:
        msg = "Id and Password is mandetory"
        return False, msg
    else:
        hashed_password = result[0]
        print(result)
        # 入力されたパスワードがデータベースのハッシュと一致するかを検証
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            print('Login Sucessful')
            session['login'] = user_id
            return True,msg
        # url_for関数は、Flaskのルート関数名を引数に取り、そのルートのURLを生成します。ルート関数名は、@app.routeデコレータで定義された関数の名前です。url_forを使用する際は、URLの一部を動的に追加するために文字列結合を直接使用するのではなく、キーワード引数を渡してその部分を指定します。
        else:
            print('Password is Incorrect')
            msg="Password or Id is wrong"
            return False,msg


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

# ログアウト
def try_logout():
    session.pop('login', None)

# ユーザIDをもとに該当するレコードを返す関数
def user_info(user_id):
    conn = sqlite3.connect(sqlite_func.DB_FILE)
    c = conn.cursor()
    c.execute()

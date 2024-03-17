from flask import Flask, request, render_template, url_for
from flask import redirect, Markup, session
import os, time
import sns_user as user, sns_data as sns_data

# Flaskインスタンスの作と暗号化キーの決定
app = Flask(__name__)
secret_key = "jknmmM9090"

# URLルーティング
@app.route('/')
def index():
    if 'login' in session:
        user_id = session.get('user_id')
        return redirect(url_for('home', user_id=user_id))
    else:
        return redirect('/welcome')

# ウェルカムページ
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

# ログインページ
@app.route('/login')
def login():
    return render_template('login.html',msg='')

# ログインページ loginページから入力フォームが送られる
@app.route('/login/try', methods=["POST"])
def login_try():
    ok = user.try_login(request.form)
    if not ok:
        return render_template('login.html',msg='IDまたはパスワードが間違っています')
    return redirect('/')

# アカウント作成ページ
@app.route('/create_account')
def create_account():
    return render_template('create_account.html',msg='')

# アカウント作成ページ
@app.route('/create_account/try',methods=["POST"])
def create_account_try():
    ok = user.try_create_account(request.form)
    if not ok:
        return render_template('create_account.html',msg='このIDはすでに使われています')
    return redirect('/')

# ホーム画面
@app.route('/home/<user_id>')
@login_required
def home(user_id):
    post_all=user.get_posts(user_id)
    return render_template('home.html',posts=post_all)

# 
    







    



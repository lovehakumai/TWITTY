from flask import Flask, request, render_template, url_for
from flask import redirect, Markup, session
import os, time
import sns_user as user, sns_data as sns_data
from werkzeug.utils import secure_filename

# BASE_DIR
BASE_DIR = os.pat.dirname(__file__)
IMAGE_FILE = BASE_DIR + '/data/images'
PROFILE_FILE = BASE_DIR + '/data/thumbnails'
USER_FILE = BASE_DIR + '/data/users.sqlite3'
RELATION_FILE = BASE_DIR + '/data/user_relation.sqlite3'
POST_FILE = BASE_DIR + '/data/post.sqlite3'


# Flaskインスタンスの作と暗号化キーの決定
app = Flask(__name__)
secret_key = "jknmmM9090"

# URLルーティング
@app.route('/')
def index():
    if 'login' in session:
        user_id = session.get('user_id')
        return redirect('home' +user_id)
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

# 投稿画面
@app.route('/post/<user_id>')
@login_required
def post():
    return render_template('post.html')

@app.route('/post/try/<user_id>', methods=["POST"])
@login_required
def post_try():
    title = request.form.get('title')
    image = request.files['image']
    comment = request.form.get('comment')

    if image:
        filename=secure_filename(image.filename)
        # 画像を保存するディレクトリのパスを指定
        save_path = IMAGE_FILE + filename
        image.save(save_path)
    sns_data.save_to_post(title=title, comment=comment, filename=filename)
    return redirect('/')

# プロファイル画面
@login_required
@app.route('/myprofile/<user_id>')
def profile():
    return render_template('myprofile.html')

# プロファイル編集画面
@login_required
@app.route('/myprofile/<user_id>/edit', method=["POST"])
def profile_edit():
    user_id = user.get_id()
    name = request.get.form('name','')
    introduction = request.get.form('introduction','')
    thumbnail = request.files['image']

    if not name:
        return render_template('/myprofile/'+user_id+'/edit',msg='ニックネームは必須です')

    if thumbnail:
        filename=secure_filename(thumbnail.filename)
        # 画像を保存するディレクトリのパスを指定
        save_path = PROFILE_FILE
        thumbnail.save(save_path,filename)

    sns_data.save_to_post(user_id=user_id, name=name, introduction=introduction, filename=filename)


# 他人プロファイル画面
@login_required
@app.route('/profile/<user_id>')
def profile_others():
    
    

        

    







    



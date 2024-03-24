from flask import Flask, request, render_template
from flask import redirect, session
from markupsafe import Markup
import os, time
import sns_user as user, sns_data as sns_data, relation as rel, sns_posts as post
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from extension import db, migrate
# スキーマ定義のインポート
from models.Users import Users
from models.Relations import Relations
from models.Post_communications import Post_communications
from models.Post_contents import Post_contents

# BASE_DIR
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FILE = BASE_DIR + '/data/images'
PROFILE_FILE = BASE_DIR + '/data/thumbnails'
DB_PATH = os.path.join(BASE_DIR, 'sqlite', 'db.sqlite3')



# Flaskインスタンスの作と暗号化キーの決定
app = Flask(__name__)
secret_key = "test_key"

# Flask-Migrate
# モデルをインポート
    # Flask-Migrate（FlaskのためのAlembicのラッパー）を使用する場合、
    # モデルが複数のファイルに分割されていても、
    # マイグレーションを実行するプロセスは変わりません。
    # 重要なのは、アプリケーションの初期化時に
    # これらのモデルを読み込むことを確実にすることです。
    # Flask-Migrateは、dbインスタンスを介してモデル定義を探しますので、
    # マイグレーションプロセスを実行する前に、
    # アプリケーションがすべてのモデル定義を認識している必要があります。
from models.Users import Users
from models.Relations import Relations
from models.Post_contents import Post_contents
from models.Post_communications import Post_communications
# アプリケーションでFlask-Migrateを使用するためには、
# app.py（またはアプリケーションのメインスクリプト）でFlask-Migrateを設定する必要があります。
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False # ログインchat.openai.com/c/db3a03dc-0a6d-47fc-8c68-e865eaa70241
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(DB_PATH)

db.init_app(app)
migrate.init_app(app,db)


# URLルーティング
@app.route('/')
def index():
    if 'login' in session:
        user_id = session.get('user_id')
        return redirect('home/' +user_id)
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
    user.try_login(request.form)

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
@user.login_required
def home(user_id):
    post_all=user.get_posts(user_id)
    return render_template('home.html',posts=post_all)

# 投稿画面
@app.route('/post/<user_id>')
@user.login_required
def post():
    return render_template('post.html')

@app.route('/post/try/<user_id>', methods=["POST"])
@user.login_required
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
@user.login_required
@app.route('/myprofile/<user_id>')
def profile():
    return render_template('myprofile.html')

# プロファイル編集画面
@user.login_required
@app.route('/myprofile/<user_id>/edit', methods=["POST"])
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


# 他人プロファイル画面の詳細画面
@user.login_required
@app.route('/profile/<user_id>')
def profile_others(user_id):
    user_id = user.get_id()
    name = request.get.form('name','')
    introduction = request.get.form('introduction','')
    thumbnail = request.files['image']
    posts = sns_data.get_posts(user_id)
    return render_template('/profile/<user_id>')

# 他のユーザを検索する画面
@user.login_required
@app.route('/user_search')
def user_search():
    return render_template('/user_search')

# プロファイル画面から、フォローしている人を一覧で表示
@user.login_required
@app.route('/follow_list/<user_id>')
def follow_list(user_id):
    following_users = rel.get_all_following(user_id)
    return render_template('user_following_list.html', users = following_users)

# プロファイル画面から、フォローしてくれている人を一覧で表示
@user.login_required
@app.route('/follower_list')
def follower_list(user_id):
    follower_users = rel.get_all_following(user_id)
    return render_template('user_following_list.html', users = follower_users)
 
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
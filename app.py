from flask import Flask, request, render_template,url_for
from flask import redirect, session,flash
import sns_data
import os,time
import sns_user as user, sns_data as sns_data, relation as rel, sns_posts as posts
from werkzeug.utils import secure_filename
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
app.secret_key = "test_key"

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
        user_id = session.get('login')
        return redirect('home/' + user_id)
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
    result, msg = user.try_login(request.form)
    if result :
        user_id = session['login']
        return redirect(url_for('home',user_id=user_id))
    else:
        return render_template('login.html', msg=msg)

# ログアウトページ
@app.route('/logout')
def logout():
    user.try_logout()
    return redirect('/')

# アカウント作成ページ
@app.route('/create_account')
def create_account():
    return render_template('create_account.html',msg='')

# アカウント作成ページ
@app.route('/create_account/try',methods=["POST"])
def create_account_try():
    judge, msg = user.try_create_account(request.form)
    if not judge:
        return render_template('create_account.html',msg=msg)
    else:
        user_id=session['login']
        return redirect('/')

# ホーム画面
@app.route('/home/<user_id>')
@user.login_required
def home(user_id):
    post_all=posts.get_posts(user_id)
    return render_template('home.html',posts=post_all,user_id=user_id)

# プロファイル画面
@app.route('/myprofile')
@user.login_required
def post():
    user_id = session['login']
    return redirect(url_for('myprofile_try',user_id=user_id))

#url_for はリダイレクトを行う redirect 関数と組み合わせて使う必要があります。
#myprofile_try 関数で user_id を引数として受け取らなければ、その関数の中で user_id を使うことはできません。


@app.route('/myprofile/<user_id>')
@user.login_required
def myprofile_try(user_id):
    # ユーザのニックネームがない場合はプロファイル設定画面へ
    # ある場合はプロファイルを参照する画面へ
    # ユーザの情報を取得
    app.logger.debug('【SECTION!】myprofile_try is in process')
    user_id = session['login']
    user_info = user.user_info(user_id) # 辞書型でUser_idに関連する行を取得する(想定は1行)
    first_row=user_info[0]
    if len[user_info]==0 or first_row[user_id]==None:
        flash('ERROR : something went wrong with your Account!!')
        return redirect('/')
    if len[user_info]==1:

        if first_row['nickname']==None:
            flash('Before checking your profile,Please set your infomation')
            return render_template('myprofile_edit.html',user_id=user_id)
        else:
            posts=sns_data.get_posts(user_id)
            return render_template('myprofile.html',
                                   user_info=first_row,
                                   post=posts)
    else:
        flash('ERROR : something went wrong with your Account!!')
        return redirect('/') 

# プロファイル編集画面へのRequestを受理
@user.login_required
@app.route('/myprofile/<user_id>/edit', methods=["POST"])
def myprofile_edit():
    user_id = user.session['login']
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

    sns_data.save_to_post(user_id=user_id, 
                          name=name, 
                          introduction=introduction, 
                          filename=filename)
    return url_for('myprofile_try')



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


# 投稿処理
@app.route('/post/try/<user_id>',methods=['POST'])
@user.login_required
def post_save():
    user_id=session['login']
    title=request.form.get('title',time.utcnow)
    description = request.form.get('desctiption',"")
    return sns_data.save_post(user_id,title,description)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
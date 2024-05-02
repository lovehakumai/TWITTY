from flask import Flask, request, render_template,url_for
from flask import redirect, session,flash
import sns_data
import os,time
import sns_user as user, sns_data as sns_data, relation as rel, sns_posts as posts, sqlite_func
import hashlib
from werkzeug.utils import secure_filename
from extension import db, migrate
# スキーマ定義のインポート
from models.Users import Users
from models.Relations import Relations
from models.Post_communications import Post_communications
from models.Post_contents import Post_contents

# Flaskインスタンスの作と暗号化キーの決定
app = Flask(__name__)
app.secret_key = "test_key"

# BASE_DIR
BASE_DIR = 'static'
IMAGE_FILE = BASE_DIR + '/images'
PROFILE_FILE = BASE_DIR + '/thumbnails'
DB_PATH = os.path.join(BASE_DIR, 'sqlite', 'db.sqlite3')

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
def myprofile():
    user_id = session['login']
    return redirect(url_for('myprofile_try',user_id=user_id))

#url_for はリダイレクトを行う redirect 関数と組み合わせて使う必要があります。
#myprofile_try 関数で user_id を引数として受け取らなければ、その関数の中で user_id を使うことはできません。


@app.route('/myprofile/<user_id>')
@user.login_required
def myprofile_try(user_id):
    # ユーザのニックネームがない場合はプロファイル設定画面へ
    # ある場合はプロファイルを参照する画面へ
    #辞書型でUser_idに関連する行を取得する(想定は1行)
    user_info = user.user_info(user_id)
    first_row=user_info[0]
    if len(user_info)==0 or first_row==None:
        flash('ERROR : something went wrong with your Account!!')
        return redirect('/')
    if len(user_info)==1:

        if first_row['nickname']==None:
            flash('Before checking your profile,Please set your infomation')
            return render_template('myprofile_edit.html',user_id=user_id)
        else:
            posts=sns_data.get_posts(user_id)
            for post in posts :
                print("BEFORE > POST IMAGE_URL : ", post['image_url'])
                post['image_url'] = url_for('static',filename='images/'+ post['image_url'])
                print("AFTER > POST IMAGE_URL : ", post['image_url'])
            print("BEFORE > THUMBNAIL IMAGE_URL : ",first_row['thumbnail_url'] )
            first_row['thumbnail_url'] = url_for('static',filename='thumbnails/'+first_row['thumbnail_url'])
            print("AFTER > THUMBNAIL IMAGE_URL : ",first_row['thumbnail_url'] )
            return render_template('myprofile.html',
                                   user_info=first_row,
                                   post_all=posts)
    else:
        flash('ERROR : something went wrong with your Account!!')
        return redirect('/') 

# プロファイル編集画面へのGETリクエスト
@user.login_required
@app.route('/myprofile/<user_id>/edit')
def myprofile_edit_get(user_id):
    return render_template('myprofile_edit.html',user_id=user_id)

# プロファイル編集画面へのRequestを受理
@user.login_required
@app.route('/myprofile/edit/try', methods=["POST"])
def myprofile_edit():
    user_id = user.session['login']
    name = request.form.get('nickname','')
    introduction = request.form.get('description','')
    thumbnail = request.files['thumbnail_img']
    if not name:
        return render_template("myprofile_edit.html",msg='Nickname is needed')

    if thumbnail:
        # ファイル名が日本語の場合の対応
        # 日本語などの非ASCII文字が含まれるファイル名がsecure_filename関数によって「jpg」などの予期せぬ値に変更されてしまう問題が発生しています。
        # これは、secure_filenameがデフォルトでASCII文字のみを扱い、非ASCII文字を除去するためです。
        # ファイル拡張子を保持
        filename=thumbnail.filename
        _, ext = os.path.splitext(filename)
        # ファイル名をハッシュ化
        hash_name = hashlib.md5(filename.encode('utf-8')).hexdigest()
        print("hashed filename : ", hash_name)
        filename = f"{hash_name}{ext}"
        filename=secure_filename(filename)
        # 問題2: 静的ファイルへのパス指定問題
        # 指定されたパス static/thumbnails/... がブラウザ上でうまく機能しない問題は、
        # Flaskでの静的ファイルのURL生成が正しく行われていないことが原因かもしれません。

        # 解決策
        # Flaskでは、静的ファイルへのURLは url_for ヘルパー関数を使って生成するのが一般的です。
        # これにより、適切なルートが設定され、キャッシュバスティングのクエリ文字列が自動的に付加されることがあります。
        # url_for を使用してファイルへの正確なURLを生成してみてください
        # 画像を保存するディレクトリのパスを指定
        save_user_dir = os.path.join(PROFILE_FILE,user_id)
        if not os.path.exists(save_user_dir):
            os.makedirs(save_user_dir)
        print("profile_file : ", PROFILE_FILE)
        print("save_path : ", save_user_dir)
        print("filename : ", filename)
        save_path = os.path.join(save_user_dir,filename)
        thumbnail.save(save_path)
        save_path_db = user_id+"/"+filename

    if sns_data.save_profile_try(user_id=user_id,nickname=name, description=introduction,thumbnail_url=save_path_db):
        return redirect(url_for('myprofile'))
    else:
        return render_template("myprofile_edit.html",msg='You couldn\'t save profile. Please Try again. ')

# 他人プロファイル画面の詳細画面
@user.login_required
@app.route('/profile/<user_id>')
def profile_others(user_id):
    user_id = user.get_id()
    name = request.form.get('name','')
    introduction = request.form.get('introduction','')
    thumbnail = request.files['image']
    posts = sns_data.get_posts(user_id)
    return render_template('')

# 投稿処理
@app.route('/post')
@user.login_required
def post():
    user_id = session['login']
    user_info = user.user_info(user_id)[0]
    # TODO : debug system
    user_info['thumbnail_url'] = url_for('static', filename='thumbnails/' + user_info['thumbnail_url'])
    return render_template('post.html', user_info=user_info,user_id=user_id)

@app.route('/post/try/<user_id>',methods=['POST'])
@user.login_required
def post_save(user_id):
    result = sns_data.save_post_try(request)
    if result :
        flash('Posting is Succeeded!!!')
        return redirect(url_for('home', user_id=user_id))
    else:
        flash('Posting Failed Try again!!')
        return redirect(url_for('post'))

# 投稿削除
@app.route('/delete_post/<user_id>/<post_id>')
@user.login_required
def delete_login(user_id,post_id):
    user_id = session['login']
    sql="DELETE FROM Post_contents WHERE user_id=? AND post_id=?"
    params = (user_id,post_id)
    sqlite_func.exec(sql, params)
    return redirect(url_for('myprofile', user_id=user_id))

# ユーザ検索機能
@app.route('/search')
@user.login_required
def search():
    return render_template('user_search.html')

@app.route('/search',methods=['POST'])
@user.login_required
def search_try():
    keyword = request.form.get('keyword')
    result = user.get(keyword)
    return render_template('search_result.html', result)




# # 他のユーザを検索する画面
# @user.login_required
# @app.route('/user_search')
# def user_search():
#     return render_template('')

# # プロファイル画面から、フォローしている人を一覧で表示
# @user.login_required
# @app.route('/follow_list/<user_id>')
# def follow_list(user_id):
#     following_users = rel.get_all_following(user_id)
#     return render_template('user_following_list.html', users = following_users)

# # プロファイル画面から、フォローしてくれている人を一覧で表示
# @user.login_required
# @app.route('/follower_list')
# def follower_list(user_id):
#     follower_users = rel.get_all_following(user_id)
#     return render_template('user_following_list.html', users = follower_users)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
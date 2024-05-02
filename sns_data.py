import os,time
from flask import Flask, send_from_directory,flash,request,session,redirect,url_for
from werkzeug.utils import secure_filename
from PIL import Image
import sqlite3
import sqlite_func,hashlib
from datetime import datetime, timedelta

def get_app():
    # 循環参照を避けるために関数の中でappをインポートしてappオブジェクトを戻り値として返す関数
    from app import app
    app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg'}
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit to prevent large uploads
    return app

# ポストされた内容をPostテーブルに保管する処理
def allowed_file(filename):
    app = get_app()
    return '.' in filename and filename.rsplit('.',1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_post_try(request):
    app = get_app()
    user_id = session['login']
    title = request.form.get('title')
    description = request.form.get('description')
    # ファイルが存在している場合は, file名作成処理を行う
    # ユーザ用のフォルダが存在しない時はフォルダを作成する
    if 'post_img' in request.files:
        if  request.files['post_img']!='':
            file = request.files['post_img']
            filename= file.filename
            if allowed_file(filename):
                _, ext = os.path.splitext(filename)
                hash_name = hashlib.md5(filename.encode('utf-8')).hexdigest()
                print("hashed filename : ", hash_name)
                
                filename = f"{hash_name}{ext}"
                print("BEFORE > filename : ", filename)
                filename=secure_filename(filename)
                print("AFTER > filename : ", filename)
                user_id = session['login']
                post_save_dir = os.path.join('static/images',user_id)

                if not os.path.exists(post_save_dir):
                    os.makedirs(post_save_dir)
                
                save_path=os.path.join(post_save_dir,filename)
                image = Image.open(file)
                image.thumbnail((800,800))
                image.save(save_path)
                image_url = user_id+"/"+filename
    else:
        image_url = ""
    # DB処理
    sql='INSERT INTO Post_contents(user_id,title,image_url,description) VALUES (?,?,?,?)'
    args = (user_id,title,image_url,description)
    result = sqlite_func.exec(sql, args)
    return redirect(url_for('home',user_id=user_id))
    
# ユーザ自身のポスト内容を取得する
def get_posts(user_id):
    today = datetime.now().date()
    one_week_ago = today - timedelta(days=7)
    sql='SELECT * FROM Post_contents WHERE user_id = ? ORDER BY post_date DESC'
    result = sqlite_func.select(sql, user_id)
    return result

# conn.close() を実行する理由は、データベースとの接続を適切に閉じることで、リソースの解放とデータの整合性を保つためです。以下にその重要な理由をいくつか挙げます：
# リソースの解放: データベースへの接続はシステムリソース（メモリ、ファイルハンドルなど）を消費します。アプリケーションがデータベース接続を開いたままにしておくと、これらのリソースが不必要に消費され続け、システムのパフォーマンスが低下したり、リソースが枯渇して他の操作ができなくなることがあります。
# データの整合性: データベース操作を行った後、特に書き込み操作（挿入、更新、削除）の場合、適切にトランザクションを閉じることが重要です。conn.close()を呼び出すと、開いているトランザクションが適切に終了し、変更がデータベースに確実に反映されることが保証されます。これにより、データの一貫性と正確さが維持されます。
# 接続のリミット: 多くのデータベースシステムでは、同時に開ける接続数に上限があります。不要な接続を開いたままにしておくと、新しい接続が必要なときにリミットに達してしまい、エラーが発生する可能性があります。適切に接続を閉じることで、新しい接続が必要な際にリソースが利用可能であることを保証します。
# エラーの防止: 接続を開いたままにしてアプリケーションが終了すると、未完了の変更が適切に保存されない可能性があります。これはデータの損失や予期しないエラーの原因となります。
# したがって、データベース接続を閉じることは、リソース管理、データの整合性保持、システムの安定性維持にとって非常に重要です。それにより、アプリケーションの信頼性と効率が向上します

# fetchone(): 通常、クエリによって単一行のみが期待される場合や、結果から1行ずつ順に処理が必要な場合に使用します。
# 使用方法: fetchone() 関数は、カーソルが指向する結果セットから次の行を取得します。もし結果セットにこれ以上の行がない場合は None を返します。
# fetchall(): 結果セットの全行が必要な場合、特に小規模なデータセットの処理や分析に適しています。大規模な結果セットでの使用は、メモリの消費が大きくなるため注意が必要です。
# 使用方法: fetchall() 関数は、カーソルが指向する結果セットにあるすべての行をリストとして返します。結果セットが空の場合、空のリストが返されます。

def save_profile_try(user_id,nickname,description,thumbnail_url):
    sql = 'UPDATE Users SET nickname = ?, description = ?, thumbnail_url = ? WHERE user_id = ?'
    params = (nickname, description, thumbnail_url, user_id)
    result = sqlite_func.exec(sql,params)
    if result != None or result != "":
        return True
    else:
        return False
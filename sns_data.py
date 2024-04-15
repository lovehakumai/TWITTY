import os,time
from flask import Flask, send_from_directory,flash,request,session,redirect,url_for
from werkzeug.utils import secure_filename
from PIL import Image
import sqlite3
import sqlite_func
from app import app
from datetime import datetime, timedelta

app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit to prevent large uploads


# ポストされた内容をPostテーブルに保管する処理
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_post(user_id,title,description):
    if 'image' not in request.files:
        flash('No file part')
        return redirect(url_for('post'))
    
    file = request.files['image']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('post'))
    
    if file and allowed_file(file.filename):
        filename=secure_filename(file.filename)
        user_path = os.path.join(app.config['UPLOAD_FOLDER'],user_id)
        if not os.path.exists(user_path):
            os.makedirs(user_path)
        file_path=os.path.join(user_path,filename)

        image = Image.open(file)
        image.thumbnail((800,800))
        image.save(file_path)

        # DB処理
        conn = sqlite3.connect(sqlite_func.DB_FILE)
        c = conn.cursor()
        c.execute('INSERT INTO Post_contents(user_id,title,image_url,description) VALUES (?,?,?,?)'.format(user_id,title,file_path,description))
        conn.close()
        return redirect(url_for('home',user_id=user_id))
    else:
        flash('Allowed file types are .jpg, jpeg')
        return redirect(url_for('post',user_id=user_id))
    
# ユーザ自身のポスト内容を取得する
def get_posts(user_id):
    today = datetime.now().date()
    one_week_ago = today - timedelta(days=7)

    conn = sqlite3.conn()
    c = conn.cursor()
    c.execute('SELECT * FROM Post_Contents WHERE user_id=? AND post_date BETWEEN ? AND ? ORDER BY post_date DESC'.format(user_id, today,one_week_ago ))
    result = c.fetchall()
    conn.close()
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

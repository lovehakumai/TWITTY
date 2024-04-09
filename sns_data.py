import os
from flask import Flask, send_from_directory,flash,request,session,redirect,url_for
from werkzeug.utils import secure_filename
from PIL import Image
import sqlite3
import sqlite_func
from app import app

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
        c.execute('INSERT INTO Post_contents(user_id,title,image_url,description) VALUES (?,?,?,?)'.format(user_id,title,file_path,desctiption))
        return redirect(url_for('home',user_id=user_id))
    else:
        flash('Allowed file types are .jpg, jpeg')
        return redirect(url_for('post',user_id=user_id))
    



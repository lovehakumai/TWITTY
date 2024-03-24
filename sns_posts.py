from flask import Flask,render_template,session

# 1 - User_idを引数にそのユーザのポスト投稿内容の行を取得する。
# 2 - User_idのフォローしているユーザIDの一覧を取得
# 3 - フォローしているユーザと自分の投稿内容リストを、投稿日時順に降順に並べ替えて取得する
# home.htmlで投稿内容の一覧をページング表示する


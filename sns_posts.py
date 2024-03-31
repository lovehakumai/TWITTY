from flask import Flask,render_template,session
import sqlite3
from sqlite_func import exec, select

# 1 - User_idを引数にそのユーザのポスト投稿内容の行を取得する。
# 2 - User_idのフォローしているユーザIDの一覧を取得
# 3 - フォローしているユーザと自分の投稿内容リストを、投稿日時順に降順に並べ替えて取得する
# home.htmlで投稿内容の一覧をページング表示する


def get_posts(user_id):
    # ユーザーのIDの一覧を取得
    following_id_list = {}
    post_list = {}
    temp_list = select(
        'SELECT follow_to FROM Relations WHERE followed_by=?',
        user_id
    )
    if len(temp_list)==0:
        return None
    else:
        following_id_list=temp_list
        # following_id_listの複数のUser_idをリスト型にまとめる
        user_ids = [item['follow_to'] for item in following_id_list]
        
        # クエリのプレースホルダーの文字列を生成する(?,?,~)
        # '?' for _ in user_idsは、
        # user_idsリストの各要素に対して繰り返しを行い、
        # 各繰り返しで?を生成しています。
        # ここでの_（アンダースコア）は、
        # ループの各イテレーションで使用される値を無視するための慣用的な記法です
        # （この場合、リストの各要素自体は関係なく、単に要素の数だけ?を生成したいため）。
        placeholders = ','.join('?' for _ in user_ids)
        post_dict = {}
        temp_post_dict = select(
            'SELECT * FROM Post_contents WHERE user_id IN ({placeholders})'
            , *user_ids
            )
         #*user_idsにおけるアスタリスク（*）は、Pythonにおける「アンパック演算子」です。
        # この演算子は、リストやタプルなどのイテラブル（反復可能オブジェクト）を、
        # 関数呼び出しの際に複数の引数として展開するために使用されます。
        # つまり、*を使ってuser_idsリストをselect関数に渡すと、リ
        # スト内の各要素が個別の引数として関数に渡されることになります。
        #この記法は、関数が可変長引数を受け取る場合に特に有用です。
        #select関数がSQLクエリと、それに続く任意の数のパラメータを受け取るよう設計されている場合、
        #*を使って引数リストをアンパックすることで、リストの各要素を個別の引数として渡すことができます。
        if len(temp_post_dict)==0:
            return None
        else:
            post_list=temp_post_dict
            # post情報を取得するための post_idのリストを作成
            post_ids = tuple(item['post_id'] for item in post_list)
            post_info_list = {}
            temp_post_infos = select(
            'SELECT post_id, MAX(reply_no) as reply_max_no FROM Post_communications where post_id IN ({placeholders_post}) GROUP BY 1'
            ,post_ids
            )
            post_info_list=temp_post_infos
            
            # post_listとpost_infoを一つのデータに左外部結合する準備
            # 右テーブルのデータを post_idをキーとする辞書に変換する
            right_table_dict = {item['post_id']: item for item in post_info_list}
            # 左外部結合
            joined_data_post_info = []
            for post_item in post_list:
                post_id = post_item["post_id"] # 左テーブルのpost_idの値を取得
                right_item = right_table_dict.get(post_id, {"reply_max_no": None}) # もし左テーブルの行nに同じpost_idがあれば辞書型で{post_id:n, reply_max_no:5}を返す。なければreply_max_noはNoneになる
                joined_item = post_item.copy() # 左テーブルの元データ1行を変更しないようにコピーを行う
                joined_item.update({k: v for k, v in right_item.items() if k !="post_id"}) # その一行に対して、上記における右テーブルから作成した{post_id:n, reply_max_no:5orNone}をupdate():追加する。post_idは不要なのでif k != "post_id"で排除しておく
                joined_data_post_info.append(joined_item) # リスト型のデータjoined_dataに上記で作成したデータを追加s流


            # user_情報左外部結合 / ユーザのプロファイルからnicknameが欲しかった。
            user_info_list = select(
                "SELECT * from Users WHERE user_id=?",
                user_id
            )
            right_table_dict_user_info = {item['user_id']: item for item in user_info_list}
            joined_data_user_info=[]
            for row in joined_data_post_info:
                user_id = row['user_id']
                right_item = right_table_dict_user_info.get(user_id,{'nickname':None})
                joined_item = row.copy()
                joined_item.update({k: v for k, v in right_item.items() if k != "user_id"})
                joined_data_post_info.append(joined_item)
            
            return joined_data_user_info

            


import os, sqlite3

# パスの指定
BASE_DIR = os.path.dirname(__file__)
DB_FILE = BASE_DIR + '/sqlite/db.sqlite3'


def open_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = dict_factory
    return conn

# SWLWCT句の結果を辞書で得られるようにする
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
        print(d) # test
    return d

# SQLを実行する時
def exec(sql, *args):
    db = open_db()
    c = db.cursor()
    c.execute(sql, args)
    db.commit()
    return c.lastrowid

# SQLを実行して結果を得る
def select(sql, *args):
    db = open_db()
    c = db.cursor()
    c.execute(sql, args)
    return c.fetchall()

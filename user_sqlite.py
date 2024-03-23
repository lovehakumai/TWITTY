import os, sqlite3

# パスの指定
BASE_DIR = os.path.dirname(__file__)
USER_FILE = BASE_DIR + '/sqlite/Users.sqlite3'
RELATION_FILE = BASE_DIR + '/sqlite/Relations.sqlite3'
POST_CONTENT_FILE = BASE_DIR + '/sqlite/Post_contents.sqlite3'
POST_COMMUNICATION_FILE = BASE_DIR + '/sqlite/Post_communications.sqlite3'


def open_db():
    conn = sqlite3.connect()

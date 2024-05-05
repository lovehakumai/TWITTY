import sqlite3
import sqlite_func

def get(followed_by,follow_to):
    if followed_by==follow_to:
        return False
    sql = 'SELECT * FROM Relations where followed_by=? AND follow_to=?'
    result = sqlite_func.select(sql,followed_by,follow_to)
    if len(result)>0:
        return True
    else:
        return False
    

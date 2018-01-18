import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn = sqlite3.connect('my_db.sqlite3', check_same_thread=False)

conn.row_factory = dict_factory
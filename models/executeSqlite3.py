# -*- coding:utf-8 -*-

from sqlite3 import IntegrityError
# from models import conn
from models import conn


def executeSelectOne(sql):

    curs = conn.cursor()
    curs.execute(sql)
    data = curs.fetchone()

    return data

def executeSelectAll(sql):

    curs = conn.cursor()
    curs.execute(sql)
    data = curs.fetchall()

    return data

def executeSQL(sql):
    try:
        print('executeSQL = {}'.format(sql))
        curs = conn.cursor()
        curs.execute(sql)
        conn.commit()
        return curs.lastrowid
    except IntegrityError:
        return False




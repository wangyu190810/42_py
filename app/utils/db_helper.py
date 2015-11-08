#! -*- coding:utf8 -*-

import MySQLdb
import Queue

def singleton(cls, *args, **kw):
    instances = {}
    def _singleton(*args):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton


@singleton
class DB42(object):
    ''' FIXME 单例数据库连接池 '''
    def __init__(self, host='127.0.0.1', port=3306, user='root',passwd=None, db=None, pool_size=8):
        self._conn_pool = Queue.Queue()
        # 数据库连接配置
        self._config = cn = {}
        cn['host'] = host
        cn['port'] = port
        cn['user'] = user
        cn['passwd'] = passwd
        cn['db'] = db
        self._pool_size = pool_size
        for i in range(self._pool_size):
            _conn = MySQLdb.connect(use_unicode=True, charset='utf8', host='127.0.0.1',port=3306,user='root',passwd='qweasd',db=db)
            _conn.autocommit(True)
            self._conn_pool.put(_conn)

    def get_cursor(self):
        conn_pool = self._conn_pool
        # FIXME is multi-thread safe ?
        try:
            if conn_pool.empty():
                for i in range(self._pool_size):
                    _conn = MySQLdb.connect(use_unicode=True, charset='utf8', **self._config)
                    _conn.autocommit(True)
                    if not conn_pool.full():
                        _conn_pool.put(_conn)
            conn = conn_pool.get()
            if conn:
                if not conn_pool.full():
                    conn_pool.put(conn) # 将连接还给连接池, 没办法，不知道怎么封装到多线程环境中，。。。😢
                return conn.cursor()
        except Exception as e:
            raise e

    # update
    def update(self, sql, argvs=None):
        cursor = self.get_cursor(self)
        try:
            result_sz = cursor.execute(sql, argvs)
            if result_sz > 1:
                return cursor.fetchall()
            else:
                return cursor.fetchone()
        finally:
            cursor.close()
    # query
    def query(self, sql, argvs=None):
        cursor = self.get_cursor()
        try:
            result_sz = cursor.execute(sql, argvs)
            if result_sz > 1:
                return cursor.fetchall()
            else:
                return cursor.fetchone()
        finally:
            cursor.close()
    # 关闭所有连接
    def stop(self):
        conn_pool = self._conn_pool
        while not conn_pool.empty():
            conn = conn_pool.get()
            conn.close()


if __name__ == '__main__':
    db1 = DB42('127.0.0.1',3306,'root','qweasd','user')
    db2 = DB42('127.0.0.1',3306,'root','qweasd','test')# FIXME
    print id(db1)
    print id(db2)
    print db1 == db2
    print db1 is db2
    cur = db1.get_cursor()
    cur.execute("select * from user_passport")
    print cur.fetchall()
    cur.execute('show tables')
    print cur.fetchall()
    cur.close()
    db1.stop()

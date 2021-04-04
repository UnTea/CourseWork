import psycopg2
from psycopg2.sql import SQL, Literal, Identifier

def make_arg_placeholders(n):
    return ','.join(['%s'] * n)

class Database:
    def __init__(self, user, password):
        self.conn = psycopg2.connect(dbname='coursework',
                                     user=user,
                                     password=password,
                                     host='localhost',
                                     port='5432')
        self.cursor = self.conn.cursor()

        self.conn.commit()

    def call(self, func, args):
        arg_placeholders = f'({make_arg_placeholders(len(args))})'
        call = SQL('call {}' + arg_placeholders).format(Identifier(func))
        self.cursor.execute(call, args)
        self.conn.commit()

    def fetch_all(self, query, *args):
        self.cursor.execute(query, (*args,))
        return list(self.cursor.fetchall())

    def close(self):
        self.cursor.close()
        self.conn.close()

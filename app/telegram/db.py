import psycopg2


class Database:
    def __init__(self, dsn):
        self.conn = psycopg2.connect(dsn)
        self.cursor = self.conn.cursor()

    def fetchall(self, query, *params):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetchone(self, query, *params):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def execute(self, query, *params):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return True
        except (Exception, psycopg2.Error) as error:
            print("Ошибка при выполнении запроса:", error)
            self.conn.rollback()
            return False

    def close(self):
        self.cursor.close()
        self.conn.close()


dsn = 'dbname=bot user=postgres password=password host=localhost'
db = Database(dsn)

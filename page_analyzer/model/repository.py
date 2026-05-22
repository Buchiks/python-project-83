import psycopg2
import requests
from psycopg2.extras import DictCursor


def get_db(app):
    return psycopg2.connect(app.config['DATABASE_URL'])


class UrlRepository:
    def __init__(self, conn):
        self.conn = conn
    
    def get_content(self):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            sql = "SELECT MAX(ch.created_at) as last_date, urls.name, urls.id" \
            " FROM urls LEFT JOIN url_checks as ch " \
            "ON ch.url_id = urls.id GROUP BY urls.id, urls.name ORDER BY id"
            cur.execute(sql)
            return [dict(row) for row in cur]
    
    def find(self, id):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE id=%s", (id,))
            row = cur.fetchone()
            return dict(row) if row else None
    
    def does_exist(self, url):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT id FROM urls WHERE name = %s",
                         (url["name"],))
            id = cur.fetchone()
            if id:
                url["id"] = id["id"]
                return True
            else:
                return False
                
    
    def save(self, url):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO urls (name) VALUES (%s) RETURNING id",
                         (url["name"],))
            id = cur.fetchone()[0]
            url["id"] = id
        self.conn.commit()

    def get_check_content(self, url):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM url_checks WHERE url_id=%s", 
                        (url["id"],))
            return [dict(row) for row in cur]
    
    def check(self, url):
        response = requests.get(url["name"])
        response.raise_for_status()
        status_code = response.status_code
        with self.conn.cursor() as cur:
            cur.execute('''INSERT INTO url_checks (url_id, status_code)
                        VALUES (%s, %s)''', (url["id"], status_code,))
        self.conn.commit()

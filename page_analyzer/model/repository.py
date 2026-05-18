import psycopg2
from psycopg2.extras import DictCursor


def get_db(app):
    return psycopg2.connect(app.config['DATABASE_URL'])


class UrlRepository:
    def __init__(self, conn):
        self.conn = conn
    
    def get_content(self):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * from urls")
            return [dict(row) for row in cur]
    
    def find(self, id):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * from urls WHERE id=%s", (id,))
            row = cur.fetchone()
            return dict(row) if row else None
    
    def get_by_term(self, search_term=""):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM urls " \
            "WHERE url ILIKE %s", (f"%{search_term}%",))
            return cur.fetchall()
    
    def save(self, url):
        if "id" in url and url["id"]:
            return url["id"]
        else:
            self._create(url)
    
    def _create(self, url):
        
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO urls (name) VALUES (%s) RETURNING id", (url["name"],))
            id = cur.fetchone()[0]
            url["id"] = id
        self.conn.commit()

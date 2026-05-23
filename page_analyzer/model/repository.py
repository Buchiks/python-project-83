from urllib.parse import urlparse, urlunparse

import psycopg2
import requests
from bs4 import BeautifulSoup
from psycopg2.extras import DictCursor


def get_db(app):
    return psycopg2.connect(app.config['DATABASE_URL'])


class UrlRepository:
    def __init__(self, conn):
        self.conn = conn
    
    def get_content(self):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            sql = "SELECT DISTINCT ON (urls.id) " \
            "ch.created_at as last_date, ch.status_code, urls.name, urls.id" \
            " FROM urls LEFT JOIN url_checks as ch " \
            "ON ch.url_id = urls.id ORDER BY urls.id, ch.created_at DESC"
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
        html = BeautifulSoup(response.text, "html.parser")
        h1 = html.h1.string if html.h1 else None
        title = html.title.string if html.title else None
        meta = html.find("meta", {"name": "description"})
        if meta and "content" in meta.attrs:
            description = meta["content"]
        else:
            description = None
        with self.conn.cursor() as cur:
            cur.execute('''INSERT INTO url_checks (url_id, status_code, 
                        h1, title, description)
                        VALUES (%s, %s, %s, %s, %s)''', 
                        (url["id"], status_code, h1, title, description)
                        )
        self.conn.commit()

    def normalize(self, url):
        parsed = urlparse(url["name"])
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        url["name"] = urlunparse((scheme, netloc, '', '', '', ''))
        return 

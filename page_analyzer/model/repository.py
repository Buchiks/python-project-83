from urllib.parse import urlparse, urlunparse
from .db import get_db, Urls, UrlCheck
from sqlalchemy import desc
import requests
from bs4 import BeautifulSoup


class UrlRepository:

    def get_content(self):
        db = get_db()
        try:
            urls = db.query(Urls).order_by(Urls.id).all()
            result = []
            for url in urls:
                last_check = db.query(UrlCheck).filter(
                    UrlCheck.url_id == url.id
                ).order_by(desc(UrlCheck.created_at)).first()
                result.append({
                    "id": url.id,
                    "name": url.name,
                    "last_date": last_check.created_at if last_check else None,
                    "status_code": last_check.status_code if last_check else None
                })
            return result
        finally:
            db.close()
    
    def find(self, id):
        db = get_db()
        try:
            url = db.query(Urls).filter(Urls.id == id).first()
            if url:
                return {"id": url.id, "name": url.name}
            return None
        finally:
            db.close()
    
    def does_exist(self, url):
        db = get_db()
        try:
            exist = db.query(Urls).filter(Urls.name == url["name"]).first()
            if exist:
                url["id"] = exist.id
                return True
            return False
        finally:
            db.close()
                
    def save(self, url):
        db = get_db()
        try:
            new_url = Urls(name=url["name"])
            db.add(new_url)
            db.commit()
            db.refresh(new_url)
            url["id"] = new_url.id
        finally:
            db.close()
        

    def get_check_content(self, url):
        db = get_db()
        try:
            checks = db.query(UrlCheck).filter(
                UrlCheck.url_id == url["id"]
            ).order_by(UrlCheck.created_at).all() 
            return [{
                "id": c.id,
                "url_id": c.url_id,
                "status_code": c.status_code,
                "h1": c.h1,
                "title": c.title,
                "description": c.description,
                "created_at": c.created_at
            } for c in checks]
        finally:
            db.close()
    
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
        
        db = get_db()
        try:
            check = UrlCheck(
                url_id=url["id"],
                status_code=status_code,
                h1=h1,
                title=title,
                description=description
            )
            db.add(check)
            db.commit()
        finally:
            db.close()

    def normalize(self, url):
        parsed = urlparse(url["name"])
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        url["name"] = urlunparse((scheme, netloc, '', '', '', ''))
        return 

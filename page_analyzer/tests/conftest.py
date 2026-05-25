import os
import pytest
import shutil
import tempfile
from dotenv import load_dotenv
from flask import Flask
from pathlib import Path

from page_analyzer.model import UrlRepository
from page_analyzer.model.db import Urls, UrlCheck



@pytest.fixture(scope="session")
def app():

    
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "test_key"
    app.config["TESTING"] = True
    return app


@pytest.fixture
def repo(app):

    temp_dir = tempfile.mkdtemp()
    test_db_path = Path(temp_dir) / "test.db"
    
    original_db_url = os.getenv("SQLite_DATABASE_URL")
    
    os.environ["SQLite_DATABASE_URL"] = f"sqlite:///{test_db_path}"
    
    from page_analyzer.model import db
    import importlib
    importlib.reload(db)
    
    db.Base.metadata.create_all(bind=db.engine)
    
    repo = UrlRepository()
    
    yield repo

    db.SessionLocal().close_all()
    test_db_path.unlink(missing_ok=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    if original_db_url:
        os.environ["SQLite_DATABASE_URL"] = original_db_url
    else:
        os.environ.pop("SQLite_DATABASE_URL", None)
    
    importlib.reload(db)




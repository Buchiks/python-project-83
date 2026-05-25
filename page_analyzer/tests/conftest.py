import os
import shutil
import tempfile
from pathlib import Path

import pytest
from flask import Flask

from page_analyzer.model import UrlRepository


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
    
    import importlib

    from page_analyzer.model import db
    
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




import os

import psycopg2
import pytest
from dotenv import load_dotenv
from flask import Flask

from page_analyzer.model import UrlRepository

load_dotenv()


@pytest.fixture(scope="session")
def app():

    app = Flask(__name__)

    app.config["SECRET_KEY"] = "test_key"
    app.config["TESTING"] = True
    return app


@pytest.fixture
def connection(app):
    TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
    conn = psycopg2.connect(TEST_DATABASE_URL)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE urls, url_checks RESTART IDENTITY CASCADE")
            cur.execute("BEGIN")
    
        yield conn

    finally:
        conn.rollback()
        conn.close()


@pytest.fixture
def repo(connection):
    return UrlRepository(connection)

import os

import psycopg2
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)
from requests import HTTPError
from validators import url as validate

from .model import UrlRepository

load_dotenv()


app = Flask(__name__)


app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)

repo = UrlRepository(conn)


@app.route("/")
def index():
    return render_template("index.html", url="", errors="1")


@app.route("/urls")
def show():
    urls = repo.get_content()
    return render_template("show.html", urls=urls)


@app.post("/urls")
def add_site():
    url = request.form.to_dict("url")
    no_errors = validate(url["name"])

    if not no_errors:
        return render_template("index.html", url=url, errors=no_errors)
    repo.save(url)
    flash("Url was added succesfully", "alert-success")
    return redirect(url_for("url_show", id=url["id"]))


@app.route("/urls/<int:id>")
def url_show(id):
    url = repo.find(id)
    if not url:
        abort(404)
    checks = repo.get_check_content(url)
    message = get_flashed_messages(with_categories=True)
    return render_template("show_id.html", url=url, 
                           checks=checks, message=message)


@app.post("/urls/<int:id>/checks")
def url_check(id):
    url = repo.find(id)
    try:
        repo.check(url)
    except HTTPError:
        flash("Произошла ошибка при проверке", "alert-danger")
    return redirect(url_for("url_show", id=url["id"]))
    
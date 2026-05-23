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
from requests import RequestException
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
    
    return render_template("index.html", url="", errors="")


@app.route("/urls")
def show():
    urls = repo.get_content()
    return render_template("show.html", urls=urls)


@app.post("/urls")
def add_site():
    data = request.form.to_dict()
    url = {}
    url["name"] = data["url"]
    no_errors = validate(url["name"])

    if not no_errors:
        message = "Некорректный URL"
        return render_template("index.html", url=url, errors=message), 422

    repo.normalize(url)

    if repo.does_exist(url):
        flash("Страница уже существует", "alert-info")
    else:
        repo.save(url)
        flash("Страница успешно добавлена", "alert-success")
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
    if not url:
        abort(404)
    try:
        repo.check(url)
        flash("Страница успешно проверена", "alert-success")
    except RequestException:
        flash("Произошла ошибка при проверке", "alert-danger")
    return redirect(url_for("url_show", id=url["id"]))
    
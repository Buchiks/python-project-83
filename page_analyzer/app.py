import psycopg2
import os


from flask import Flask, render_template, url_for, request, flash, redirect, abort
from dotenv import load_dotenv
from .model import UrlRepository
from validators import url as validate

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
    flash("Url was added succesfully", "success")
    return redirect(url_for("url_show", id=url["id"]))

@app.route("/urls/<int:id>")
def url_show(id):
    url = repo.find(id)
    if not url:
        abort(404)
    return render_template("show_id.html", url=url)
    
import os

from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy


# path = "__main__"
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "PostGresSQL"


@app.route("/")
def home():
    try:
        url = os.getenv("DATABASE_URL")
    except:
        url = "URL не был изъят"
    data = {
        "URL": url
    }
    return render_template("home.html", data=data)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/user/<string:name>/<int:id_>")
def user_page(name, id_):
    data = {
        "name": name,
        "id": id_
    }
    return render_template("user_page.html", data=data)


@app.route("/<string:username>/chats")
def chats(username):
    data = {
        "username": "Oleg",
        "chats": [
            "Jamil",
            "Rasul",
            "Ilon Mask",
            "Bill Gates"
        ]
    }
    return render_template("chats.html", data=data)


@app.route("/<string:username>/friends")
def friends(username):
    data = {
        "username": "Oleg",
        "friends": [
            "Jamil",
            "Rasul",
            "Bill Gates"
        ]
    }
    return render_template("friends.html", data=data)


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/login")
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
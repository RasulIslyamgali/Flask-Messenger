import os
from datetime import datetime

from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy


# path = "__main__"
app = Flask(__name__)
URI = os.getenv("DATABASE_URL").replace(__old="postgres", __new="postgresql")
app.config["SQLALCHEMY_DATABASE_URI"] = URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(db.Model):
    id_ = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.DateTime)
    country = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    date_of_register = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f"<User username: {self.username} id: {self.id_}>"



@app.route("/")
def home():
    return render_template("home.html")


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


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        lastname = request.form["lastname"]
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]

        user = User(name=name, lastname=lastname, username=username, password=password, email=email)

        try:
            db.session.add(user)
            db.session.commit()
            return redirect("/")
        except:
            return "При добавлении статьи произошла ошибка"
    else:
        return render_template("register.html")


@app.route("/login")
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
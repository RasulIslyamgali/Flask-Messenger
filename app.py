import json
import os
from datetime import datetime

from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv


load_dotenv()  # this method required for extract data from local .env file

# path = "__main__"
app = Flask(__name__)
app.secret_key = os.getenv("SEKRET_KEY")

URI = os.getenv("DATABASE_URL").replace("postgres", "postgresql")
app.config["SQLALCHEMY_DATABASE_URI"] = URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)


class User(db.Model, UserMixin):
    id_ = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(10000), nullable=False)
    date_of_birth = db.Column(db.DateTime)
    country = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    date_of_register = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        data = {"username": self.username, "name": self.name, "id": self.id_, "lastname": self.lastname}
        return f'{data}'

    def get_id(self):
        return self.id_


@app.context_processor
def check_user():
    if session.get("user", None) is not None:
        return dict(user_active=json.loads(session.get("user", None).replace("'", '"')))
    else:
        return dict(user_active=session.get("user", None))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/user/<string:username>/<int:id>")
@login_required
def user_page(username, id):
    data = json.loads(session["user"].replace("'", '"'))
    return render_template("user_page.html", data=data)


@app.route("/<string:username>/chats")
@login_required
def chats(username):
    data = json.loads(session["user"].replace("'", '"'))
    return render_template("chats.html", data=data)


@app.route("/<string:username>/friends")
@login_required
def friends(username):
    data = json.loads(session["user"].replace("'", '"'))
    return render_template("friends.html", data=data)


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        lastname = request.form.get("lastname")
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        if not (name and username and password):
            flash("Пожалуйста заполните все необходимые поля")
        else:
            hash_pwd = generate_password_hash(password)
            if email:
                new_user = User(name=name, lastname=lastname, username=username, password=hash_pwd, email=email)
            else:
                new_user = User(name=name, lastname=lastname, username=username, password=hash_pwd)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login_page"))
        except Exception as e:
            print(f'[INFO] Register exception: {e}')
            if "(psycopg2.errors.UniqueViolation)" in str(e) and "user_username_key" in str(e):
                flash("Пользователь с таким именем уже существует. Пожалуйста придумайте другую")
            elif "psycopg2.errors.UniqueViolation" in str(e) and "user_email_key" in str(e):
                flash("Эта почта уже используется другим пользователем. Пожалуйста выберите другую")
            else:
                flash("При добавлении статьи произошла ошибка")
            return redirect(url_for("register"))
    else:
        return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login_page():
    login_ = request.form.get("username")
    password = request.form.get("password")

    if login_ and password:
        # это значит пользователь зареганный
        user = User.query.filter_by(username=login_).first()

        if user and check_password_hash(user.password, password=password):
            login_user(user)

            next_ = request.args.get("next", "/")
            # it's return last page before redirect to login page
            # this "next" we added in func redirect_to_sign_in

            # сохраняем юзера в сессию, чтобы потом рендерить или скрыть разные части темплейтов
            session["user"] = repr(user)
            return redirect(next_)
        else:
            flash("Пожалуйста введите правильный пароль и имя пользователя")
    else:
        flash("Пожалуйста введите пароль и имя пользователя")
    return render_template("login.html")


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()

    # удаляем username из session
    del session["user"]

    return redirect(url_for("home"))


@app.after_request
def redirect_to_sign_in(response):
    if response.status_code == 401 and "logout" not in request.url:
        return redirect(url_for("login_page") + f"?next={request.url}")
    elif response.status_code == 401 and "logout" in request.url:
        return redirect(url_for("home") + f"?next={request.url}")

    return response


if __name__ == "__main__":
    app.run(debug=True)
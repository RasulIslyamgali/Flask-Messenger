import os
from datetime import datetime

from flask import Flask, render_template, url_for, request, redirect, flash
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
        return f"<User username: {self.username} id: {self.id_}>"

    def get_id(self):
        return self.id_


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/user/<string:name>/<int:id_>")
@login_required
def user_page(name, id_):
    data = {
        "name": name,
        "id": id_
    }
    return render_template("user_page.html", data=data)


@app.route("/<string:username>/chats")
@login_required
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
@login_required
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
        name = request.form.get("name")
        lastname = request.form.get("lastname")
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        if not (name and username and password):
            flash("Пожалуйста заполните все необходимые поля")
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(name=name, lastname=lastname, username=username, password=hash_pwd, email=email)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login_page"))
        except Exception as e:
            print(f'[INFO] Register exception: {e}')
            return "При добавлении статьи произошла ошибка"
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
            return redirect(next_)
        else:
            flash("Пожалуйста введите правильный пароль и имя пользователя")
    else:
        flash("Пожалуйста введите пароль и имя пользователя")
    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.after_request
def redirect_to_sign_in(response):
    if response.status_code == 401:
        return redirect(url_for("login_page") + f"?next={request.url}")

    return response


if __name__ == "__main__":
    app.run(debug=True)
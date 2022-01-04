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
        data = {"model": self.__class__.__name__,
                "username": self.username,
                "name": self.name,
                "id_": self.id_,
                "lastname": self.lastname
                }

        return f'{data}'

    def get_id(self):
        return self.id_


class Chat(db.Model, UserMixin):
    __tablename__ = "chat"

    chat_id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime, default=datetime.utcnow())

    user_id = db.Column(db.Integer, db.ForeignKey("user.id_"))
    # user = db.relationship("User", backref=db.backref("user", uselist=False))

    user_2_id = db.Column(db.Integer, db.ForeignKey("user.id_"))
    user_2_name = db.Column(db.String(255))

    def __repr__(self):
        data = {
            "model": self.__class__.__name__,
            "chat_id": self.chat_id,
            "user_id": self.user_id,
            "user_2_id": self.user_2_id,
            "user_2_name": self.user_2_name
        }
        return f"{data}"

    def get_id(self):
        return self.chat_id


class Message(db.Model, UserMixin):
    __tablename__  = "message"

    message_id = db.Column(db.Integer, primary_key=True)
    message_text = db.Column(db.Text, nullable=False)
    create_date = db.Column(db.Text, default=datetime.utcnow())

    chat_id = db.Column(db.Integer, db.ForeignKey("chat.chat_id"))
    # chat = db.relationship("chat", backref=db.backref("chat", uselist=False))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id_"))
    # user = db.relationship("User", backref=db.backref("user", uselist=False))

    def __repr__(self):
        data = {
            "model": self.__class__.__name__,
            "message_id": self.message_id,
            "message_text": self.message_text,
            "chat_id": self.chat_id,
            "user_id": self.user_id,
            "create_date": self.create_date
        }

        return f"{data}"

    def get_id(self):
        return self.message_id


@app.context_processor
def check_user():
    """эта функция передает data к base.html
    если user в session есть, передаются его данные
    если нет, передается None
    И исходя из этого какие то части base.html будут рендериться,
    а какие то hide"""
    data = session.get("user", None)

    if data is not None:
        return dict(user_active=json.loads(data.replace("'", '"')))
    else:
        return dict(user_active=data)


@app.route("/chat/with/user/<string:username>", methods=["GET", "POST"])
def chat_with_user(username):
    user_id = json.loads(session.get("user").replace("'", '"'))["id_"]
    current_user = json.loads(session.get("user").replace("'", '"'))["username"]
    print("user id is", user_id)
    query = fr"""SELECT "user".id_ FROM "user" WHERE "user".username = '{username}';"""
    user_2_id = db.engine.execute(query).first()[0]

    if request.method == "POST":
        message_text = request.form.get("send_message")
        sql = fr"""SELECT "chat".chat_id, "chat".user_2_id FROM "chat" WHERE ("chat".user_2_name='{username}' AND "chat".user_id={user_id}) OR ("chat".user_id={user_2_id} AND "chat".user_2_name = '{current_user}');"""
        # сначала получаю чат id
        try:
            chat_id, user_2_id = db.engine.execute(sql).first()
        except TypeError:
            # это если первое сообщение и чат создается

            new_chat = Chat(user_id=user_id, user_2_id=user_2_id, user_2_name=username)
            db.session.add(new_chat)
            db.session.commit()

            chat_id, user_2_id = db.engine.execute(sql).first()

        new_message = Message(chat_id=chat_id, user_id=user_id, message_text=message_text)
        db.session.add(new_message)
        db.session.commit()

        sql = fr"""SELECT "message".message_text, "message".create_date, "message".user_id FROM "message" WHERE chat_id={chat_id};"""
        messages = db.engine.execute(sql).all()
        print("messages", messages)
        data = {
            "chat_exist": 1,
            "chat_id": chat_id,
            "username": username,  # имя собеседника
            "messages": messages,
            "user_2_id": user_2_id,
            "current_user": current_user,
            "user_id": user_id
        }

        return render_template("chat_with_user.html", data=data)
    else:
        print("123", username, user_id, user_2_id, current_user)
        sql = fr"""SELECT "chat".chat_id, "chat".user_2_id FROM "chat" WHERE ("chat".user_2_name='{username}' AND "chat".user_id={user_id}) OR ("chat".user_id={user_2_id} AND "chat".user_2_name = '{current_user}');"""
        # сначала получаю чат id
        try:
            chat_id, user_2_id = db.engine.execute(sql).first()
            print("))", chat_id, user_2_id)
        except TypeError:
            print("++", user_2_id)
            chat_id = None

        if chat_id:
            # если чат есть, то отображаем сообщения в нем
            sql = fr"""SELECT "message".message_text, "message".create_date, "message".user_id FROM "message" WHERE chat_id={chat_id};"""
            messages = db.engine.execute(sql).all()

            data = {
                "chat_exist": 1,
                "chat_id": chat_id,
                "username": username,  # имя собеседника
                "messages": messages,
                "user_2_id": user_2_id,
                "current_user": current_user,
                "user_id": user_id
            }
            return render_template("chat_with_user.html", data=data)
        else:
            # если чата нету, то скажем что пока сообщение нету, и попросить приветствовать, типа как в телеграме
            data = {
                "chat_exist": None,
                "chat_id": chat_id,
                "username": username,  # имя собеседника
                "user_2_id": user_2_id,
                "current_user": current_user,
                "user_id": user_id
            }
            return render_template("chat_with_user.html", data=data)


@app.route("/<string:username>/page")
def some_user_page(username):
    sql = fr"""SELECT "user".name, "user".lastname FROM "user" WHERE "user".username='{username}';"""
    name, lastname = db.engine.execute(sql).first()
    data = {
        "username": username,
        "name": name,
        "lastname": lastname
    }
    return render_template("some_user_page.html", data=data)


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        query_text = request.form.get("search_query", None)
        id_ = json.loads(session.get("user").replace("'", '"'))["id_"]
        sql = f"SELECT \"user\".username, \"user\".id_ FROM \"user\" WHERE (\"user\".username LIKE '%%{query_text}%%' OR \"user\".username LIKE '{query_text}%%') AND \"user\".id_ != {id_};"
        users = db.engine.execute(sql).all()
        if users:
            pass
        else:
            flash(f"По запросу '{query_text}' ничего не было найдено")
            return render_template("search_page.html")
        # удаляем поисковый запрос из request.form
        # del request.form["search_query"]

        return render_template("search_result.html", data=users)
    else:
        return render_template("search_page.html")


@app.route("/chat/<string:user1>/<int:chat_id>")
def chat_(user1, chat_id):
    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.create_date).all()

    return render_template("chat_page.html", data=messages)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/user/<string:username>/<int:id_>")
@login_required
def user_page(username, id_):
    data = json.loads(session["user"].replace("'", '"'))
    return render_template("user_page.html", data=data)


@app.route("/<string:username>/<int:user_id>/chats")
@login_required
def chats(username, user_id):
    query = fr"""SELECT * FROM "chat" WHERE "chat".user_id = {user_id} OR "chat".user_2_id = {user_id} ORDER BY "chat".create_date ASC;"""
    chats_ = db.engine.execute(query).all()
    query_users = """SELECT "user".id_, "user".username FROM "user";"""
    users = db.engine.execute(query_users).all()
    users_dict = {}
    for user in users:
        users_dict[user[0]] = user[1]

    print(users_dict)
    print("chats", chats_)
    data = json.loads(session["user"].replace("'", '"'))
    data["chats"] = chats_
    data["user2"] = username
    data["users"] = users_dict

    return render_template("chats.html", data=data)


@app.route("/<string:username>/<int:id_>/friends")
@login_required
def friends(username, id_):
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
            username = username.lower()
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
    # elif request.form.get("search_query", None):
    #     if request.form.get("search_query", None) and session.get("user"):
    #         query_text = request.form.get("search_query", None)
    #         id_ = json.loads(session.get("user").replace("'", '"'))["id_"]
    #         sql = f"SELECT \"user\".username, \"user\".id_ FROM \"user\" WHERE (\"user\".username LIKE '%%{query_text}%%' OR \"user\".username LIKE '{query_text}%%') AND \"user\".id_ != {id_};"
    #         users = db.engine.execute(sql).all()
    #
    #         # удаляем поисковый запрос из request.form
    #         # del request.form["search_query"]
    #
    #         return render_template("search_result.html", data=users)
    #     else:
    #         flash("Чтобы искать людей, надо войти в систему")
    #
    #         next_ = request.args.get("next", "/")
    #         return redirect(next_)
    return response


if __name__ == "__main__":
    app.run(debug=True)

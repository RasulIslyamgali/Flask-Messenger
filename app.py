from flask import Flask, render_template, url_for
import os


# path = "__main__"
app = Flask(__name__)


@app.route("/")
@app.route("/home")
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


if __name__ == "__main__":
    app.run(debug=True)
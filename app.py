from flask import Flask
import os


# path = "__main__"
app = Flask(__name__)


@app.route("/")
def home():
    return "Домашняя страница"


@app.route("/about")
def about():
    return "Страница о нас"


if __name__ == "__main__":
    app.run(debug=False)
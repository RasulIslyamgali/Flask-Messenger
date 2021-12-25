from flask import Flask
import os


path = "__main__"
app = Flask(path)


@app.route("/")
def home():
    return "Домашняя страница"


@app.route("/about")
def about():
    return "Страница о нас"
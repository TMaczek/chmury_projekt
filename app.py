from DatabaseApp import *
from flask import Flask, render_template
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

app = Flask(__name__)


def get_episodes_for_tests():
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USERNAME")
    password = os.environ.get("NEO4J_PASSWORD")
    db_app = DatabaseApp(uri, user, password)
    data = db_app.find_characters_episodes("Peridot")
    db_app.close()
    return data


@app.route("/")
@app.route("/home")
def hello():
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('home.html', subpage='About Page')


@app.route("/episodes")
def episodes():
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USERNAME")
    password = os.environ.get("NEO4J_PASSWORD")
    db_app = DatabaseApp(uri, user, password)
    data = db_app.get_episodes()
    db_app.close()

    return render_template('episodes.html', episodes=data)


@app.route("/characters")
def characters():
    return render_template("home.html", subpage="Characters Page")


@app.route("/groups")
def groups():
    return render_template("home.html", subpage="Groups Page")


@app.route("/writers")
def writers():
    return render_template("home.html", subpage="Writers Page")


if __name__ == "__main__":
    app.run(debug=True)

    # Aura queries use an encrypted connection using the "neo4j+s" URI scheme
    # uri = "neo4j+s://1b0bc938.databases.neo4j.io"
    # user = "neo4j"
    # password = "cfG0JN4KRSAc1VjsB-xVyp7KO8jRsMvd7WNdGf0KMj4"
    # db_app = DatabaseApp(uri, user, password)
    #
    # #app.find_characters_episodes("Peridot")
    #
    # db_app.close()

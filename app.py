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
    print(uri)
    print("xd")
    user = os.environ.get("NEO4J_USERNAME")
    password = os.environ.get("NEO4J_PASSWORD")
    # uri = "neo4j+s://1b0bc938.databases.neo4j.io"
    # user = "neo4j"
    # password = "cfG0JN4KRSAc1VjsB-xVyp7KO8jRsMvd7WNdGf0KMj4"
    db_app = DatabaseApp(uri, user, password)

    data = db_app.find_characters_episodes("Peridot")

    db_app.close()
    return data
    #return "ohio"


@app.route("/")
@app.route("/home")
def hello():
    data = get_episodes_for_tests()
    str_print = ""
    for row in data:
        str_print += str(row["name"])
    return str_print
    #return render_template('home.html')


@app.route("/about")
def about():
    return "<h1>About page</h1>"


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

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


@app.route("/episodes/")
def episodes():
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USERNAME")
    password = os.environ.get("NEO4J_PASSWORD")
    db_app = DatabaseApp(uri, user, password)
    data = db_app.get_episodes()
    db_app.close()

    return render_template('episodes.html', episodes=data)


@app.route('/episodes/<path:text>', methods=['GET', 'POST'])
def all_episodes_routes(text):
    episode =  text.split('/', 1)[0]
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USERNAME")
    password = os.environ.get("NEO4J_PASSWORD")
    db_app = DatabaseApp(uri, user, password)
    episode, characters, writers = db_app.find_episode_data(episode)
    db_app.close()
    return render_template("episode.html", name=episode, characters=characters, episode=episode, writers=writers)


@app.route("/characters/")
def characters():
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USERNAME")
    password = os.environ.get("NEO4J_PASSWORD")
    db_app = DatabaseApp(uri, user, password)
    data = db_app.get_characters()
    db_app.close()
    return render_template("characters.html", names=data)


@app.route('/characters/<path:text>', methods=['GET', 'POST'])
def all_characters_routes(text):
    character= text.split('/', 1)[0]
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USERNAME")
    password = os.environ.get("NEO4J_PASSWORD")
    db_app = DatabaseApp(uri, user, password)
    groups, episodes = db_app.find_character_data(character)
    db_app.close()
    return render_template("character.html", name=character, groups=groups, episodes=episodes, ep_count=len(episodes))


@app.route("/groups/")
def groups():
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USERNAME")
    password = os.environ.get("NEO4J_PASSWORD")
    db_app = DatabaseApp(uri, user, password)
    groups, members = db_app.find_group_data()
    db_app.close()
    return render_template("groups.html", groups=groups, members=members)


@app.route("/writers/")
def writers():
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USERNAME")
    password = os.environ.get("NEO4J_PASSWORD")
    db_app = DatabaseApp(uri, user, password)
    data = db_app.get_writers()
    db_app.close()
    return render_template("writers.html", names=data)


@app.route('/writers/<path:text>', methods=['GET', 'POST'])
def all_writers_routes(text):
    writer= text.split('/', 1)[0]
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USERNAME")
    password = os.environ.get("NEO4J_PASSWORD")
    db_app = DatabaseApp(uri, user, password)
    episodes = db_app.find_writer_data(writer)
    db_app.close()
    return render_template("writer.html", name=writer,  episodes=episodes, ep_count = len(episodes))

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

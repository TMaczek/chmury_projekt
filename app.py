from DatabaseApp import *
from flask import Flask, render_template, url_for, flash, redirect
import os
from os.path import join, dirname
from dotenv import load_dotenv
from forms import CharacterForm, WriterForm, EpisodeForm

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/episodes/", methods=['GET', 'POST'])
def episodes():
    episode_form = EpisodeForm()
    if episode_form.name.data is not None:
        flash(f'Episode {episode_form.name.data} added.', 'success')

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


@app.route("/characters/", methods=['GET', 'POST'])
def characters():
    char_form = CharacterForm()
    if char_form.name.data is not None:
        flash(f'Character {char_form.name.data} added.', 'success')
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


@app.route("/writers/", methods=['GET', 'POST'])
def writers():
    writer_form = WriterForm()

    if writer_form.name.data is not None:
        flash(f'Writer {writer_form.name.data} added.', 'success')

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


@app.route("/fusions/")
def fusions():
    return render_template('fusions.html')


@app.route("/addnode/", methods=['GET', 'POST'])
def addnode():
    char_form = CharacterForm()
    writer_form = WriterForm()
    episode_form = EpisodeForm()
    return render_template('addnode.html', char_form=char_form, writer_form=writer_form, episode_form=episode_form)


@app.route("/addrelation/")
def addrelation():
    return render_template('addrelation.html')

if __name__ == "__main__":
    app.run(debug=True)



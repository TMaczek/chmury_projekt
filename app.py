from DatabaseApp import *
from flask import Flask, render_template, url_for, flash, redirect
import os
from os.path import join, dirname
from dotenv import load_dotenv
from forms import CharacterForm, WriterForm, EpisodeForm, CharacterToEpisode, CharacterToGroup, WriterToEpisode, CharactersToFusion

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

uri = os.environ.get("NEO4J_URI")
user = os.environ.get("NEO4J_USERNAME")
password = os.environ.get("NEO4J_PASSWORD")

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/episodes/", methods=['GET', 'POST'])
def episodes():
    episode_form = EpisodeForm()
    if episode_form.name.data is not None:
        flash(f'Episode {episode_form.name.data} added.', 'success')

    db_app = DatabaseApp(uri, user, password)

    data = db_app.get_episodes()
    db_app.close()

    return render_template('episodes.html', episodes=data)


@app.route('/episodes/<path:text>', methods=['GET', 'POST'])
def all_episodes_routes(text):
    episode =  text.split('/', 1)[0]

    db_app = DatabaseApp(uri, user, password)
    episode, characters, writers = db_app.find_episode_data(episode)
    db_app.close()
    return render_template("episode.html", name=episode, characters=characters, episode=episode, writers=writers)


@app.route("/characters/", methods=['GET', 'POST'])
def characters():
    char_form = CharacterForm()
    if char_form.name.data is not None:
        flash(f'Character {char_form.name.data} added.', 'success')

    db_app = DatabaseApp(uri, user, password)
    data = db_app.get_characters()
    db_app.close()
    return render_template("characters.html", names=data)


@app.route('/characters/<path:text>', methods=['GET', 'POST'])
def all_characters_routes(text):
    character= text.split('/', 1)[0]
    db_app = DatabaseApp(uri, user, password)
    groups, episodes = db_app.find_character_data(character)
    db_app.close()
    return render_template("character.html", name=character, groups=groups, episodes=episodes, ep_count=len(episodes))


@app.route("/groups/")
def groups():
    db_app = DatabaseApp(uri, user, password)
    groups, members = db_app.find_group_data()
    db_app.close()
    return render_template("groups.html", groups=groups, members=members)


@app.route("/writers/", methods=['GET', 'POST'])
def writers():
    writer_form = WriterForm()

    if writer_form.name.data is not None:
        flash(f'Writer {writer_form.name.data} added.', 'success')

    db_app = DatabaseApp(uri, user, password)
    data = db_app.get_writers()
    db_app.close()
    return render_template("writers.html", names=data)


@app.route('/writers/<path:text>', methods=['GET', 'POST'])
def all_writers_routes(text):
    writer= text.split('/', 1)[0]

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


@app.route("/addrelation/", methods=['GET', 'POST'])
def addrelation():
    db_app = DatabaseApp(uri, user, password)
    res = db_app.get_characters()
    char_choices = []
    for pair in res:
        char_choices.append( (pair['name'], pair['name']) )

    res = db_app.get_episodes()
    episode_choices = []
    for pair in res:
        episode_choices.append( (pair['name'], pair['name']) )

    res = db_app.get_groups()
    group_choices = []
    for pair in res:
        group_choices.append( (pair['name'], pair['name']) )

    res = db_app.get_writers()
    writer_choices = []
    for pair in res:
        writer_choices.append( (pair['name'], pair['name']) )

    db_app.close()
    cte_form = CharacterToEpisode()
    ctg_form = CharacterToGroup()
    wte_form = WriterToEpisode()
    ctf_form = CharactersToFusion()

    cte_form.character.choices = char_choices
    cte_form.episode.choices = episode_choices

    ctg_form.character.choices = char_choices
    ctg_form.group.choices = group_choices

    wte_form.writer.choices = writer_choices
    wte_form.episode.choices = episode_choices

    ctf_form.first_char.choices = char_choices
    ctf_form.second_char.choices = char_choices
    ctf_form.fusion.choices = char_choices

    return render_template('addrelation.html', cte_form=cte_form, ctg_form=ctg_form, wte_form=wte_form, ctf_form=ctf_form)

if __name__ == "__main__":
    app.run(debug=True)



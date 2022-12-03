from DatabaseApp import *
from flask import Flask, render_template, flash, request
import os
from os.path import join, dirname
from dotenv import load_dotenv
from forms import *

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
    db_app = DatabaseApp(uri, user, password)

    if request.method == 'POST':
        episode_name = request.form['name']
        season = request.form['season']
        number = request.form['season_num']
        overall = request.form['overall']
        res = db_app.check_if_exists(episode_name, 'Episode')
        episode_form = EpisodeForm()
        if episode_form.name.data is not None and res == 0:
            db_app.add_episode(episode_name, season, number, overall)
            flash(f'Episode {episode_form.name.data} added.', 'success')
        elif res != 0:
            flash(f'Episode {episode_form.name.data} exists already.', 'danger')

    data = db_app.get_episodes()
    db_app.close()
    return render_template('episodes.html', episodes=data)


@app.route('/episodes/<path:text>', methods=['GET', 'POST'])
def all_episodes_routes(text):
    episode = text.split('/', 1)[0]
    db_app = DatabaseApp(uri, user, password)
    episode_data, characters_data, writers_data = db_app.find_episode_data(episode)
    db_app.close()
    return render_template("episode.html", name=episode, characters=characters_data, episode=episode_data,
                           writers=writers_data)


@app.route("/characters/", methods=['GET', 'POST'])
def characters():
    db_app = DatabaseApp(uri, user, password)

    if request.method == 'POST':
        char_name = request.form['name']
        res = db_app.check_if_exists(char_name, 'Character')
        char_form = CharacterForm()
        if char_form.name.data is not None and res == 0:
            db_app.add_characters(char_name)
            flash(f'Character {char_form.name.data} added.', 'success')
        elif res != 0:
            flash(f'Character {char_form.name.data} exists already.', 'danger')

    data = db_app.get_characters()
    db_app.close()
    return render_template("characters.html", names=data)


@app.route('/characters/<path:text>', methods=['GET', 'POST'])
def all_characters_routes(text):
    character = text.split('/', 1)[0]
    db_app = DatabaseApp(uri, user, password)
    groups_data, episodes_data = db_app.find_character_data(character)
    db_app.close()
    return render_template("character.html", name=character, groups=groups_data, episodes=episodes_data,
                           ep_count=len(episodes_data))


@app.route("/groups/")
def groups():
    db_app = DatabaseApp(uri, user, password)
    groups_data, members_data = db_app.find_group_data()
    db_app.close()
    return render_template("groups.html", groups=groups_data, members=members_data)


@app.route("/writers/", methods=['GET', 'POST'])
def writers():
    db_app = DatabaseApp(uri, user, password)

    if request.method == 'POST':
        writer_name = request.form['name']
        print(writer_name)
        res = db_app.check_if_exists(writer_name, 'Writer')
        print(res)
        writer_form = WriterForm()
        if writer_form.name.data is not None and res == 0:
            db_app.add_writers(writer_name)
            flash(f'Writer {writer_form.name.data} added.', 'success')
        elif res != 0:
            flash(f'Writer {writer_form.name.data} exists already.', 'danger')

    data = db_app.get_writers()
    db_app.close()
    return render_template("writers.html", names=data)


@app.route('/writers/<path:text>', methods=['GET', 'POST'])
def all_writers_routes(text):
    writer = text.split('/', 1)[0]
    db_app = DatabaseApp(uri, user, password)
    episodes_data = db_app.find_writer_data(writer)
    db_app.close()
    return render_template("writer.html", name=writer,  episodes=episodes_data, ep_count=len(episodes_data))


@app.route("/fusions/")
def fusions():
    db_app = DatabaseApp(uri, user, password)
    fusion_names = db_app.get_fusions()
    fusions_array = []
    for pair in fusion_names:
        name = pair['name']
        parts = db_app.find_fusion_parts(name)
        fusions_array.append({'name': name, 'parts': parts})
    db_app.close()
    return render_template('fusions.html', data=fusions_array)


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
        char_choices.append((pair['name'], pair['name']))

    res = db_app.get_episodes()
    episode_choices = []
    for pair in res:
        episode_choices.append((pair['name'], pair['name']))

    res = db_app.get_groups()
    group_choices = []
    for pair in res:
        group_choices.append((pair['name'], pair['name']))

    res = db_app.get_writers()
    writer_choices = []
    for pair in res:
        writer_choices.append((pair['name'], pair['name']))

    cte_form = CharacterToEpisode()
    ctg_form = CharacterToGroup()
    wte_form = WriterToEpisode()
    ctf_form = CharactersToFusion()
    if request.method == 'POST':
        button = request.form['submit']
        if button == 'Add to episode':
            character = request.form['character']
            episode = request.form['episode']
            res = db_app.check_if_exists_relation(character, episode, "Character", "Episode", 'APPEARED_IN')
            if cte_form.validate_on_submit() and res == 0:
                db_app.add_appeared(episode, character)
                flash(f'Character added to episode.', 'success')
            elif res != 0:
                flash(f'This relation exists already', 'danger')
        elif button == 'Add to group':
            character = request.form['character']
            group = request.form['group']
            res = db_app.check_if_exists_relation(character, group, "Character", "Group", 'BELONGS_TO')
            if ctg_form.validate_on_submit() and res == 0:
                db_app.add_belongs_to(group, character)
                flash(f'Character added to group.', 'success')
            elif res != 0:
                flash(f'This relation exists already', 'danger')
        elif button == 'Add writer':
            writer = request.form['writer']
            episode = request.form['episode']
            res = db_app.check_if_exists_relation(writer, episode, "Writer", "Episode", 'WROTE')
            if wte_form.validate_on_submit() and res == 0:
                db_app.add_wrote(episode, writer)
                flash(f'Writer assigned to episode.', 'success')
            elif res != 0:
                flash(f'This relation exists already', 'danger')
        elif button == 'Add to fusion':
            first = request.form['first_char']
            second = request.form['second_char']
            fusion = request.form['fusion']
            check_fusion = db_app.check_if_fusion(fusion)
            if check_fusion != 0:
                flash(f'This character is already a fusion.', 'danger')
            elif first != second and first != fusion and fusion != second:
                res = db_app.check_if_exists_relation(fusion, first, "Character", "Character", 'FUSION_OF')
                res += db_app.check_if_exists_relation(fusion, second, "Character", "Character", 'FUSION_OF')
                if ctf_form.validate_on_submit() and res == 0:
                    db_app.add_fusion_of(fusion, first, second)
                    flash(f'Characters added to fusion.', 'success')
                elif res != 0:
                    flash(f'This relation (or part of it) exists already', 'danger')
            else:
                flash(f'Duplicate character choices.', 'danger')

    cte_form.character.choices = char_choices
    cte_form.episode.choices = episode_choices

    ctg_form.character.choices = char_choices
    ctg_form.group.choices = group_choices

    wte_form.writer.choices = writer_choices
    wte_form.episode.choices = episode_choices

    ctf_form.first_char.choices = char_choices
    ctf_form.second_char.choices = char_choices
    ctf_form.fusion.choices = char_choices
    db_app.close()

    return render_template('addrelation.html',
                           cte_form=cte_form,
                           ctg_form=ctg_form,
                           wte_form=wte_form,
                           ctf_form=ctf_form)


@app.route("/deletenode/", methods=['GET', 'POST'])
def deletenode():
    db_app = DatabaseApp(uri, user, password)
    delete_character = DeleteCharacter()
    delete_episode = DeleteEpisode()
    delete_writer = DeleteWriter()

    if request.method == 'POST':
        button = request.form['submit']
        print(button)
        if button == 'Delete Character':
            character = request.form['character']
            if delete_character.validate_on_submit():
                db_app.delete_by_name(character)
                flash(f'Character {delete_character.character.data} removed.', 'info')
        elif button == 'Delete Episode':
            episode = request.form['episode']
            if delete_episode.validate_on_submit():
                db_app.delete_by_name(episode)
                flash(f'Episode {delete_episode.episode.data}  removed', 'info')
        elif button == 'Delete Writer':
            writer = request.form['writer']
            if delete_writer.validate_on_submit():
                db_app.delete_by_name(writer)
                flash(f'Writer {delete_writer.writer.data}  removed', 'info')

    res = db_app.get_characters()
    char_choices = []
    for pair in res:
        char_choices.append((pair['name'], pair['name']))

    res = db_app.get_episodes()
    episode_choices = []
    for pair in res:
        episode_choices.append((pair['name'], pair['name']))

    res = db_app.get_writers()
    writer_choices = []
    for pair in res:
        writer_choices.append((pair['name'], pair['name']))

    delete_character.character.choices = char_choices
    delete_episode.episode.choices = episode_choices
    delete_writer.writer.choices = writer_choices
    db_app.close()
    return render_template('deletenode.html', delete_character=delete_character, delete_episode=delete_episode,
                           delete_writer=delete_writer)


@app.route("/deleterelation/", methods=['GET', 'POST'])
def deleterelation():
    db_app = DatabaseApp(uri, user, password)
    delete_character_episode = DeleteCharacterFromEpisode()
    delete_character_group = DeleteCharacterFromGroup()
    delete_writer_episode = DeleteWriterFromEpisode()
    delete_fusion = DeleteFusion()

    if request.method == 'POST':
        button = request.form['submit']
        if button == 'Delete from episode':
            character = request.form['character']
            episode = request.form['episode']
            if delete_character_episode.validate_on_submit():
                db_app.delete_relation_between(character, episode)
                flash(f'Character {delete_character_episode.character.data} removed from episode '
                      f'{delete_character_episode.episode.data}.', 'info')
        elif button == 'Delete from group':
            character = request.form['character']
            group = request.form['group']
            if delete_character_group.validate_on_submit():
                db_app.delete_relation_between(character, group)
                flash(f'Character {delete_character_group.character.data}  removed from group '
                      f'{delete_character_group.group.data}', 'info')
        elif button == 'Delete writing credits':
            writer = request.form['writer']
            episode = request.form['episode']
            if delete_writer_episode.validate_on_submit():
                db_app.delete_relation_between(writer, episode)
                flash(f'Writer {delete_writer_episode.writer.data}  removed from episode '
                      f'{delete_writer_episode.episode.data}', 'info')
        elif button == 'Delete fusion':
            fusion = request.form['fusion']
            if delete_fusion.validate_on_submit():
                parts = db_app.find_fusion_parts(fusion)
                db_app.delete_relation_between(fusion, parts[0])
                db_app.delete_relation_between(fusion, parts[1])
                flash(f'Fusion {delete_fusion.fusion.data}  removed', 'info')

    res = db_app.get_characters()
    char_choices = []
    for pair in res:
        char_choices.append((pair['name'], pair['name']))

    res = db_app.get_episodes()
    episode_choices = []
    for pair in res:
        episode_choices.append((pair['name'], pair['name']))

    res = db_app.get_fusions()
    fusion_choices = []
    for pair in res:
        fusion_choices.append((pair['name'], pair['name']))

    res = db_app.get_writers()
    writer_choices = []
    for pair in res:
        writer_choices.append((pair['name'], pair['name']))

    res = db_app.get_groups()
    group_choices = []
    for pair in res:
        group_choices.append((pair['name'], pair['name']))

    delete_character_episode.character.choices = char_choices
    delete_character_episode.episode.choices = episode_choices

    delete_character_group.character.choices = char_choices
    delete_character_group.group.choices = group_choices

    delete_writer_episode.writer.choices = writer_choices
    delete_writer_episode.episode.choices = episode_choices

    delete_fusion.fusion.choices = fusion_choices

    db_app.close()

    return render_template('deleterelation.html', delete_character_episode=delete_character_episode,
                           delete_character_group=delete_character_group,
                           delete_writer_episode=delete_writer_episode,
                           delete_fusion=delete_fusion)


if __name__ == "__main__":
    app.run(debug=True)

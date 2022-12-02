from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms.widgets.html5 import NumberInput
from DatabaseApp import *


class CharacterForm(FlaskForm):
    name = StringField('Character Name',
                       validators=[DataRequired(), Length(min=1)])
    char_submit = SubmitField('Add')


class WriterForm(FlaskForm):
    name = StringField('Writer Name',
                       validators=[DataRequired(), Length(min=5)])
    writer_submit = SubmitField('Add')


class EpisodeForm(FlaskForm):
        name = StringField('Episode Name',
                           validators=[DataRequired(), Length(min=5)])
        overall = IntegerField('Overall Number', validators=[DataRequired()], widget=NumberInput(min=1, max=160))
        season = IntegerField('Season', validators=[DataRequired()], widget=NumberInput(min=1, max=6))
        season_num = IntegerField("Season Number", validators=[DataRequired()], widget=NumberInput(min=1, max=52))
        episode_submit = SubmitField('Add')


class CharacterToEpisode(FlaskForm):

    character = SelectField('Character', validate_choice=False)
    episode = SelectField('Episode', validate_choice=False)

    submit = SubmitField('Add to episode')


class CharacterToGroup(FlaskForm):
    character = SelectField('Character', validate_choice=False)
    group = SelectField('Group', validate_choice=False)

    submit = SubmitField('Add to group')


class WriterToEpisode(FlaskForm):

    writer = SelectField('Writer', validate_choice=False)
    episode = SelectField('Episode', validate_choice=False)
    submit = SubmitField('Add writer')


class CharactersToFusion(FlaskForm):
    first_char = SelectField('First Character', validate_choice=False)
    second_char = SelectField('Second Character', validate_choice=False)
    fusion = SelectField('Fusion', validate_choice=False)
    submit = SubmitField('Add to fusion')
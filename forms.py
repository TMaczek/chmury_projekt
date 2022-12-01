from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms.widgets.html5 import NumberInput


class CharacterForm(FlaskForm):
    name = StringField('Character Name',
                       validators=[DataRequired(), Length(min=1)])
    char_submit = SubmitField('Add')


class WriterForm(FlaskForm):
    name = StringField('Writer Name',
                       validators=[DataRequired(), Length(min=10)])
    writer_submit = SubmitField('Add')


class EpisodeForm(FlaskForm):
        name = StringField('Episode Name',
                           validators=[DataRequired(), Length(min=10)])
        overall = IntegerField('Overall Number', validators=[DataRequired()], widget=NumberInput(min=1, max=160))
        season = IntegerField('Season', validators=[DataRequired()], widget=NumberInput(min=1, max=6))
        season_num = IntegerField("Season Number", validators=[DataRequired()], widget=NumberInput(min=1, max=26))
        episode_submit = SubmitField('Add')
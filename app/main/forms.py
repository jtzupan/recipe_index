from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, widgets, SelectMultipleField, SubmitField, FileField
from wtforms.validators import DataRequired


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class RecipeForm(FlaskForm):
    recipe_name = StringField('Recipe Name', validators=[DataRequired()])
    choices = ['Mexican', 'Thai']
    form_choices = [(x, x) for x in choices]
    cuisine_type = MultiCheckboxField('Cuisine Type', choices=form_choices)
    optional_description = StringField('Optional Descriptors')
    file = FileField()
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
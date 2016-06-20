from flask_wtf import Form
from wtforms.validators import Required
from wtforms import SubmitField

from ..question.forms import TagListField

class UserTagsForm(Form):
	tags = TagListField('Tags', validators=[Required()])
	submit = SubmitField('Add')
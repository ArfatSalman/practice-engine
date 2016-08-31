from flask_wtf import Form
from wtforms.validators import Required
from wtforms import SubmitField, TextAreaField

from ..question.forms import TagListField

class UserTagsForm(Form):
	tags = TagListField('Topic(s)', validators=[Required()])
	submit = SubmitField('Add')


class ContactUsForm(Form):
	message = TextAreaField('Message', validators=[Required()])
	submit = SubmitField('Send')
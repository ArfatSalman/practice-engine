from flask_wtf import Form
from wtforms.fields import Field
from wtforms import (SubmitField,
                     SelectField,
                     TextAreaField,
                     BooleanField,
                     FieldList, 
                     FormField,
                     HiddenField)
from wtforms.validators import Required, DataRequired, InputRequired
from wtforms.widgets import TextInput, ListWidget

class TagListField(Field):
    '''
    _value() is called by the TextInputWidget to provide the 
    value that is displayed in the form.
     
     process_formdata() processes incoming formdata back into a list of tags.
     '''
    
    widget = TextInput()

    def _value(self):
        if self.data:
            return ', '.join(self.data)
        else:
            return ''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [x.strip() for x in valuelist[0].split(',')]
        else:
            self.data = []


class OptionForm(Form):
    option = TextAreaField('option')
    check_option = BooleanField()


class UserTagsForm(Form):
    tags = TagListField('Tags', validators=[Required()])
    submit = SubmitField('Add')


class PostQuestionForm(Form):
    body = TextAreaField('Question?', validators=[Required()])
    description = TextAreaField('Description')

    tags = TagListField('Tags', validators=[InputRequired()])

    option1 = TextAreaField('option1', validators=[Required()])
    check_option1 = BooleanField()
    
    option2 = TextAreaField('option2', validators=[Required()])
    check_option2 = BooleanField('check2')
    
    option3 = TextAreaField('option3')
    check_option3 = BooleanField('check3')
    
    option4 = TextAreaField('option4')
    check_option4 = BooleanField('check4')
    
    submit = SubmitField('Submit')


class EditQuestionForm(PostQuestionForm):
    option1_id = HiddenField('option1_id')
    option2_id = HiddenField('option2_id')
    option3_id = HiddenField('option3_id')
    option4_id = HiddenField('option4_id')


class SolutionForm(Form):
    body = TextAreaField('Solution', validators=[Required()])
    submit = SubmitField('Post')

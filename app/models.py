from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager
from datetime import datetime
from .utilities import print_debug

tags_assoc = db.Table('tags_assoc',
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('questions.id'), primary_key=True)
)

user_tags_assoc = db.Table('user_tags_assoc',
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

solved_questions_assoc = db.Table('solved_questions_assoc',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('questions.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(128))
    username = db.Column(db.String(128), unique=True, index=True)
    #email = db.Column(db.String(128), unique=True, index=True)
    questions = db.relationship("Question", 
                    backref=db.backref('user', lazy='joined'),
                    lazy='dynamic')

    questions_solved = db.relationship("Question",
                                        secondary=solved_questions_assoc,
                                        backref=db.backref('solved_by', 
                                            lazy='dynamic'),
                                        lazy='dynamic')

    associated_tags = db.relationship("Tag",
                                      secondary=user_tags_assoc,
                                      backref=db.backref('assoc_users', 
                                                    lazy='dynamic'),
                                      lazy='dynamic')

    def __init__(self, username, password=''):
    	self.username = username
    	self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        print_debug('check password called')
    	return check_password_hash(self.password_hash, password)

    def get_relevant_question(self):

        # get the questions
        ques = Question.query

        '''Remove the questions which are already solved by the user'''
        ques = ques.join(solved_questions_assoc, solved_questions_assoc.c.question_id != Question.id)
        
        '''
        Get the questions where tags are filled.
        It is required because the next joins filters by tags
        '''
        ques = ques.join(tags_assoc, tags_assoc.c.question_id == Question.id)

        '''Get the questions where the tags matches the tags of user'''
        ques = ques.join(user_tags_assoc, user_tags_assoc.c.tag_id == tags_assoc.c.tag_id)

        '''Filter the question by individual user'''
        ques = ques.filter_by(user_id=self.id)

        return ques.first()

@login_manager.user_loader
def load_user(user_id):
    print_debug("User loader called with id %s" % user_id)
    return User.query.get(int(user_id))


class Question(db.Model):
    '''
    One Question has many options. Therefore, One to many relationship.
    One question has only one author. Hence, one to many.
    One question has many tags.
    '''
    __tablename__='questions'
    
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    
    body_html = db.Column(db.Text)
    
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    author_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)

    options = db.relationship("Option",
                            cascade="all, delete-orphan")

    tags = db.relationship("Tag", 
                            secondary=tags_assoc,
                            backref=db.backref('questions', 
                                                lazy='dynamic'),
                            lazy='dynamic')


class Option(db.Model):
    __tablename__='options'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    is_right = db.Column(db.Boolean, default=False)

    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'),
        nullable=False)



class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    tagname = db.Column(db.String(64), unique=True, nullable=False)
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func, event, desc
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.exc import NoResultFound
from flask_login import UserMixin, current_user
from . import db, login_manager
from .utilities import print_debug
from markdown import markdown
import bleach

tags_assoc = db.Table('tags_assoc',
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('questions.id'), primary_key=True)
)

user_tags_assoc = db.Table('user_tags_assoc',
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class ReportQuestionAssoc(db.Model):
    __tablename__ = 'report_questions_assoc'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    message = db.Column(db.Text)

    question = db.relationship('Question', 
                                backref=db.backref('reported_by', 
                                                    lazy='dynamic'))
    def __init__(self, question):
        self.question = question


class UpvoteDownvoteSolutionAssoc(db.Model):
    __tablename__ = 'upvote_downvote_solutions_assoc'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    solution_id = db.Column(db.Integer, db.ForeignKey('solutions.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_upvote = db.Column(db.Boolean, default=True)

    solution = db.relationship('Solution',
                                backref=db.backref('voted_by',
                                                    lazy='dynamic'))
    
    def __init__(self, solution):
        self.solution = solution


class DownvoteQuestionAssoc(db.Model):
    __tablename__ = 'downvote_questions_assoc'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    question = db.relationship('Question', 
                                backref=db.backref('downvoted_by', 
                                                    lazy='dynamic'))

    def __init__(self, question):
        self.question = question


class UpvoteQuestionAssoc(db.Model):
    __tablename__ = 'upvote_questions_assoc'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    question = db.relationship('Question', 
                                backref=db.backref('upvoted_by', 
                                                    lazy='dynamic'))

    def __init__(self, question):
        self.question = question


class FavouriteQuestionAssoc(db.Model):
    __tablename__ = 'favourite_questions_assoc'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    question = db.relationship('Question', 
                                backref=db.backref('fav_by', 
                                                    lazy='dynamic'))

    def __init__(self, question):
        self.question = question


class SolvedQuestionsAssoc(db.Model):
    '''
    Parent(left-table): User. It references One->Many
    Child(right-table): Question. It references Many->One
    '''
    __tablename__ = 'solved_questions_assoc'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    attempted = db.Column(db.Integer, default=0)
    solved = db.Column(db.Integer, default=False)

    # For when the user wants to unsolve just a prticualr question.
    # The solved will be changed to Flase, and is_set_unsolved
    # will be changed to True. In Score calculation, if a 
    # question is_set_unsolved, score = 0
    is_set_unsolved = db.Column(db.Boolean, default=False)

    question = db.relationship('Question', backref=db.backref('solved_by', lazy='dynamic'))

    def __init__(self, question):
        self.question = question
        self.attempted = 0


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(128))
    description = db.Column(db.Text())
    username = db.Column(db.String(128), index=True, default='User')
    email = db.Column(db.String(128), unique=True, index=True, nullable=False)
    picture = db.Column(db.String(128))
    score = db.Column(db.Integer, default=0) # Only from correct solution
    streak = db.Column(db.Integer, default=1)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    questions = db.relationship("Question", 
                    backref=db.backref('user'),
                    order_by='desc(Question.timestamp)',
                    lazy='dynamic')

    solutions = db.relationship('Solution',
                                backref='user',
                                order_by='desc(Solution.timestamp)',
                                lazy='dynamic')

    solutions_voted = db.relationship('UpvoteDownvoteSolutionAssoc',
                                      backref='user',
                                      order_by='desc(UpvoteDownvoteSolutionAssoc.timestamp)',
                                      lazy='dynamic',
                                      cascade='all, delete-orphan')
    sols_voted = association_proxy('solutions_voted', 'solution')

    setting = db.relationship('UserSetting',
                               backref='user',
                               uselist=False,
                               lazy='joined',
                               cascade='all, delete-orphan')

    questions_activity = db.relationship('SolvedQuestionsAssoc',
                                    backref='user',
                                    order_by='desc(SolvedQuestionsAssoc.timestamp)',
                                    cascade='all, delete, delete-orphan',
                                    lazy='dynamic')
    ques_solved = association_proxy('questions_activity', 'question')

    questions_upvoted = db.relationship('UpvoteQuestionAssoc',
                                             backref='user',
                                             order_by='desc(UpvoteQuestionAssoc.timestamp)',
                                             cascade='all, delete-orphan',
                                             lazy='dynamic')
    ques_upvoted = association_proxy('questions_upvoted', 'question')

    questions_downvoted = db.relationship('DownvoteQuestionAssoc',
                                               backref='user',
                                               order_by='desc(DownvoteQuestionAssoc.timestamp)',
                                               cascade='all, delete, delete-orphan',
                                               lazy='dynamic')
    ques_downvoted = association_proxy('questions_downvoted', 'question')


    questions_fav = db.relationship('FavouriteQuestionAssoc',
                                     backref='user',
                                     order_by='desc(FavouriteQuestionAssoc.timestamp)',
                                     cascade='all, delete-orphan',
                                     lazy='dynamic')
    ques_fav = association_proxy('questions_fav', 'question')

    questions_reported = db.relationship('ReportQuestionAssoc', 
                                         backref='user',
                                         order_by='desc(ReportQuestionAssoc.timestamp)',
                                         cascade= 'all, delete, delete-orphan',
                                         lazy='dynamic')


    associated_tags = db.relationship("Tag",
                                      secondary=user_tags_assoc,
                                      backref=db.backref('assoc_users', 
                                                    lazy='dynamic'),
                                      lazy='dynamic')

    def __init__(self, email):
        self.email = email

    @property
    def questions_solved(self):
        return self.questions_activity\
                   .filter(SolvedQuestionsAssoc.solved == True)

    @property
    def questions_attempted(self):
        return self.questions_activity\
                   .filter(SolvedQuestionsAssoc.solved==False)

    def total_solved_in_tag(self, tag):
        # Those questions which are solved by a particular user in 
        # a specific tag.
        return self.questions_solved.join(Question)\
                                 .join(tags_assoc)\
                                 .filter(tags_assoc.c.tag_id==tag.id)

    def check_password(self, password):
        print_debug('check password called')
        return check_password_hash(self.password_hash, password)

    def has_upvoted(self, obj):
        UDS = UpvoteDownvoteSolutionAssoc

        try:
            if isinstance(obj, Question):
                u = self.questions_upvoted\
                        .filter(UpvoteQuestionAssoc.question == obj)\
                        .one()
            else:
                u = self.solutions_voted\
                        .filter(UDS.is_upvote == True)\
                        .filter(UDS.solution == obj)\
                        .one()
        except NoResultFound:
            return False
        return u

    def has_authoured(self, obj):
        try:
            if isinstance(obj, Question):
                u = self.questions.filter(Question.id == obj.id)\
                                  .one()
            else:
                pass
        except NoResultFound:
            return False 
        return u

    def has_downvoted(self, obj):
        UDS = UpvoteDownvoteSolutionAssoc

        try:
            if isinstance(obj, Question):
                u = self.questions_downvoted\
                        .filter(DownvoteQuestionAssoc.question == obj)\
                        .one()
            else:
                u = self.solutions_voted\
                        .filter(UDS.is_upvote == False)\
                        .filter(UDS.solution == obj)\
                        .one()
        except NoResultFound:
            return False
        return u

    def has_favourited(self, ques):
        FQ = FavouriteQuestionAssoc

        try:
            u = self.questions_fav.filter(FQ.question == ques).one()
        except NoResultFound:
            return False
        return True

    def has_solved(self, ques):
        SQ = SolvedQuestionsAssoc

        try:
            u = self.questions_activity.filter(SQ.question == ques)\
                                     .filter(SQ.solved == True).one()
        except NoResultFound:
            return False
        return True

    def update_streak(self):
        one_day = timedelta(days=1)
        two_days = timedelta(days=2)
        
        time_difference = datetime.utcnow() - current_user.last_seen

        if time_difference >= one_day and time_difference <= two_days:
            current_user.streak = current_user.streak + 1
        elif time_difference > two_days:
            current_user.streak = 1
        else:
            return

        db.session.add(self)
        db.session.commit()
    
    def total_score(self):
        pass


    def get_relevant_question(self):

        SQA = SolvedQuestionsAssoc
        ques = Question.query

        '''Subquery to determine the question which are
            solved by a particualar user.
        '''
        subquery = db.session.query(SQA.question_id)\
                             .filter_by(user_id=self.id)\
                             .filter_by(solved=True)
        #subquery =  db.session.query(sq.c.question_id).filter(sq.c.user_id == self.id)        

        '''Remove the questions which are already solved by the user
            by using NOT IN subquery synatx.
        '''
        if not self.setting.repeat_solved_questions:
            print_debug('removing solved questions')
            ques = ques.filter(~Question.id.in_(subquery))
        
        '''
        Get the questions where tags are filled.
        It is required because the next joins filters by tags
        '''
        ques = ques.join(tags_assoc, tags_assoc.c.question_id == Question.id)

        '''Get the questions where the tags matches the tags of user'''
        ques = ques.join(user_tags_assoc, user_tags_assoc.c.tag_id == tags_assoc.c.tag_id)

        '''Filter the question by individual user'''
        ques = ques.filter_by(user_id=self.id)

        return ques.limit(10).all()

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
    
    disabled = db.Column(db.Boolean, default=False)
    
    body_html = db.Column(db.Text)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    author_id = db.Column(
        db.Integer, db.ForeignKey('users.id'))

    solutions = db.relationship('Solution',
                                backref='question',
                                lazy='dynamic',
                                cascade="all, delete-orphan")

    options = db.relationship("Option",
                               order_by='Option.id',
                               lazy='joined',
                               cascade="all, delete, delete-orphan")

    tags = db.relationship("Tag", 
                            secondary=tags_assoc,
                            backref=db.backref('questions', 
                                                lazy='dynamic'),
                            lazy='dynamic')

    '''
    BACKREFS:
    user -> the user object who has posted this question
    upvoted_by -> is a collection of Users who've upvoted this question
    downvoted_by -> same as upvoted by
    fav_by -> collection of Users who've favourited this question
    solved_by -> collection of Users who've solved this question

    '''

    def recently_solved_by(self):
        return self.solved_by\
                   .order_by(desc(SolvedQuestionsAssoc.timestamp))\
                   .limit(5).all()
    @property
    def solution_by_upvotes(self):
        return self.solutions.order_by(desc(Solution.upvotes))

    @property
    def votes(self):
        upvotes = self.upvoted_by.count()
        downvotes = self.downvoted_by.count()
        return upvotes - downvotes

    @property
    def difficulty(self):
        times_solved = db.session\
                         .query(func.sum(SolvedQuestionsAssoc.solved))\
                         .filter(SolvedQuestionsAssoc.question == self)\
                         .scalar()
        times_attempted = db.session\
                            .query(func.sum(SolvedQuestionsAssoc.attempted))\
                            .filter(SolvedQuestionsAssoc.question == self)\
                            .scalar()
        if times_solved is None:
            return 0, 0

        return int(times_attempted), int(times_solved)

    def solution_by_user(self, user):
        try:
            sol = Solution.query.filter_by(user=user, question=self).one()
        except NoResultFound:
            return False
        return sol

    def __repr__(self):
        return 'Question(body="%s", author_id=%d)' % (self.body, self.author_id)

# @event.listens_for(User.questions_upvoted, 'append')
# def upvote_append(target, value, initiator):
#     # target is the User instance (i.e who upvotes the question)
#     # value is the UpvoteQuestionAssoc event (i.e which question is upvoted)

#     if not target.has_authoured(value.question):
#         target.points.by_upvote += 1

# @event.listens_for(User.questions_upvoted, 'remove')
# def upvote_remove(target, value, initiator):
#     if not target.has_authoured(value.question):
#         target.points.by_upvote -= 1 

# @event.listens_for(User.questions_downvoted, 'append')
# def downvote_append(target, value, initiator):
#     if not target.has_authoured(value.question):
#         target.points.by_downvote += 1

# @event.listens_for(User.questions_downvoted, 'remove')
# def downvote_remove(target, value, initiator):
#     if not target.has_authoured(value.question):
#         target.points.by_downvote -= 1

def calculate_score(ques, sq):
    print_debug("CALC SCORE called")
    print_debug("SQ attempted", sq.attempted)

    num_opts = len(ques.options)
    trials = num_opts - 1
    points = range(1, num_opts+1)

    score = 0

    # if the questions is posted by the user
    # then no points in solving 
    if ques.user == current_user:
        return score
    # when the user has solved-> and then unsolved
    # is_set_unsolved will become True. Score will be 0
    # in that case.
    elif sq.is_set_unsolved:
        return score
    # If the user has previously been solved the 
    # quention, then no points.
    elif sq.solved:
        return score
    # if attempted more than trials allowed 
    elif sq.attempted > trials:
        return score
    else:
        for x in points:
            if sq.attempted == x:
                score = points[-x]
    print_debug("SCORE Calculated is : ", score)
    return score    

# This event is used for Markdown to HTML conversion.
# @event.listens_for(Question.body, 'set')
# def markdown_to_html(target, value, oldvalue, initiator):
#     allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
#                     'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 
#                     'h1', 'h2', 'h3', 'p']
#     target.body_html = bleach.linkify(bleach.clean(markdown(value,
#                                                     output_format='html'),
#                                             tags=allowed_tags, strip=True))

@event.listens_for(SolvedQuestionsAssoc.solved, 'set')
def set_event(target, value, oldvalue, initiator):
    # target is an instance of SolvedQuestionAssoc
    print_debug("ATTEMPTED: ", target.attempted)
    print_debug("IS SOLVED", target.solved)
    print_debug('set called on update called')

    ques = target.question
    if value:
        current_user.score += calculate_score(ques, target)
    

@event.listens_for(User, 'init')
def load_user_init(target, args, kwargs):
    # target is the instance that is created and attached to the User.
    # Receive an instance when its constructor is called.
    # Auto initialises the Point and Setting for every user.
    target.setting = UserSetting()
    

class Solution(db.Model):
    __tablename__ = 'solutions'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'),
                            nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @property
    def upvoted_by(self):
        UDS = UpvoteDownvoteSolutionAssoc
        return self.voted_by.filter(UDS.is_upvote == True)

    @property
    def downvoted_by(self):
        UDS = UpvoteDownvoteSolutionAssoc
        return self.voted_by.filter(UDS.is_upvote == False)
    
    @hybrid_property
    def upvotes(self):
        UDS = UpvoteDownvoteSolutionAssoc
        return self.voted_by.filter(UDS.is_upvote == True).count()

    @upvotes.expression
    def upvotes(cls):
        UDS = UpvoteDownvoteSolutionAssoc
        a = db.session.query(func.sum(UDS.is_upvote))\
                         .filter(UDS.is_upvote == True)\
                         .filter(cls.id == UDS.solution_id)
        return a

    @property
    def downvotes(self):
        UDS = UpvoteDownvoteSolutionAssoc
        return self.voted_by.filter(UDS.is_upvote == False).count()

    '''
    BACKREFS:
    voted_by -> collection of all the users who have upvoted or downvoted
    question-> The question to which this solution belongs
    user -> user who has written this question
    '''


class Option(db.Model):
    __tablename__='options'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    is_right = db.Column(db.Boolean, default=False)

    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'),
        nullable=False)



class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text()) 
    tagname = db.Column(db.String(64), unique=True, nullable=False)

    def has_user(self, user):
        try:
            u = self.assoc_users.filter(User.id == user.id).one()
        except NoResultFound:
            return False
        return u

    def top_users(self, limit=5):
        SA = SolvedQuestionsAssoc
        return db.session.query(User)\
                 .filter(user_tags_assoc.c.tag_id==self.id)\
                 .filter(User.id == user_tags_assoc.c.user_id)\
                 .order_by(
                    desc(
                        db.session.query(func.count(SA.question_id))\
                          .join(Question)\
                          .join(tags_assoc)\
                          .filter(User.id == SA.user_id)\
                          .filter(SA.solved == True)\
                          .filter(tags_assoc.c.tag_id == user_tags_assoc.c.tag_id)))\
                 .limit(limit).all()

    @property
    def solved_questions(self):
        return self.questions\
                   .join(SA)\
                   .filter(SA.solved==True)


    '''
    BACKREFS: 
    assoc_users-> Users associated with this tag
    questions -> Collection of Questions with this Tag
    '''


class UserSetting(db.Model):
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    hide_difficulty = db.Column(db.Boolean, default=False)
    repeat_solved_questions = db.Column(db.Boolean, default=False)
    auto_load_questions = db.Column(db.Boolean, default=False)
    hide_options = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # nullable = false

    '''
    BACKREFS:
    user -> User associated with this setting. Only one user can exist.
    '''
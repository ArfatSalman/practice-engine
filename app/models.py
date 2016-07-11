from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.exc import NoResultFound
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

	question = db.relationship('Question', backref=db.backref('solved_by', lazy='dynamic'))

	def __init__(self, question):
		self.question = question


class User(UserMixin, db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	password_hash = db.Column(db.String(128))
	username = db.Column(db.String(128), unique=True, index=True)
	email = db.Column(db.String(128), unique=True, index=True)
	score = db.Column(db.Integer, default=0)
	
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
									  order_by='desc(Solution.timestamp)',
									  lazy='dynamic')
	sols_voted = association_proxy('solutions_voted', 'solution')

	setting = db.relationship('UserSetting',
							   backref='user',
							   uselist=False,
							   lazy='joined',
							   cascade='all, delete-orphan')

	questions_solved = db.relationship('SolvedQuestionsAssoc',
									backref='user',
									order_by='desc(SolvedQuestionsAssoc.timestamp)',
									cascade='all, delete, delete-orphan',
									lazy='dynamic')
	ques_solved = association_proxy('questions_solved', 'question')

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

	def has_upvoted(self, ques):
		try:
			u = self.questions_upvoted\
					.filter(UpvoteQuestionAssoc.question == ques)\
					.one()
		except NoResultFound:
			return False
		return True

	def has_downvoted(self, ques):
		try:
			u = self.questions_downvoted\
					.filter(DownvoteQuestionAssoc == ques)\
					.one()
		except NoResultFound:
			return False
		return True

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
			u = self.questions_solved.filter(SQ.question == ques)\
									 .filter(SQ.solved == True).one()
		except NoResultFound:
			return False
		return True

	def get_relevant_question(self, remove_solved=1):

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
		if remove_solved:
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

	reported_wrong_ques = db.Column(db.Integer, default=0)
	
	body_html = db.Column(db.Text)
	
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)

	author_id = db.Column(
		db.Integer, db.ForeignKey('users.id'))

	solutions = db.relationship('Solution',
								order_by='desc(Solution.timestamp)',
								backref='question',
								lazy='joined',
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

		try:
			di = times_solved/times_attempted
		except ZeroDivisionError:
			return 0
		except TypeError:
			return None
		return float(di)

	def solution_by_user(self, user):
		try:
			sol = Solution.query.filter_by(user=user, question=self).one()
		except NoResultFound:
			return False
		return sol

	def __repr__(self):
		return 'Question(body=%s, author_id=%d)' % (self.body, self.author_id)


class Solution(db.Model):
	__tablename__ = 'solutions'
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text, nullable=False)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)

	question_id = db.Column(db.Integer, db.ForeignKey('questions.id'),
							nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

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
	tagname = db.Column(db.String(64), unique=True, nullable=False)

	'''
	BACKREFS: 
	assoc_users-> Users associated with this tag
	questions -> Collectio of Questions with this Tag
	'''


class UserSetting(db.Model):
	__tablename__ = 'user_settings'
	
	id = db.Column(db.Integer, primary_key=True)
	hide_difficulty = db.Column(db.Boolean, default=False)
	repeat_solved_questions = db.Column(db.Boolean, default=False)
	auto_load_questions = db.Column(db.Boolean, default=False)

	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

	'''
	BACKREFS:
	user -> User associated with this setting. One one user can exist.
	'''
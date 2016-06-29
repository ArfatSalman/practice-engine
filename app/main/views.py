from flask import render_template, session, redirect, url_for
from flask import request, jsonify, flash
from flask_login import current_user, login_required, login_user
from sqlalchemy.exc import SQLAlchemyError
from . import main
from .. import db
from ..models import User, Question, Tag
from .forms import UserTagsForm
from ..question.views import associate_tags
from ..utilities import print_debug, bad_request, add_to_db, add_to_db_ajax
import random


@main.route('/', methods=['GET', 'POST'])
def index():
	login_user(User.query.get(1))
	if current_user.is_authenticated:
		print_debug('User is authenticated in /')
		return redirect(url_for('.home'))
	else:
		return render_template('index.html')


@main.route('/home', methods=['GET', 'POST'])
@login_required
def home():
	form = UserTagsForm()

	tags = current_user.associated_tags.all()
	
	ques = random.sample(set(current_user.get_relevant_question()), 5)

	for q in ques:
		print_debug(q.id)

	ques, sidebar = ques[0], ques[1:]

	return render_template('home.html',
							tags=tags, 
							ques=ques,
							side_ques=sidebar, 
							form=form)


@main.route('/add-user-tags', methods=['POST'])
@login_required
def add_user_tags():
	form = UserTagsForm()

	if form.validate_on_submit():
		tags = associate_tags(form)
		
		if not tags:
			return bad_request('At least one tag is required', 406)
		
		"""This loop checks to see if any matching tags
		for this user exists or not. Since, SQLAlchemy will
		either generate unique contraint error or Add multiple 
		duplicate entries. Hence, it is checked manually."""
		for tag in tags:
			if tag not in current_user.associated_tags:
				current_user.associated_tags.append(tag)
		try:
			db.session.add(current_user)
			db.session.commit()
		except SQLAlchemyError:
			db.session.rollback()
			msg = 'Tags could not be properly saved. Please try again.'
			return jsonify(bad_request(msg, 500))

		result = {}
		for tag in current_user.associated_tags:
			result[tag.tagname] = tag.id
		return jsonify(result)

	return bad_request('Form submission is not correct', 403)


@main.route('/remove-user-tags', methods=['POST'])
@login_required
def remove_user_tags():
	result = {}

	tag_id = request.form.get('id', 0, type=int)
	tag = Tag.query.get_or_404(tag_id)

	current_user.associated_tags.remove(tag)

	try:
		db.session.add(current_user)
		db.session.commit()
	except SQLAlchemyError:
		db.session.rollback()
		msg = 'Tag cannot be removed.'
		return bad_request(msg, 500)
	
	result['message'] = 'Remove Successful'
	return jsonify(result)


@main.route('/upvote', methods=['POST'])
@login_required
def upvote():

	ques_id = request.form.get('question-id', 0, type=int)
	ques = Question.query.get_or_404(ques_id)

	if current_user.has_downvoted(ques):
		msg = "You can't upvote and downvote the same question"
		return bad_request(msg)

	if current_user.has_upvoted(ques):
		current_user.questions_upvoted.remove(ques)
		msg = 'Upvote Removed'
	else:
		current_user.questions_upvoted.append(ques)
		msg = 'Upvoted'

	add_to_db_ajax(current_user, 'Upvote unsuccessful', 500)

	return jsonify(message=msg)


@main.route('/downvote', methods=['POST'])
@login_required
def downvote():
	ques_id = request.form.get('question-id', 0, type=int)
	ques = Question.query.get_or_404(ques_id)

	if current_user.has_upvoted(ques):
		msg = "You can't upvote and downvote the same question"
		return bad_request(msg)

	if current_user.has_downvoted(ques):
		current_user.questions_downvoted.remove(ques)
		msg = 'Downvote Removed'
	else:
		current_user.questions_downvoted.append(ques)
		msg = 'Downvoted'

	add_to_db_ajax(current_user, 'Downvote unsuccessful', 500)

	return jsonify(message=msg)


@main.route('/favourite-question', methods=['POST'])
@login_required
def fav_ques():
	ques_id = request.form.get('question-id', 0, type=int)
	ques = Question.query.get_or_404(ques_id)

	if current_user.has_favourited(ques):
		current_user.questions_fav.remove(ques)
		msg = 'Favourite Removed'
	else:
		current_user.questions_fav.append(ques)
		msg = 'Question Favourited'

	add_to_db_ajax(current_user, 'Favourite Operation unsuccessful', 500)

	return jsonify(message=msg)
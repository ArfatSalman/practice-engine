from flask import render_template, session, redirect, url_for
from flask import request, jsonify, flash
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError
from . import main
from .. import db
from ..models import User, Question, Tag
from .forms import UserTagsForm
from ..question.views import associate_tags, bad_request
from ..utilities import print_debug


@main.route('/', methods=['GET', 'POST'])
def index():
	if current_user.is_authenticated:
		print_debug('User is authenticated in /')
		return redirect(url_for('.home'))
	else:
		return render_template('index.html')


@main.route('/home', methods=['GET', 'POST'])
@login_required
def home():
	form = UserTagsForm()
	
	user = User.query.get(current_user.id)

	tags = user.associated_tags.all()
	
	ques = current_user.get_relevant_question()

	return render_template('home.html',
							tags=tags, 
							ques=ques, 
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


@main.route('/aaa')
def aaa():
	if current_user.is_authenticated:
		print_debug('aaa')
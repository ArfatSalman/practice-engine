from flask import render_template, flash, url_for
from flask import request, redirect, jsonify, abort
from flask_login import current_user, login_required

from sqlalchemy.exc import SQLAlchemyError
from ..models import User, Question, Option, Tag
from . import question
from .. import db

from .forms import PostQuestionForm

'''Helper Functions'''
def get_options(form):
	options = []
	for fieldname, value in form.data.items():
		if fieldname.startswith('option'):
			options.append(Option(body=value,
				is_right=form.data.get('check_'+fieldname)))
	return options

def associate_tags(form):
	tags = []
	for tagname in form.tags.data:
		tag = Tag.query.filter_by(tagname=tagname).first()
		if not tag:
			tag = Tag(tagname=tagname)
		tags.append(tag)
	return tags

@question.route('/post-question', methods=['GET','POST'])
@login_required
def post_question():
	form = PostQuestionForm()

	if form.validate_on_submit():

		options = get_options(form)

		ques = Question(body=form.body.data,
							description=form.description.data,
							user=current_user,
							options=options,
							tags=associate_tags(form))
		try:
			db.session.add(ques)
			db.session.commit()

			flash('Question has been posted successfully.','success')
			return redirect(url_for('main.home'))

		except SQLAlchemyError:
			db.session.rollback()
			flash('There was a problem posting the question.', 'danger')
			return redirect(url_for('.post_question'))
	return render_template('question/post-question.html', form=form)


@question.route('/edit-question/<int:id>', methods=['GET','POST'])
@login_required
def edit_question(id):
	ques = Question.query.get_or_404(id)

	if current_user != ques.user:
		abort(403)

	form = PostQuestionForm()

	if form.validate_on_submit():
		ques.body = form.body.data
		ques.description = form.body.description
		
		"""Delete all the previous options."""
		try:
			for option in ques.options:
				db.session.delete(option)
			#db.session.commit()
		except SQLAlchemyError:
			db.session.rollback()
			flash('There was a problem updating the question','danger')
			return redirect(url_for('.edit_question', id=ques.id))
		
		"""Add new options"""	
		ques.options = get_options(form)

		ques.tags = associate_tags(form)

		try:
			db.session.add(ques)
			db.session.commit()
			flash('Question %s updated Successfully.' % ques.id, 'success')
			return redirect(url_for('main.home'))
		except SQLAlchemyError, e:
			db.session.rollback()
			flash('%s There was a problem updating the question ' % str(e), 'danger')
			return redirect(url_for('.edit_question', id=ques.id))
	
	form.body.data = ques.body
	form.description.data = ques.description

	options = ques.options
	if options:
		try:
			if options[0]:
				form.option1.data, form.check_option1.data = options[0].body, options[0].is_right
			if options[1]:
				form.option2.data, form.check_option2.data = options[1].body, options[1].is_right
			if options[2]:
				form.option3.data, form.check_option3.data = options[2].body, options[2].is_right
			if options[3]:
				form.option4.data, form.check_option4.data = options[3].body, options[3].is_right
		except IndexError:
			pass
	
	"""Build tag list for the form."""
	tags = []
	for tag in ques.tags:
		tags.append(tag.tagname)

	form.tags.data = tags

	return render_template('question/edit-question.html', form=form)

@question.route('/get-tags', methods=['GET'])
@login_required
def get_tags():
	query = request.args.get('query')
	tags = Tag.query.filter(Tag.tagname.like('%{}%'.format(query)))
	
	result = {}
	for i, tag in enumerate(tags):
		result[i]=tag.tagname
	return jsonify(result)


@question.route('/check-answer', methods=['POST'])
@login_required
def check_answer():
	ques_id = request.form.get('question-id', 0, type=int)
	option_selected = request.form.getlist('opt')
	
	ques = Question.query.get_or_404(ques_id)

	result = {}
	for option_id in option_selected:
		option = Option.query.get(int(option_id))
		if option.is_right:
			result[str(option.id)]=True
		else:
			result[str(option.id)]=False

	return jsonify(result)
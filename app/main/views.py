from flask import render_template, session, redirect, url_for, jsonify, flash
from flask_login import current_user, login_required

from . import main
#from .forms import NameForm
from .. import db
from ..models import User, Question


@main.route('/', methods=['GET', 'POST'])
def index():
	if current_user.is_authenticated:
		return redirect(url_for('.home'))
	else:
		return render_template('index.html')

@main.route('/home', methods=['GET', 'POST'])
@login_required
def home():
	ques = Question.query.filter_by(id=6).first()

	return render_template('home.html', ques=ques)

@main.route('/')
@login_required
def pro():
	return 'pro'
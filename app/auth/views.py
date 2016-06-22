from flask import session, redirect, url_for, jsonify, flash, request
from flask_login import login_user, login_required, logout_user
from flask_login import current_user
from . import auth
from .. import db, google
from ..models import User
import requests

GOOGLE_OAUTH_USERINFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'

@auth.route('/google-login')
def google_login():
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	return google.authorize(
		callback=url_for('.google_authorized', _external = True))


@auth.route('/oauth2callback')
@google.authorized_handler
def google_authorized(resp):
	next_url = request.args.get('next') or url_for('main.index')

	if resp is None:
		return 'Access Denied %s' % (request.args['error_reason'])

	'''
	The tokengetter return either None or a tuple (token, secret).
	The google_oauth_token is returned by tokengetter
	'''
	session['google_oauth_token'] = (resp['access_token'], '')

	userinfo = requests.get(GOOGLE_OAUTH_USERINFO_URL,
		params=dict(access_token=resp['access_token'])).json()

	session['user_picture'] = userinfo['picture']
	session['username'] = userinfo['name']

	user = User.query.filter_by(username=userinfo['email']).first()

	if not user:
		user = User(userinfo['email'])
		db.session.add(user)
		db.session.commit()

	login_user(user, remember=True)

	return redirect(next_url)

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been Logged Out.', 'success')
	return redirect(url_for('main.index'))


@google.tokengetter
def get_google_oauth_token():
	return session.get('google_ouath_token')


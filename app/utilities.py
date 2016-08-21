from __future__ import print_function
import sys

from . import db
from sqlalchemy.exc import SQLAlchemyError
from flask import (
	flash, 
	redirect, 
	jsonify, 
	url_for, 
	request, 
	current_app
	)



def print_debug(*args, **kwargs):
	return print(*args, file=sys.stderr, **kwargs)

def dual_response(message, category='success', redir=''):
	if request.is_xhr:
		return jsonify(message=message)
	else:
		flash(message, 'success')
		if redir:
			return redirect(redir)
		return redirect(url_for('main.home'))

def bad_request(message, status_code=403, redir='', category='danger'):
	if request.is_xhr:
		response = jsonify(message=message, category=category)
		response.status_code = status_code
	else:
		flash(message, category)
		if redir:
			return redirect(redir)
		return redirect(url_for('main.index'))
	return response


def add_to_db_ajax(obj, msg='Something went wrong', status_code=403):
	try:
		db.session.add(obj)
		db.session.commit()
	except SQLAlchemyError:
		db.session.rollback()
		return bad_request(msg, status_code)


def add_to_db(obj, msg='Something went wrong', category='danger'):
	try:
		db.session.add(obj)
		db.session.commit()
	except SQLAlchemyError:
		db.session.rollback()
		return bad_request(msg, 403)
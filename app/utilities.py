from __future__ import print_function
import sys

from . import db
from sqlalchemy.exc import SQLAlchemyError
from flask import flash, redirect

def print_debug(*args, **kwargs):
	return print(*args, file=sys.stderr, **kwargs)


def bad_request(message, status_code=403):
    response = jsonify({'message': message})
    response.status_code = status_code
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
		flash(msg, category)
		return redirect(url_for('main.home'))
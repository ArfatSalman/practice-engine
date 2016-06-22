from __future__ import print_function
import sys

from . import db
from sqlalchemy.exc import SQLAlchemyError
from flask import flash, redirect

def print_debug(*args, **kwargs):
	return print(*args, file=sys.stderr, **kwargs)


def add_to_database(obj, msg='Something went wrong', category='danger', supress_msg = False):
	try:
		db.session.add(obj)
		db.session.commit()
	except SQLAlchemyError:
		if not supress_msg:
			flash(msg, category)
		return redirect(url_for('main.home'))
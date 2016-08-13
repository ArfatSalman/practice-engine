from flask import render_template
from sqlalchemy.exc import *
from . import main

'''A difference when writing error handlers inside a blueprint is that if the errorhandler
decorator is used, the handler will only be invoked for errors that originate in the blue
print. To install application-wide error handlers, the app_errorhandler must be used
instead.'''

@main.app_errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500

@main.app_errorhandler(OperationalError)
def aa(e):
	return 'operational error %s ' % e
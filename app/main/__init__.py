from datetime import datetime
from flask import Blueprint

main = Blueprint('main', __name__)
'''
Blueprint takes the Blueprint name and the module
or package where the Blueprint s located.

Importing modules causes the routes to be associated
with the Blueprint.

Modules are imported at the end to avoid circular dependecies
since views.py and errors.py need to import main Blueprint.
'''

@main.app_template_filter('time')
def format_time(time):
    fmt = "%b %d '%y at %H:%M"
    return time.strftime(fmt) + ' UTC'

@main.app_template_filter('timedelta')
def timedelta(time):
	td = datetime.utcnow() - time

	if td.total_seconds() < 86400:
		hours = td.total_seconds() // 3600
		if hours >= 0:
			return "%d hours ago." % hours
		else:
			"0 hours ago."
	elif td.total_seconds() < 2*86400:
		return "%d day ago" % td.days
	else:
		return "%d days ago" % td.days


from . import views, errors
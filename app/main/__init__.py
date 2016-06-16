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
from . import views, errors
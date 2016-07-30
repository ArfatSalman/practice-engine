#!/usr/bin/env python

import os
from app import create_app, db
from app.models import (User, Question, Option, Tag,
						tags_assoc, user_tags_assoc,
						FavouriteQuestionAssoc,
						UpvoteQuestionAssoc,
						DownvoteQuestionAssoc,
						SolvedQuestionsAssoc,
						Solution,
						UserSetting)

from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

# Test Coverage library setup
COV = None
if os.environ.get('COVERAGE'):
	import coverage
	COV = coverage.coverage(branch=True, include='app/*')
	COV.start()


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
	return dict(app=app, 
				db=db,
				Question=Question,
				User=User,
				Option=Option,
				Tag=Tag,
				tags_assoc=tags_assoc,user_tags_assoc=user_tags_assoc,
				UpvoteQuestionAssoc=UpvoteQuestionAssoc,
				DownvoteQuestionAssoc=DownvoteQuestionAssoc,
				SQ=SolvedQuestionsAssoc,
				FQ=FavouriteQuestionAssoc,
				Solution=Solution,
				UserSetting=UserSetting)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test(coverage=False):
	if coverage and not os.environ.get('COVERAGE'):
		import sys
		os.environ['COVERAGE'] = '1'
		# This line re-run this script with same argument
		os.execvp(sys.executable, [sys.executable] + sys.argv)

	import unittest
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=3).run(tests)

	if COV:
		COV.stop()
		COV.save()

		print 'Coverage Summary'

		COV.report()
		basedir = os.path.abspath(os.path.dirname(__file__))
		covdir = os.path.join(basedir, 'tests/coverage')
		COV.html_report(directory=covdir)
		print 'HTML Version in %s' % covdir
		COV.erase()

if __name__=='__main__':
	manager.run()
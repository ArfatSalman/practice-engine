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
def test():
	import unittest
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=3).run(tests)

if __name__=='__main__':
	manager.run()
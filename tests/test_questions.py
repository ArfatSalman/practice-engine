import unittest
from app import create_app, db
from flask import current_app
from app.models import Question, User, Option

class QuestionsTestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def test_options_deleted_after_questions_deleted(self):
		u = User('a@aaaa.com')

		options = [
					Option(body='This in option 1',is_right=True),
					Option(body='This is option 2'),
					Option(body='This is option 3')
					]

		ques = Question(body='test Question',
						user=u,
						options=options)

		db.session.add(ques)
		db.session.add(u)
		db.session.commit()

		ques_query_obj = Question.query.filter_by(id = ques.id).one()

		self.assertTrue(ques_query_obj)

		db.session.delete(ques)
		db.session.commit()

		opts = Option.query.all()

		self.assertTrue(opts == [])


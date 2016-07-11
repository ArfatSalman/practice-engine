import unittest
from app import create_app, db
from flask import current_app
from app.models import (Question, 
						User, 
						Option, 
						Tag, 
						tags_assoc)


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
		'''
		When a question is deleted, its related options should be 
		deleted along with it.
		'''
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

	def test_questions_tag_assoc(self):
		'''
		When a question is deleted, its related rows from 
		Question-Tags-Assoc should be deleted, but not the 
		Tags itself.

		'''
		u = User('test@test.com')

		tags = [
				Tag(tagname="Test Tag 1"),
				Tag(tagname="Test Tag 2"),
				Tag(tagname='Test Tag 3')
				]

		ques = Question(body='test Question',
						user=u,
						tags=tags)

		db.session.add(ques)
		db.session.commit()

		q = db.session.query(Question).get(1)
		self.assertTrue(q) # Question Exists
		
		tags = Tag.query.all()
		self.assertTrue(tags) # tags Exist

		assocs = db.session.query(tags_assoc).all()
		self.assertTrue(assocs != []) # assocs exists

		db.session.delete(q)
		db.session.commit()

		q = db.session.query(Question).get(1)
		self.assertFalse(q) # question has been deleted

		tags = Tag.query.all()
		self.assertTrue(tags) # Tags should exist independent of Question

		assocs = db.session.query(tags_assoc).all()
		self.assertTrue(assocs == [])

	def test_user_is_deleted(self):
		u = User('test@test.com')

		tags = [
				Tag(tagname="Test Tag 1"),
				Tag(tagname="Test Tag 2"),
				Tag(tagname='Test Tag 3')
				]
		
		ques = Question(body='test Question',
						user=u,
						tags=tags)

		db.session.add(ques)
		db.session.commit()

		db.session.delete(u)
		db.session.commit()

		u = User.query.all()
		self.assertFlase(u) # User should be deleted

		q = Question.query.all()
		self.assertTrue(q) # But the question shouldn't 


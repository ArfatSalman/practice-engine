import unittest
from app import create_app, db
from flask import current_app, url_for
from flask_login import login_user
from app.models import User

class MainTestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()

		db.session.add(User('test@test.com'))
		db.session.commit()
		
		self.client = self.app.test_client(use_cookies=True)

	def tearDown(self):
		db.drop_all()
		self.app_context.pop()

	def test_home_page(self):
		response = self.client.get(url_for('main.index'), 
									follow_redirects=True)
		text = 'Please choose at least one topic.'
		print 'Checking the response'
		self.assertTrue(text in response.get_data(as_text=True))
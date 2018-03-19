import os

"""Absolute path for defining the path of SQLite database file"""
basedir = os.path.abspath(os.path.dirname(__file__))


SECRET_KEY = os.environ['SECRET_KEY']
MAIL_SERVER = os.environ['MAIL_SERVER']
MAIL_USERNAME = os.environ['MAIL_USERNAME']
MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
DATABASE_URL = os.environ['DATABASE_URL']

class Config:
	"""This class defines the configurations common to the app.
		It is inherited by other classes to add custom configurations.
	"""
	SECRET_KEY = SECRET_KEY
	SQLALCHEMY_COMMIT_ON_TEARDOWN = False
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SQLALCHEMY_POOL_RECYCLE = 299
	PER_PAGE_LIMIT = 2

	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	DEBUG = True
	MAIL_SERVER = MAIL_SERVER
	MAIL_PORT = 465
	MAIL_USE_TLS = False
	MAIL_USE_SSL = True
	MAIL_USERNAME = MAIL_USERNAME
	MAIL_PASSWORD = MAIL_PASSWORD
	SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost/test'
	SQLALCHEMY_ECHO = False
	REMEMBER_COOKIE_HTTPONLY = True


class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_ECHO = False
	SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost/testing'
	SERVER_NAME = 'localhost:5000'


class ProductionConfig(Config):
	MAIL_SERVER = MAIL_SERVER
	MAIL_PORT = 465
	MAIL_USE_TLS = False
	MAIL_USE_SSL = True
	MAIL_USERNAME = MAIL_USERNAME
	MAIL_PASSWORD = MAIL_PASSWORD
	SQLALCHEMY_DATABASE_URI = DATABASE_URL

config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,
	'production': ProductionConfig,
	'default': DevelopmentConfig
}


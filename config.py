import os

"""Absolute path for defining the path of SQLite database file"""
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
	"""This class defines the configurations common to the app.
		It is inherited by other classes to add custom configurations.
	"""
	SECRET_KEY = "\x079Z\x9c%Z\xcf/f\x1f\x17\xad\x18\xcb+eIP%a-\x99M:\xaf\x82\x98\x9e\xe3B4"
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True

	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = ''
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost/test'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
        #os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
        os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://Arfat:arfat78692@mysql.server/Arfat$arfat'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


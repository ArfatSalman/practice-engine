from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_oauth import OAuth
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'main.index'
login_manager.login_message_category = 'danger'

db = SQLAlchemy()

oauth = OAuth()

google = oauth.remote_app('google',
	base_url = 'https://www.google.com/accounts/',
	authorize_url = 'https://accounts.google.com/o/oauth2/auth',
	request_token_url = None,
	request_token_params={
			'scope': 'https://www.googleapis.com/auth/userinfo.email',
			'response_type': 'code'
		},
	access_token_url='https://accounts.google.com/o/oauth2/token',
	access_token_method='POST',
	access_token_params={'grant_type' : 'authorization_code'},
	consumer_key='90862200578-bi07ptn7ltqo52rr21hbc3efoo1jcvje.apps.googleusercontent.com',
	consumer_secret='yOrrkxnJUC48lN8dsYTx6ovy'
	)

def create_app(config_name):
	'''The flask object acts as a central object. It is
	 passed the name of module or package of app.
	'''
	app = Flask(__name__)

	# config is a dictionary
	'''Objects are either modules or classes.
		Only Uppercase variables in that object are stored.
	'''
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)
	
	db.init_app(app)
	login_manager.init_app(app)

	'''The blueprint is registered here.'''
	from main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	from auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint)

	from question import question as question_bluprint
	app.register_blueprint(question_bluprint)

	return app
from app.models import *
from app import create_app, db

# users 
def create_database():
	u1 = User('test1@gmail.com')
	u2 = User('test2@gmail.com')
	u3 = User('test3@gmail.com')

	db.session.add_all([u1, u2, u3])

	db.session.commit()

def del_database():
	db.drop_all()

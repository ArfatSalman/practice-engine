from . import db
from .models import User

user_coll = []
for user in User.query.all():
	user.streak_updated = False
	user_coll.append(user)

db.session.add_all(user_coll)
db.session.commit()
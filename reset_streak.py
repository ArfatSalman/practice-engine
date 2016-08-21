from manage import app
from app import db
from app.models import User

with app.app_context(): 

    user_coll = []
    for user in User.query.all():
        user.streak_updated = False
        user_coll.append(user)

    db.session.add_all(user_coll)
    db.session.commit()
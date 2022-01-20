from . import db
from . import login_manager

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class UserChange(db.Model):
    __tablename__ = 'user_changes'
    id = db.Column(db.Integer, primary_key=True)
    neo_id = db.Column(db.Integer, nullable=False)
    time = db.Column(db.BIGINT)
    username = db.Column(db.String(20), nullable=False)
    property = db.Column(db.String(10), nullable=False)
    property_value = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<User %s, Neo_Id %r>' % (self.username, self.neo_id)

# class Link(db.Model):
#     __tablename__ = 'links'
#     id = db.Column(db.Integer, primary_key=True)
#     time = db.Column(db.Integer)
#     user = db.Column(db.String(20), nullable=True)
#     # start_node = db.Column(db.String(40), nullable=False)
#     # end_node = db.Column(db.String(40), nullable=False)
#     # type = db.Column(db.String(20))
#     link_property = db.Column(db.String(10), nullable=False)
#     link_property_value = db.Column(db.String(255), nullable=False)
#
#     def __repr__(self):
#         return '<User %s, LinkType %r>' % (self.user, self.type)

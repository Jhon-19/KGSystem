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

class UserNodeChange(db.Model):
    __tablename__ = 'user_node_changes'
    id = db.Column(db.Integer, primary_key=True)
    neo_id = db.Column(db.Integer, nullable=False)
    time = db.Column(db.BIGINT)
    username = db.Column(db.String(20), nullable=False)
    property = db.Column(db.String(10), nullable=False)
    property_value = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<User %s, Neo_Id %r>' % (self.username, self.neo_id)

class UserLinkChange(db.Model):
    __tablename__ = 'user_link_changes'
    id = db.Column(db.Integer, primary_key=True)
    neo_id = db.Column(db.Integer, nullable=False)
    time = db.Column(db.BIGINT)
    start_node = db.Column(db.Integer, nullable=False)
    end_node = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(20), nullable=False)
    property = db.Column(db.String(10), nullable=False)
    property_value = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<User %s, Neo_Id %r, StartNode %s, EndNode %s>' \
               % (self.username, self.neo_id, self.start_node, self.end_node)


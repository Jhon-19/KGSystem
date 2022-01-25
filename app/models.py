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
    neo_link_id = db.Column(db.Integer, nullable=False)
    time = db.Column(db.BIGINT)
    username = db.Column(db.String(20), nullable=False)
    property = db.Column(db.String(10), nullable=False)
    property_value = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<User %s, Neo_Id %r>' \
               % (self.username, self.neo_link_id)

class UserNodeAdd(db.Model):
    __tablename__ = 'user_node_adds'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.BIGINT)
    username = db.Column(db.String(20), nullable=False)

    user_node_id = db.Column(db.Integer, nullable=False)
    Label = db.Column(db.String(10), nullable=False)
    title = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return '<User %s, Neo_Id %r>' % (self.username, self.user_node_id)

class UserLinkAdd(db.Model):
    __tablename__ = 'user_link_adds'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.BIGINT)
    username = db.Column(db.String(20), nullable=False)

    user_link_id = db.Column(db.Integer, nullable=False)
    Type = db.Column(db.String(10), nullable=False)
    start_node = db.Column(db.Integer, nullable=False)
    end_node = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<User %s, Neo_Id %r, StartNode %s, EndNode %s>' \
               % (self.username, self.user_link_id, self.start_node, self.end_node)

#定义前后端交互的Neo4j数据的json格式
class Node():

    def __init__(self, ID, label_list, record_node=None, title=''):
        self.ID = ID
        self.Label = self.format_labels(label_list)
        if record_node != None:
            self.title = self.add_node_title(record_node)
        else:
            self.title = title

    def get_dict(self):
        node = {
            'ID': self.ID,
            'Label': self.Label,
            'title': self.title
        }
        return node

    def format_labels(self, label_list):
        return ', '.join(label_list)

    def add_node_title(self, record_node):
        title = ''
        if 'title' in record_node:
            title = record_node['title']
        elif 'name' in record_node:
            title = record_node['name']
        return title

class Link():

    def __init__(self, ID, Type, source, target, link_list):
        self.ID = ID
        self.Type = Type
        self.source = source
        self.target = target
        self.link_list = link_list
        self.link_order = 0 # 如果节点之间有两条边，则记录每条边的顺序
        self.order_link()

    def get_dict(self):
        link = {
            'ID': self.ID,
            'Type': self.Type,
            'source': self.source,  # d3.js中的id默认为节点数组中的下标
            'target': self.target,
            'link_order': self.link_order
        }
        return link

    def order_link(self):
        for link in self.link_list:
            if self.is_same_link(link):
                self.link_order += 1

        if int(self.ID) < 0: #用户添加的边为反方向添加
            self.link_order = -self.link_order-1

    def is_same_link(self, link2):
        return (self.source == link2['source'] and self.target == link2['target']) \
               or (self.source == link2['target'] and self.target == link2['source'])
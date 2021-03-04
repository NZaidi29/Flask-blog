from datetime import datetime
from blog import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

#reference for the many to many relationship method
#date accessed 12/02/2021
#https://www.youtube.com/watch?v=OvhoYbjtiKc
#https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
#fave posts table
favs= db.Table('favs', db.Column('user_id', db.Integer, db.ForeignKey('user.id')), db.Column('post_id', db.Integer, db.ForeignKey('post.id')))

likes= db.Table('likes', db.Column('user_id', db.Integer, db.ForeignKey('user.id')), db.Column('post_id', db.Integer, db.ForeignKey('post.id')))

#class for post model in database
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(40), nullable=False, default='default.jpg')
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tag = db.Column(db.Text, nullable=True)

    comment = db.relationship('Comment', backref='post', lazy=True)

    def likes(self):#this function is to make getting and displaying number of likes easy with post.likes()
        count = 0
        for i in self.likers:#iterate over this as self.likers has no length as its an AppenderBaseQuery which doesnt have a length
            count += 1
        return str(count)

    def __repr__(self):
        return f"Post('{self.date}', '{self.title}', '{self.content}')"

#class for user id in database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash=db.Column(db.String(128))
    password = db.Column(db.String(60), nullable=False)

    is_admin = db.Column(db.Boolean, nullable=False, default=False)#admins are special so they get a separate block to the rest of the columns

    post = db.relationship('Post', backref='user', lazy=True)
    comment = db.relationship('Comment', backref='user', lazy=True)

    favourites = db.relationship('Post', secondary=favs, backref=db.backref('followers', lazy='dynamic'))
    liked = db.relationship('Post', secondary=likes, backref=db.backref('likers', lazy='dynamic'))

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
#making sure we cant accidentall read peoples passwords becuase security
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
#setting the password
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self,password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#class for comments left by users
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)#only registered users can comments

    def __repr__(self):
        return f"Post('{self.date}', '{self.content}')"

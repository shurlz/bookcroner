from bookapp import app
from flask_login import UserMixin
from bookapp import bcrypt
from bookapp import db, login_manager
import datetime

@login_manager.user_loader
def load_user(user_id):
    return users.query.get(int(user_id))

class users(db.Model,UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(),unique=True)
    password_hash = db.Column(db.String(),unique=False)
    user_content = db.relationship('users_contents', backref='author', lazy = True)
    
    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, password_unhashed):
        self.password_hash = bcrypt.generate_password_hash(password_unhashed).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

class users_contents(db.Model,UserMixin):
    id = db.Column(db.Integer(),primary_key=True)
    book_name = db.Column(db.String(), nullable=False)
    message = db.Column(db.Text(),nullable=True)
    start_time = db.Column(db.DateTime(),nullable=True)
    end_time = db.Column(db.DateTime(),nullable=True)
    owner = db.Column(db.Integer(), db.ForeignKey('users.id'))

class search_history(db.Model,UserMixin):
    id = db.Column(db.Integer(),primary_key=True)
    search = db.Column(db.String(),nullable=False)

class all_books(db.Model,UserMixin):
    id = db.Column(db.Integer(),primary_key=True)
    books = db.Column(db.String(),nullable=False,unique=True)

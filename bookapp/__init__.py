from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_moment import Moment
from flask_migrate import Migrate
import pickle
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['SECRET_KEY']='secret ket'
app.config['SQLALCHEMY_TRACE_MODIFICATIONS']=False
app.config['GOOGLE_CLIENT_ID'] = "google client id"
app.config['GOOGLE_CLIENT_SECRET'] = "google client secret key"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
moment = Moment(app)
login_manager = LoginManager(app)
migrate = Migrate(app,db)
oauth = OAuth(app)

login_manager.login_view= 'login'
login_manager.login_message_category = 'success'
from bookapp import routes

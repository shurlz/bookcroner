from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import Length, Email ,DataRequired ,EqualTo , ValidationError
from bookapp.models import users

class SignUpForm(FlaskForm):

    def validate_email_address(self,inputed_email):
        new_email = users.query.filter_by(email=inputed_email.data).first()
        if new_email:
            raise ValidationError('email address already in use by another user')

    email_address = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired(),Length(min=8)])
    confirm_password = PasswordField(validators=[EqualTo('password'), DataRequired()])
    submit = SubmitField(label='Sign Up')

class TodoList(FlaskForm):
    book_name = StringField(validators=[DataRequired()])
    message = TextAreaField(validators=[DataRequired()])
    start_time = StringField()
    end_time = StringField(validators=[DataRequired()])
    submit = SubmitField(label='upload')

class BookSearch(FlaskForm):
    query_item = StringField(DataRequired())
    submit = SubmitField(label='search')

class SignInForm(FlaskForm):
    email = StringField(validators=[DataRequired()])
    password = PasswordField(DataRequired())
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField(label='Sign In')

class CreatePrompt(FlaskForm):
    submit = SubmitField(label='create')

class Edit(FlaskForm):
    submit = SubmitField(label='Edit')

class Delete(FlaskForm):
    submit = SubmitField(label='Delete')
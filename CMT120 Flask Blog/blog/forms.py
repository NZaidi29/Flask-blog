from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp, InputRequired
from blog.models import User


class RegistrationForm(FlaskForm):

    firstname = StringField('First Name', validators=[DataRequired(), Length(max=20)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(max=20)])
    username = StringField('Username', validators=[DataRequired(), Regexp('^.{3,15}$', message='Username should be 3-15 characters')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=3, max=20, message='Password must be 3-20 characters long.')])
    confirm_password =PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords do not match.')])
    submit = SubmitField('Register')

    def validate_username(self, username):#nesting these to ensure they are imported along with the form
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists.')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('Email already used, only one account per email allowed.')

class LoginForm(FlaskForm):

    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CommentForm(FlaskForm):
    # reference for enlarging the size of an input using TextAreaField
    # accessed 18/02/2021
    # https://stackoverflow.com/questions/38749364/wtforms-form-field-text-enlargement
    comment = TextAreaField('Comment', validators=[InputRequired()])
    submit = SubmitField('Post comment')

class SortForm(FlaskForm):
    # reference for SelectField
    # date accessed 10/02/2021
    # https://wtforms.readthedocs.io/en/2.3.x/fields/
    sorting = SelectField('Sort by', choices=[(''),('Newest'),('Oldest')], validate_choice=True)#SelectField creates a drop down
    submit = SubmitField('Sort')

class SearchForm(FlaskForm):

    query = StringField('Search', validators=[InputRequired(),Regexp('^[a-zA-Z0-9]')])
    submit = SubmitField('Search')

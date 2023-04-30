from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField , PasswordField , SubmitField , BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length , Email , EqualTo, ValidationError
from firsttry.models import User

def validate_field_username(form, username):
    user = User.query.filter_by(username=username.data).first()
    if user:
        raise ValidationError('That username is taken. Please choose a different one')
        
def validate_field_email(form, email):
    user = User.query.filter_by(email=email.data).first()
    if user:
        raise ValidationError('That email is taken. Please choose a different one')
        


class RegisterationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20), validate_field_username])
    email = StringField('Email', validators=[DataRequired(), Email(), validate_field_email])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired() , EqualTo('password')])
    submit = SubmitField('Sign Up')


    

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

        

def validate_field_username_account(form, username):
    if username.data != current_user.username:
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one')
        
def validate_field_email_account(form, email):
    if email.data != current_user.email:
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20), validate_field_username_account])
    email = StringField('Email', validators=[DataRequired(), Email(), validate_field_email_account])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')



def validate_field_email_reset(form, email):
    user = User.query.filter_by(email=email.data).first()
    if user is None:
        raise ValidationError('There is no account with that email. You may want to register first')
    

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), validate_field_email_reset])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm) :
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired() , EqualTo('password')])
    submit = SubmitField('Reset Password')




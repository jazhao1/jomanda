from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Optional, Email, EqualTo, Length

from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep Me Logged in')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username*', validators=[DataRequired()])
    nickname = StringField('Nickname')
    email = StringField('Email*', validators=[DataRequired(), Email()])
    password = PasswordField('Password*', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password*', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
    email = StringField('Email*', validators=[DataRequired()])
    nickname = StringField('Nickname')
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Update')

class EditArtistForm(FlaskForm):
    name = StringField('Name*', validators=[DataRequired()])
    twitter_handle = StringField('Twitter Handle', render_kw={'maxlength': 15})
    pixiv_id = IntegerField('Pixiv ID', validators=[Optional()])
    DA_username= StringField('Deviant Art Username', render_kw={'maxlength': 15})
    tumblr_username = StringField('Tumblr Username', render_kw={'maxlength': 15})
    other_info  = TextAreaField('Other Info', validators=[Length(min=0, max=140)])
    update = SubmitField('Update')
    add = SubmitField('Add')


class PostForm(FlaskForm):
    post = TextAreaField('Post Comment', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Post')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class UpdatePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    new_password2 = PasswordField(
        'Repeat New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Update')
    
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CompositionForm(FlaskForm):
    title = StringField('Composition Title', validators=[DataRequired(), Length(max=100)])
    music_name = StringField('Music Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    genre = SelectField('Genre', choices=[
        ('', 'Select Genre'),
        ('classical', 'Classical'),
        ('jazz', 'Jazz'),
        ('rock', 'Rock'),
        ('pop', 'Pop'),
        ('electronic', 'Electronic'),
        ('folk', 'Folk'),
        ('ambient', 'Ambient'),
        ('soundtrack', 'Soundtrack'),
        ('other', 'Other')
    ])
    submit = SubmitField('Save Composition')

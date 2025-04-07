from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Nome de usuário já está em uso. Por favor, escolha outro.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email já registrado. Por favor, use outro email.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class CompositionForm(FlaskForm):
    title = StringField('Título da Composição', validators=[DataRequired(), Length(max=100)])
    music_name = StringField('Nome da Música', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Descrição')
    genre = SelectField('Gênero', choices=[
        ('', 'Selecione o Gênero'),
        ('classical', 'Clássico'),
        ('jazz', 'Jazz'),
        ('rock', 'Rock'),
        ('pop', 'Pop'),
        ('electronic', 'Eletrônica'),
        ('folk', 'Folk'),
        ('ambient', 'Ambiente'),
        ('soundtrack', 'Trilha Sonora'),
        ('other', 'Outro')
    ])
    submit = SubmitField('Salvar Composição')

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User, Genre

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
    genre = SelectField('Gênero', choices=[])  # Será preenchido dinamicamente
    submit = SubmitField('Salvar Composição')
    
    def __init__(self, *args, **kwargs):
        super(CompositionForm, self).__init__(*args, **kwargs)
        # Preenchendo o dropdown com gêneros do banco de dados
        self.genre.choices = [('', 'Selecione o Gênero')] + [(str(g.id), g.name) for g in Genre.query.order_by(Genre.name).all()]

class GenreForm(FlaskForm):
    name = StringField('Nome do Gênero', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Descrição')
    submit = SubmitField('Salvar Gênero')
    
    def validate_name(self, name):
        # Verificar se o gênero já existe (ignorando maiúsculas/minúsculas)
        genre = Genre.query.filter(Genre.name.ilike(name.data)).first()
        if genre and (not hasattr(self, '_obj') or genre != self._obj):
            raise ValidationError('Esse gênero já existe. Por favor, escolha outro nome.')

class UserAdminForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    is_admin = BooleanField('Administrador')
    submit = SubmitField('Salvar Usuário')

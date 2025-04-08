from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, BooleanField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional

from models import User, Genre, Composition


class RegistrationForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nome de usuário já está em uso. Por favor, escolha outro.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email já está registrado. Por favor, utilize outro ou faça login.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')


class CompositionForm(FlaskForm):
    title = StringField('Título da Composição', validators=[DataRequired(), Length(max=100)])
    music_name = StringField('Nome da Música', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Descrição')
    genre = SelectField('Gênero', choices=[])  # Será preenchido dinamicamente
    audio_file = FileField('Arquivo de Áudio (MP3, máx. 3MB)', 
                          validators=[
                              FileAllowed(['mp3'], 'Apenas arquivos MP3 são permitidos!'),
                              # FileRequired() não é obrigatório para permitir edição sem alterar o arquivo
                          ])
    submit = SubmitField('Salvar Composição')
    
    def __init__(self, *args, **kwargs):
        super(CompositionForm, self).__init__(*args, **kwargs)
        # Adiciona uma opção vazia para permitir que não selecione nenhum gênero
        self.genre.choices = [('', 'Selecione o Gênero')] + [(str(g.id), g.name) for g in Genre.query.order_by(Genre.name).all()]


class GenreForm(FlaskForm):
    name = StringField('Nome do Gênero', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Descrição')
    submit = SubmitField('Salvar Gênero')
    
    def validate_name(self, name):
        # Validar apenas se for um formulário novo ou se o nome mudou
        if hasattr(self, '_obj') and self._obj.name == name.data:
            return
        
        genre = Genre.query.filter_by(name=name.data).first()
        if genre:
            raise ValidationError('Este nome de gênero já existe. Por favor, escolha outro.')


class UserAdminForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    is_admin = BooleanField('Administrador')
    submit = SubmitField('Salvar Usuário')


class SingerForm(FlaskForm):
    name = StringField('Nome do Cantor', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Telefone/WhatsApp', validators=[Length(max=20)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)])
    notes = TextAreaField('Observações')
    exclusive_until = DateField('Exclusividade até', format='%Y-%m-%d', validators=[Optional()])
    composition = SelectField('Composição', choices=[], validators=[DataRequired()])
    submit = SubmitField('Salvar Cantor')
    
    def __init__(self, *args, user=None, **kwargs):
        super(SingerForm, self).__init__(*args, **kwargs)
        if user:
            # Adicionar apenas as composições do usuário atual
            self.composition.choices = [(str(c.id), f"{c.title} - {c.music_name}") 
                                        for c in user.compositions.order_by(Composition.title).all()]

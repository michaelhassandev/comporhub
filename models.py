from datetime import datetime, timedelta
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)  # Flag para administrador
    compositions = db.relationship('Composition', backref='composer', lazy='dynamic')
    singers = db.relationship('Singer', backref='owner', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    compositions = db.relationship('Composition', backref='genre_info', lazy='dynamic')
    
    def __repr__(self):
        return f'<Genre {self.name}>'

class Composition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    music_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    genre = db.Column(db.String(50))  # Manter para compatibilidade
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'))  # Nova relação com tabela de gêneros
    audio_file = db.Column(db.String(255))  # Caminho para o arquivo de áudio
    audio_file_size = db.Column(db.Integer)  # Tamanho do arquivo em bytes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    singers = db.relationship('Singer', backref='composition', lazy='dynamic')
    
    def __repr__(self):
        return f'<Composition {self.title}>'

class Singer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    notes = db.Column(db.Text)
    exclusive_until = db.Column(db.Date, nullable=True)  # Data de término da exclusividade
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    composition_id = db.Column(db.Integer, db.ForeignKey('composition.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Proprietário do cantor

    def __repr__(self):
        return f'<Singer {self.name}>'
    
    @property
    def days_to_expiration(self):
        """Retorna o número de dias até o término da exclusividade"""
        if not self.exclusive_until:
            return None
        
        today = datetime.utcnow().date()
        delta = (self.exclusive_until - today).days
        return delta
    
    @property
    def exclusivity_status(self):
        """Retorna o status da exclusividade: 'válida', 'vence em breve', 'expirada' ou 'não definida'"""
        if not self.exclusive_until:
            return "não definida"
        
        days = self.days_to_expiration
        
        if days < 0:
            return "expirada"
        elif days <= 15:  # Aviso de 15 dias antes do vencimento
            return "vence em breve"
        else:
            return "válida"

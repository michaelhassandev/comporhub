from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, send_file
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime, timedelta
import os
import uuid
from sqlalchemy import desc
from werkzeug.utils import secure_filename
import werkzeug

from app import db
from models import User, Composition, Genre
from forms import RegistrationForm, LoginForm, CompositionForm, GenreForm, UserAdminForm

# Criar um blueprint para todas as rotas
bp = Blueprint('main', __name__)

# Tamanho máximo para arquivos de upload (3MB)
MAX_CONTENT_LENGTH = 3 * 1024 * 1024  # 3MB em bytes

def allowed_file(filename):
    """Verifica se o arquivo tem uma extensão permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['mp3']

def save_audio_file(file):
    """Salva um arquivo de áudio e retorna o caminho relativo."""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Adicionar um prefixo único para evitar conflitos de nome
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Garantir que o diretório de upload existe
        upload_dir = os.path.join('static', 'uploads', 'audio')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Caminho completo para salvar o arquivo
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Salvar o arquivo
        file.save(file_path)
        
        # Retornar o caminho relativo e o tamanho do arquivo
        return file_path, os.path.getsize(file_path)
    
    return None, 0

def admin_required(f):
    """Decorator para requerer permissão de admin."""
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)  # Acesso proibido
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/')
def home():
    # Se o usuário já estiver logado, redireciona para o dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('home.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    # Se o usuário já estiver logado, redireciona para o dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        from werkzeug.security import generate_password_hash
        
        # Verificar se é o primeiro usuário para definir como admin
        is_first_user = User.query.count() == 0
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            is_admin=is_first_user  # O primeiro usuário será admin
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Sua conta foi criada! Você já pode entrar.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Se o usuário já estiver logado, redireciona para o dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Você entrou com sucesso!', 'success')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Falha ao entrar. Verifique seu email e senha.', 'danger')
    
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('main.home'))

@bp.route('/dashboard')
@login_required
def dashboard():
    sort_by = request.args.get('sort', 'updated_at')  # Padrão: ordenar por data de atualização
    
    # Base query
    base_query = current_user.compositions
    
    # Aplicar ordenação
    if sort_by == 'title':
        base_query = base_query.order_by(Composition.title)
    elif sort_by == 'music_name':
        base_query = base_query.order_by(Composition.music_name)
    elif sort_by == 'created_at':
        base_query = base_query.order_by(desc(Composition.created_at))
    else:  # default: updated_at
        base_query = base_query.order_by(desc(Composition.updated_at))
    
    compositions = base_query.all()
    return render_template('dashboard.html', compositions=compositions)

@bp.route('/composition/new', methods=['GET', 'POST'])
@login_required
def new_composition():
    form = CompositionForm()
    if form.validate_on_submit():
        composition = Composition(
            title=form.title.data,
            music_name=form.music_name.data,
            description=form.description.data,
            user_id=current_user.id
        )
        
        # Se um gênero foi selecionado, adicione-o
        if form.genre.data and form.genre.data != '':
            # Salvar o gênero original para compatibilidade
            genre_obj = Genre.query.get(int(form.genre.data))
            if genre_obj:
                composition.genre = genre_obj.name
                composition.genre_id = genre_obj.id
        
        # Verificar se há um arquivo de áudio sendo enviado
        audio_file = form.audio_file.data
        if audio_file:
            if audio_file.content_length > MAX_CONTENT_LENGTH:
                flash('Arquivo de áudio excede o limite de 3MB!', 'danger')
                return render_template('composition_form.html', form=form, title='Nova Composição')
            
            # Salvar o arquivo e obter o caminho relativo
            filepath, file_size = save_audio_file(audio_file)
            if filepath:
                composition.audio_file = filepath
                composition.audio_file_size = file_size
            else:
                flash('Tipo de arquivo não permitido. Use apenas arquivos MP3.', 'danger')
                return render_template('composition_form.html', form=form, title='Nova Composição')
        
        db.session.add(composition)
        db.session.commit()
        flash('Sua composição foi criada!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('composition_form.html', form=form, title='Nova Composição')

@bp.route('/composition/<int:composition_id>')
@login_required
def composition_detail(composition_id):
    composition = Composition.query.get_or_404(composition_id)
    if composition.user_id != current_user.id:
        abort(403)
    return render_template('composition_detail.html', composition=composition)

@bp.route('/audio/<int:composition_id>')
@login_required
def get_audio(composition_id):
    composition = Composition.query.get_or_404(composition_id)
    
    # Verificar se o usuário tem permissão para acessar
    if composition.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    # Verificar se a composição tem um arquivo de áudio
    if not composition.audio_file or not os.path.exists(composition.audio_file):
        abort(404)
    
    # Retornar o arquivo de áudio
    return send_file(composition.audio_file, mimetype='audio/mpeg')

@bp.route('/composition/<int:composition_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_composition(composition_id):
    composition = Composition.query.get_or_404(composition_id)
    if composition.user_id != current_user.id:
        abort(403)
    
    form = CompositionForm()
    if form.validate_on_submit():
        composition.title = form.title.data
        composition.music_name = form.music_name.data
        composition.description = form.description.data
        
        # Se um gênero foi selecionado, atualize-o
        if form.genre.data and form.genre.data != '':
            # Salvar o gênero original para compatibilidade
            genre_obj = Genre.query.get(int(form.genre.data))
            if genre_obj:
                composition.genre = genre_obj.name
                composition.genre_id = genre_obj.id
        else:
            composition.genre = None
            composition.genre_id = None
        
        # Verificar se há um novo arquivo de áudio sendo enviado
        audio_file = form.audio_file.data
        if audio_file:
            if audio_file.content_length > MAX_CONTENT_LENGTH:
                flash('Arquivo de áudio excede o limite de 3MB!', 'danger')
                return render_template('composition_form.html', form=form, title='Editar Composição', composition=composition)
            
            # Remover arquivo antigo se existir
            if composition.audio_file and os.path.exists(composition.audio_file):
                try:
                    os.remove(composition.audio_file)
                except Exception as e:
                    # Apenas log, não impedir a atualização
                    print(f"Erro ao excluir arquivo antigo: {e}")
            
            # Salvar o novo arquivo e obter o caminho relativo
            filepath, file_size = save_audio_file(audio_file)
            if filepath:
                composition.audio_file = filepath
                composition.audio_file_size = file_size
            else:
                flash('Tipo de arquivo não permitido. Use apenas arquivos MP3.', 'danger')
                return render_template('composition_form.html', form=form, title='Editar Composição', composition=composition)
            
        db.session.commit()
        flash('Sua composição foi atualizada!', 'success')
        return redirect(url_for('main.composition_detail', composition_id=composition.id))
    elif request.method == 'GET':
        form.title.data = composition.title
        form.music_name.data = composition.music_name
        form.description.data = composition.description
        
        # Se tem um genre_id, use-o; caso contrário, tente usar o campo genre
        if composition.genre_id:
            form.genre.data = str(composition.genre_id)
        elif composition.genre:
            # Tente encontrar o gênero pelo nome para compatibilidade
            genre_obj = Genre.query.filter_by(name=composition.genre).first()
            if genre_obj:
                form.genre.data = str(genre_obj.id)
    
    return render_template('composition_form.html', form=form, title='Editar Composição', composition=composition)

@bp.route('/composition/<int:composition_id>/delete', methods=['POST'])
@login_required
def delete_composition(composition_id):
    composition = Composition.query.get_or_404(composition_id)
    if composition.user_id != current_user.id:
        abort(403)
    
    # Remover arquivo de áudio se existir
    if composition.audio_file and os.path.exists(composition.audio_file):
        try:
            os.remove(composition.audio_file)
        except Exception as e:
            # Apenas log, não impedir a exclusão da composição
            print(f"Erro ao excluir arquivo de áudio: {e}")
    
    db.session.delete(composition)
    db.session.commit()
    flash('Sua composição foi excluída!', 'success')
    return redirect(url_for('main.dashboard'))

@bp.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q', '')
    sort_by = request.args.get('sort', 'updated_at')  # Padrão: ordenar por data de atualização
    
    if query:
        # Consulta base - filtrar para o usuário atual
        base_query = Composition.query.filter(Composition.user_id == current_user.id)
        
        # Aplicar filtro de busca
        search_filter = (
            Composition.title.ilike(f'%{query}%') | 
            Composition.music_name.ilike(f'%{query}%') | 
            Composition.description.ilike(f'%{query}%')
        )
        
        # Buscar também pelo nome do gênero
        genre_ids = []
        genres = Genre.query.filter(Genre.name.ilike(f'%{query}%')).all()
        if genres:
            genre_ids = [g.id for g in genres]
            search_filter = search_filter | Composition.genre_id.in_(genre_ids)
        
        # Aplicar o filtro de busca
        base_query = base_query.filter(search_filter)
        
        # Aplicar ordenação
        if sort_by == 'title':
            base_query = base_query.order_by(Composition.title)
        elif sort_by == 'music_name':
            base_query = base_query.order_by(Composition.music_name)
        elif sort_by == 'created_at':
            base_query = base_query.order_by(desc(Composition.created_at))
        else:  # default: updated_at
            base_query = base_query.order_by(desc(Composition.updated_at))
        
        compositions = base_query.all()
    else:
        compositions = []
    
    return render_template('dashboard.html', compositions=compositions, search_query=query)

# Rotas de Administração
@bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    # Estatísticas para o dashboard
    total_users = User.query.count()
    total_compositions = Composition.query.count()
    total_genres = Genre.query.count()
    
    return render_template('admin/dashboard.html', 
                          total_users=total_users, 
                          total_compositions=total_compositions,
                          total_genres=total_genres)

# Gerenciamento de Gêneros
@bp.route('/admin/generos')
@login_required
@admin_required
def genre_list():
    genres = Genre.query.order_by(Genre.name).all()
    return render_template('admin/genre_list.html', genres=genres)

@bp.route('/admin/generos/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def new_genre():
    form = GenreForm()
    if form.validate_on_submit():
        genre = Genre(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(genre)
        db.session.commit()
        flash('Gênero adicionado com sucesso!', 'success')
        return redirect(url_for('main.genre_list'))
    
    return render_template('admin/genre_form.html', form=form, title='Novo Gênero')

@bp.route('/admin/generos/<int:genre_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_genre(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    form = GenreForm(obj=genre)
    form._obj = genre  # Para a validação de nome único
    
    if form.validate_on_submit():
        genre.name = form.name.data
        genre.description = form.description.data
        db.session.commit()
        flash('Gênero atualizado com sucesso!', 'success')
        return redirect(url_for('main.genre_list'))
    
    return render_template('admin/genre_form.html', form=form, title='Editar Gênero')

@bp.route('/admin/generos/<int:genre_id>/excluir', methods=['POST'])
@login_required
@admin_required
def delete_genre(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    
    # Verifica se existem composições usando este gênero
    if genre.compositions.count() > 0:
        flash('Não é possível excluir este gênero porque existem composições que o utilizam.', 'danger')
    else:
        db.session.delete(genre)
        db.session.commit()
        flash('Gênero excluído com sucesso!', 'success')
    
    return redirect(url_for('main.genre_list'))

# Gerenciamento de Usuários
@bp.route('/admin/usuarios')
@login_required
@admin_required
def user_list():
    users = User.query.order_by(User.username).all()
    return render_template('admin/user_list.html', users=users)

@bp.route('/admin/usuarios/<int:user_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevenir auto-demoção de administrador
    if user.id == current_user.id and user.is_admin:
        form = UserAdminForm(obj=user)
        form.is_admin.render_kw = {'disabled': 'disabled'}
    else:
        form = UserAdminForm(obj=user)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        
        # Não permitir que o admin atual remova seus próprios privilégios
        if not (user.id == current_user.id and user.is_admin):
            user.is_admin = form.is_admin.data
        
        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('main.user_list'))
    
    return render_template('admin/user_form.html', form=form, user=user, title='Editar Usuário')

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models import User, Composition
from forms import RegistrationForm, LoginForm, CompositionForm
from sqlalchemy import desc

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template('home.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Sua conta foi criada! Agora você pode entrar.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
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
    compositions = current_user.compositions.order_by(desc(Composition.updated_at)).all()
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
            genre=form.genre.data,
            user_id=current_user.id
        )
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
        composition.genre = form.genre.data
        db.session.commit()
        flash('Sua composição foi atualizada!', 'success')
        return redirect(url_for('main.composition_detail', composition_id=composition.id))
    elif request.method == 'GET':
        form.title.data = composition.title
        form.music_name.data = composition.music_name
        form.description.data = composition.description
        form.genre.data = composition.genre
    
    return render_template('composition_form.html', form=form, title='Editar Composição')

@bp.route('/composition/<int:composition_id>/delete', methods=['POST'])
@login_required
def delete_composition(composition_id):
    composition = Composition.query.get_or_404(composition_id)
    if composition.user_id != current_user.id:
        abort(403)
    
    db.session.delete(composition)
    db.session.commit()
    flash('Sua composição foi excluída!', 'success')
    return redirect(url_for('main.dashboard'))

@bp.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q', '')
    if query:
        compositions = Composition.query.filter(
            Composition.user_id == current_user.id,
            (Composition.title.ilike(f'%{query}%') | 
             Composition.music_name.ilike(f'%{query}%') | 
             Composition.description.ilike(f'%{query}%'))
        ).order_by(desc(Composition.updated_at)).all()
    else:
        compositions = []
    
    return render_template('dashboard.html', compositions=compositions, search_query=query)

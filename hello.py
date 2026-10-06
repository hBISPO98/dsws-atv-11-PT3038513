# Importações de bibliotecas e ferramentas necessárias
import os
from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import requests
from datetime import datetime

# Lê o ficheiro .env para carregar variáveis de ambiente de forma segura
from dotenv import load_dotenv
load_dotenv()

# Define o diretório base da aplicação
basedir = os.path.abspath(os.path.dirname(__file__))

# Inicialização da aplicação Flask e configurações básicas
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurações da API do Mailgun resgatadas das variáveis de ambiente
app.config['API_KEY'] = os.environ.get('API_KEY')
app.config['API_URL'] = os.environ.get('API_URL')
app.config['API_FROM'] = os.environ.get('API_FROM')

# Configurações auxiliares de e-mail e administradores
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'b.hiandra@aluno.ifsp.edu.br'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')

# Inicialização das extensões do Flask
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Modelo de Dados para os Cargos (Roles) dos usuários no banco de dados
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

# Modelo de Dados para os Utilizadores/Usuários cadastrados
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

# Modelo de Dados para o Histórico/Log de E-mails Enviados (Atv10)
class EmailLog(db.Model):
    __tablename__ = 'email_logs'
    id = db.Column(db.Integer, primary_key=True)
    sender_user = db.Column(db.String(64))
    recipient = db.Column(db.String(256))
    subject = db.Column(db.String(128))
    body_text = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<EmailLog %r>' % self.subject

# Função responsável por disparar o e-mail utilizando a API HTTP do Mailgun
def send_simple_message(to, subject, html_content, sender_name, body_summary):
    print('Enviando mensagem (POST)...', flush=True)
    
    if isinstance(to, list):
        to_address = ", ".join(to)
    else:
        to_address = to

    try:
        resposta = requests.post(app.config['API_URL'], 
                               auth=("api", app.config['API_KEY']), 
                               data={"from": app.config['API_FROM'], 
                                     "to": to_address, 
                                     "subject": app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject, 
                                     "html": html_content})
            
        print('Enviando mensagem (Resposta)...' + str(resposta) + ' - ' + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), flush=True)
        
        # Salva o registo do e-mail enviado no banco de dados (Atv10)
        if resposta.status_code == 200:
            log = EmailLog(
                sender_user=sender_name,
                recipient=to_address,
                subject=subject,
                body_text=body_summary
            )
            db.session.add(log)
            db.session.commit()

        return resposta
    except Exception as e:
        print('ERRO AO ENVIAR E-MAIL: ' + str(e), flush=True)
        raise e

# Definição do formulário de cadastro utilizando Flask-WTF
class NameForm(FlaskForm):
    name = StringField('Qual é o seu nome?', validators=[DataRequired()])
    role = SelectField('Qual é o seu cargo?', choices=[
        ('Usuário', 'Usuário'), 
        ('Moderador', 'Moderador'), 
        ('Administrador', 'Administrador')
    ])
    email = BooleanField('Deseja enviar e-mail para b.hiandra@aluno.ifsp.edu.br?')
    submit = SubmitField('Enviar')
    
# Contexto de shell para facilitar testes e manipulação via linha de comando
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, EmailLog=EmailLog)

# Tratamento personalizado para a página não encontrada (Erro 404)
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Tratamento personalizado para erro interno do servidor (Erro 500)
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# ROTA PRA EXIBIR O HISTÓRICO DE E-MAILS ENVIADOS (Atv10)
@app.route('/emails-enviados')
def emails_enviados():
    logs = EmailLog.query.order_by(EmailLog.timestamp.desc()).all()
    return render_template('emails_enviados.html', logs=logs)

# Rota principal da aplicação (lida com visualização e submissão do formulário)
@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    
    if form.validate_on_submit():
        old_name = session.get('name')
        nome = form.name.data
        role_selecionada = form.role.data
        
        if old_name is not None and old_name.lower() != nome.strip().lower():
            session['known'] = False
        else:
            session['known'] = True
            
        session['name'] = nome.strip()

        user_role = Role.query.filter_by(name=role_selecionada).first()
        if not user_role:
            user_role = Role(name=role_selecionada)
            db.session.add(user_role)
            db.session.commit()

        nome_tratado = nome.strip()
        usuario_existente = User.query.filter(db.func.lower(User.username) == nome_tratado.lower()).first()
        
        is_new_user = False
        is_role_updated = False

        if not usuario_existente:
            user = User(username=nome_tratado, role=user_role)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            is_new_user = True
        else:
            if usuario_existente.role != user_role:
                usuario_existente.role = user_role
                db.session.commit()
                is_role_updated = True
            session['known'] = True
            user = usuario_existente

        # Disparo de e-mail condicional apenas se a checkbox estiver marcada e houver admin configurado
        if (is_new_user or is_role_updated) and app.config['FLASKY_ADMIN'] and form.email.data:
            destinatarios = [app.config['FLASKY_ADMIN']]
            
            aluno_email = "b.hiandra@aluno.ifsp.edu.br"
            if aluno_email not in destinatarios:
                destinatarios.append(aluno_email)
                
            assunto = 'Novo usuário cadastrado' if is_new_user else 'Atualização de cargo de usuário'
            resumo_texto = f'Novo usuário cadastrado: {user.username}' if is_new_user else f'Atualização de cargo: {user.username}'
            
            html_mensagem = render_template('mail/user.html', user=user, is_new=is_new_user)
            
            send_simple_message(destinatarios, assunto, html_mensagem, user.username, resumo_texto)
            
            # Ativa a flag para exibir a mensagem fixa no template
            session['email_enviado'] = True
        else:
            session['email_enviado'] = False
            
        return redirect(url_for('index'))
        
    user_all = User.query.all()
    roles = Role.query.all()

    return render_template('index.html', 
                           form=form, 
                           name=session.get('name'),
                           known=session.get('known', False), 
                           email_enviado=session.get('email_enviado', False),
                           usuarios=user_all,
                           user_count=len(user_all),
                           roles=roles,
                           role_count=len(roles),
                           moment_time=datetime.utcnow())
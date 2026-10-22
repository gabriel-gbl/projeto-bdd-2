import os
import secrets
import sqlite3
from functools import wraps
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from banco import criar_tabelas
from modelos.usuario import Usuario
from modelos.cantor import Cantor
from modelos.perfil_cantor import PerfilCantor
from modelos.album import Album
from modelos.genero import Genero
from modelos.musica import Musica

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax')
criar_tabelas()
ENTIDADES = {'cantores': Cantor, 'perfis': PerfilCantor, 'albuns': Album,
            'generos': Genero, 'musicas': Musica}

ROTULOS = {'cantores': 'Cantores', 'perfis': 'Perfis dos cantores',
           'albuns': 'Álbuns', 'generos': 'Gêneros', 'musicas': 'Músicas'}
           
CAMPOS = {'nome': 'Nome', 'dataNascimento': 'Data de nascimento', 'nacionalidade': 'Nacionalidade',
          'idCantor': 'Cantor (ID)', 'biografia': 'Biografia', 'instagram': 'Instagram',
          'foto': 'Foto (URL)', 'anoLancamento': 'Ano de lançamento', 'gravadora': 'Gravadora',
          'descricao': 'Descrição', 'titulo': 'Título', 'duracao': 'Duração (HH:MM:SS)',
          'dataLancamento': 'Data de lançamento', 'idAlbum': 'Álbum (ID)', 'idGenero': 'Gênero (ID)'}


def usuario_atual():
    identificador = session.get('usuario_id')
    return Usuario.buscar(identificador) if identificador is not None else None

@app.context_processor
def contexto():
    return {'usuario': usuario_atual(), 'rotulos': ROTULOS, 'campos_rotulos': CAMPOS}

@app.before_request
def proteger_post():
    if request.method == 'POST':
        token = session.get('csrf_token')
        if not token or not secrets.compare_digest(token, request.form.get('csrf_token', '')):
            abort(400, 'Token de formulário inválido. Atualize a página e tente novamente.')

@app.context_processor
def csrf_contexto():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)
    return {'csrf_token': session['csrf_token']}


def login_obrigatorio(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not usuario_atual():
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper


def admin_obrigatorio(func):
    @wraps(func)
    @login_obrigatorio
    def wrapper(*args, **kwargs):
        if usuario_atual().papel != 'admin':
            abort(403)
        return func(*args, **kwargs)
    return wrapper


def entidade(nome):
    if nome not in ENTIDADES:
        abort(404)
    return ENTIDADES[nome]


@app.get('/')
def inicio():
    return render_template('inicio.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        if not nome or '@' not in email or len(senha) < 8:
            flash('Informe nome, e-mail válido e senha de pelo menos 8 caracteres.', 'erro')
        else:
            try:
                Usuario.cadastrar(nome, email, senha)
                flash('Cadastro concluído. Entre com sua conta.', 'ok')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Este e-mail já está cadastrado.', 'erro')
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = Usuario.buscar_email(request.form.get('email', ''))
        if usuario and usuario.verificar_senha(request.form.get('senha', '')):
            session.clear()
            session['usuario_id'] = usuario.idUsuario
            session['csrf_token'] = secrets.token_urlsafe(32)
            return redirect(url_for('inicio'))
        flash('E-mail ou senha inválidos.', 'erro')
    return render_template('login.html')

@app.post('/sair')
def sair():
    session.clear()
    return redirect(url_for('login'))

def numero(valor):
    """Converte o texto de um filtro em inteiro; vazio ou inválido vira None (sem filtro)."""
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


# As rotas fixas /musicas e /cantores têm prioridade sobre a rota genérica /<nome>.
# Elas usam as seleções complexas (JOIN + filtros) em vez do SELECT * simples.
@app.get('/musicas')
@login_obrigatorio
def listar_musicas():
    filtros = {
        'titulo': request.args.get('titulo', '').strip(),
        'idGenero': numero(request.args.get('idGenero')),
        'idAlbum': numero(request.args.get('idAlbum')),
        'idCantor': numero(request.args.get('idCantor')),
        'ano_inicio': numero(request.args.get('ano_inicio')),
        'ano_fim': numero(request.args.get('ano_fim')),
    }
    return render_template('musicas.html', nome='musicas', filtros=filtros,
                           musicas=Musica.pesquisar(**filtros),
                           generos=Genero.listar(), albuns=Album.listar(), cantores=Cantor.listar())

@app.get('/cantores')
@login_obrigatorio
def listar_cantores():
    filtros = {
        'nome': request.args.get('nome', '').strip(),
        'nacionalidade': request.args.get('nacionalidade', '').strip(),
        'idGenero': numero(request.args.get('idGenero')),
        'minimo_musicas': numero(request.args.get('minimo_musicas')),
        'somente_com_perfil': request.args.get('somente_com_perfil') == '1',
    }
    return render_template('cantores.html', nome='cantores', filtros=filtros,
                           cantores=Cantor.pesquisar(**filtros), generos=Genero.listar())

@app.get('/<nome>')
@login_obrigatorio
def listar(nome):
    classe = entidade(nome)
    return render_template('lista.html', nome=nome, classe=classe, objetos=classe.listar())

@app.get('/<nome>/<int:identificador>')
@login_obrigatorio
def detalhes(nome, identificador):
    classe = entidade(nome)
    objeto = classe.buscar(identificador)
    if not objeto:
        abort(404)
    extras = {}
    if nome == 'cantores':
        extras = {'Perfil': objeto.perfil(), 'Músicas': objeto.musicas()}
    if nome == 'musicas':
        extras = {'Álbum': objeto.album(), 'Gênero': objeto.genero(), 'Cantores': objeto.cantores()}
    return render_template('detalhes.html', nome=nome, objeto=objeto, extras=extras)


def validar_dados(classe):
    dados = {campo: request.form.get(campo, '').strip() for campo in classe.campos}
    obrigatorios = {'cantor': ['nome', 'dataNascimento', 'nacionalidade'],
                    'perfil_cantor': ['idCantor', 'biografia'],
                    'album': ['nome', 'anoLancamento'], 'genero': ['nome'],
                    'musica': ['titulo', 'duracao', 'dataLancamento', 'idAlbum', 'idGenero']}
    if any(not dados[c] for c in obrigatorios[classe.tabela]):
        raise ValueError('Preencha todos os campos obrigatórios.')
    for campo in ('idCantor', 'idAlbum', 'idGenero', 'anoLancamento'):
        if campo in dados and dados[campo]:
            dados[campo] = int(dados[campo])
    return {chave: (valor if valor != '' else None) for chave, valor in dados.items()}

@app.route('/<nome>/novo', methods=['GET', 'POST'])
@admin_obrigatorio
def novo(nome):
    classe = entidade(nome)
    if request.method == 'POST':
        try:
            classe.cadastrar(**validar_dados(classe))
            flash('Registro cadastrado.', 'ok')
            return redirect(url_for('listar', nome=nome))
        except (sqlite3.IntegrityError, ValueError) as erro:
            flash('Não foi possível cadastrar: ' + str(erro), 'erro')
    return render_template('formulario.html', nome=nome, classe=classe, objeto=None)

@app.route('/<nome>/<int:identificador>/editar', methods=['GET', 'POST'])
@admin_obrigatorio
def editar(nome, identificador):
    classe = entidade(nome)
    objeto = classe.buscar(identificador)
    if not objeto:
        abort(404)
    if request.method == 'POST':
        try:
            dados = validar_dados(classe)
            for campo, valor in dados.items():
                setattr(objeto, campo, valor)
            objeto.atualizar()
            flash('Registro atualizado.', 'ok')
            return redirect(url_for('listar', nome=nome))
        except (sqlite3.IntegrityError, ValueError) as erro:
            flash('Não foi possível atualizar: ' + str(erro), 'erro')
    return render_template('formulario.html', nome=nome, classe=classe, objeto=objeto)

@app.post('/<nome>/<int:identificador>/excluir')
@admin_obrigatorio
def excluir(nome, identificador):
    classe = entidade(nome)
    objeto = classe.buscar(identificador)
    if not objeto:
        abort(404)
    try:
        objeto.excluir()
        flash('Registro excluído.', 'ok')
    except sqlite3.IntegrityError:
        flash('Não é possível excluir: existem registros relacionados.', 'erro')
    return redirect(url_for('listar', nome=nome))

@app.post('/musicas/<int:identificador>/cantores')
@admin_obrigatorio
def vincular_cantor(identificador):
    musica = Musica.buscar(identificador)
    if not musica:
        abort(404)
    try:
        cantor_id = int(request.form.get('idCantor', ''))
        if not Cantor.buscar(cantor_id):
            raise ValueError('Cantor não encontrado.')
        if request.form.get('acao') == 'adicionar':
            musica.associar_cantor(cantor_id)
        elif request.form.get('acao') == 'remover':
            musica.remover_cantor(cantor_id)
        else:
            abort(400)
        flash('Relação atualizada.', 'ok')
    except ValueError as erro:
        flash(str(erro), 'erro')
    return redirect(url_for('detalhes', nome='musicas', identificador=identificador))

if __name__ == '__main__':
    app.run(debug=False)

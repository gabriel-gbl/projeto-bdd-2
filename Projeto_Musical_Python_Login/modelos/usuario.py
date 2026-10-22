from banco import conectar
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario:
    def __init__(self, dados):
        self.idUsuario = dados['idUsuario']
        self.nome = dados['nome']
        self.email = dados['email']
        self.papel = dados['papel']
        self._senha_hash = dados['senha_hash']

    @classmethod
    def buscar(cls, identificador):
        with conectar() as db:
            linha = db.execute('SELECT * FROM usuario WHERE idUsuario = ?', (identificador,)).fetchone()
        return cls(dict(linha)) if linha else None

    @classmethod
    def buscar_email(cls, email):
        with conectar() as db:
            linha = db.execute('SELECT * FROM usuario WHERE email = ?', (email.strip().lower(),)).fetchone()
        return cls(dict(linha)) if linha else None

    @classmethod
    def cadastrar(cls, nome, email, senha):
        # Cadastro público sempre gera usuário comum.
        with conectar() as db:
            cursor = db.execute('INSERT INTO usuario (nome, email, senha_hash, papel) VALUES (?, ?, ?, ?)',
                                (nome.strip(), email.strip().lower(), generate_password_hash(senha), 'usuario'))
            identificador = cursor.lastrowid
        return cls.buscar(identificador)

    @classmethod
    def criar_admin(cls, nome, email, senha):
        # Chamado apenas pelo script local configurar_admin.py, nunca por rota web.
        with conectar() as db:
            cursor = db.execute('INSERT INTO usuario (nome, email, senha_hash, papel) VALUES (?, ?, ?, ?)',
                                (nome.strip(), email.strip().lower(), generate_password_hash(senha), 'admin'))
            identificador = cursor.lastrowid
        return cls.buscar(identificador)

    def verificar_senha(self, senha):
        return check_password_hash(self._senha_hash, senha)

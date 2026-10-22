from getpass import getpass
from sqlite3 import IntegrityError
from banco import criar_tabelas
from modelos.usuario import Usuario

criar_tabelas()
print('Criação local do administrador (não disponível no site).')
nome = input('Nome: ').strip()
email = input('E-mail: ').strip()
senha = getpass('Senha (mínimo 8 caracteres): ')
if not nome or '@' not in email or len(senha) < 8:
    print('Nome, e-mail ou senha inválidos.')
else:
    try:
        Usuario.criar_admin(nome, email, senha)
        print('Administrador criado com sucesso.')
    except IntegrityError:
        print('E-mail já cadastrado.')

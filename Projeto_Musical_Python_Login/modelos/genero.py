from modelos.base import ModeloBase


class Genero(ModeloBase):
    tabela = "genero"
    chave = "idGenero"
    campos = ('nome', 'descricao')

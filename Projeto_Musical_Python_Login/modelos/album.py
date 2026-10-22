from modelos.base import ModeloBase


class Album(ModeloBase):
    tabela = "album"
    chave = "idAlbum"
    campos = ('nome', 'anoLancamento', 'gravadora')

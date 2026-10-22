from modelos.base import ModeloBase


class PerfilCantor(ModeloBase):
    tabela = "perfil_cantor"
    chave = "idPerfil"
    campos = ('idCantor', 'biografia', 'instagram', 'foto')

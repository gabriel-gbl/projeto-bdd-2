from banco import conectar
from modelos.base import ModeloBase


class Musica(ModeloBase):
    tabela = "musica"
    chave = "idMusica"
    campos = ('titulo', 'duracao', 'dataLancamento', 'idAlbum', 'idGenero')

    def album(self):
        from modelos.album import Album
        return Album.buscar(self.idAlbum)

    def genero(self):
        from modelos.genero import Genero
        return Genero.buscar(self.idGenero)

    def cantores(self):
        from modelos.cantor import Cantor
        from banco import conectar
        with conectar() as banco:
            linhas = banco.execute("""
                SELECT cantor.* FROM cantor
                JOIN cantor_musica ON cantor.idCantor = cantor_musica.idCantor
                WHERE cantor_musica.idMusica = ?
            """, (self.idMusica,)).fetchall()
        return [Cantor(dict(linha)) for linha in linhas]

    def associar_cantor(self, id_cantor):
        from banco import conectar
        with conectar() as banco:
            banco.execute("INSERT OR IGNORE INTO cantor_musica (idCantor, idMusica) VALUES (?, ?)", (id_cantor, self.idMusica))

    def remover_cantor(self, id_cantor):
        from banco import conectar
        with conectar() as banco:
            banco.execute("DELETE FROM cantor_musica WHERE idCantor = ? AND idMusica = ?", (id_cantor, self.idMusica))

    @classmethod
    def pesquisar(cls, titulo=None, idGenero=None, idAlbum=None, idCantor=None,
                  ano_inicio=None, ano_fim=None):
        """Seleção complexa: junta musica, album, genero, cantor_musica e cantor.

        Só entram no WHERE os filtros que foram informados. Cada música volta
        uma única vez (GROUP BY), com os nomes do álbum, do gênero e de todos
        os cantores, em vez dos IDs.
        """
        condicoes = []
        parametros = []
        if titulo:
            condicoes.append("m.titulo LIKE ?")
            parametros.append(f"%{titulo}%")
        if idGenero:
            condicoes.append("m.idGenero = ?")
            parametros.append(idGenero)
        if idAlbum:
            condicoes.append("m.idAlbum = ?")
            parametros.append(idAlbum)
        if idCantor:
            # Subconsulta em vez de "c.idCantor = ?": assim a música continua
            # listando todos os seus cantores, e não só o que foi filtrado.
            condicoes.append("m.idMusica IN (SELECT idMusica FROM cantor_musica WHERE idCantor = ?)")
            parametros.append(idCantor)
        if ano_inicio:
            condicoes.append("CAST(strftime('%Y', m.dataLancamento) AS INTEGER) >= ?")
            parametros.append(ano_inicio)
        if ano_fim:
            condicoes.append("CAST(strftime('%Y', m.dataLancamento) AS INTEGER) <= ?")
            parametros.append(ano_fim)

        where = ("WHERE " + " AND ".join(condicoes)) if condicoes else ""
        sql = f"""
            SELECT m.*,
                   a.nome AS album_nome,
                   g.nome AS genero_nome,
                   GROUP_CONCAT(c.nome, ', ') AS cantores_nomes
            FROM musica m
            JOIN album a ON a.idAlbum = m.idAlbum
            JOIN genero g ON g.idGenero = m.idGenero
            LEFT JOIN cantor_musica cm ON cm.idMusica = m.idMusica
            LEFT JOIN cantor c ON c.idCantor = cm.idCantor
            {where}
            GROUP BY m.idMusica
            ORDER BY m.titulo
        """
        with conectar() as banco:
            linhas = banco.execute(sql, parametros).fetchall()

        musicas = []
        for linha in linhas:
            dados = dict(linha)
            musica = cls(dados)
            # Atributos derivados: calculados pela consulta, não existem na tabela musica.
            musica.album_nome = dados["album_nome"]
            musica.genero_nome = dados["genero_nome"]
            musica.cantores_nomes = dados["cantores_nomes"] or ""
            musicas.append(musica)
        return musicas

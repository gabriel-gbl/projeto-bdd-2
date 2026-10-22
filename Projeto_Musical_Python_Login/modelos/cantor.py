from banco import conectar
from modelos.base import ModeloBase


class Cantor(ModeloBase):
    tabela = "cantor"
    chave = "idCantor"
    campos = ('nome', 'dataNascimento', 'nacionalidade')

    def musicas(self):
        from modelos.musica import Musica
        with __import__("banco").conectar() as banco:
            linhas = banco.execute("""
                SELECT musica.* FROM musica
                JOIN cantor_musica ON musica.idMusica = cantor_musica.idMusica
                WHERE cantor_musica.idCantor = ?
            """, (self.idCantor,)).fetchall()
        return [Musica(dict(linha)) for linha in linhas]

    def perfil(self):
        from modelos.perfil_cantor import PerfilCantor
        with __import__("banco").conectar() as banco:
            linha = banco.execute("SELECT * FROM perfil_cantor WHERE idCantor = ?", (self.idCantor,)).fetchone()
        return PerfilCantor(dict(linha)) if linha else None

    @classmethod
    def pesquisar(cls, nome=None, nacionalidade=None, idGenero=None,
                  minimo_musicas=None, somente_com_perfil=False):
        """Seleção complexa: junta cantor, perfil_cantor (1:1), cantor_musica e
        musica (N:N) e genero (1:N), contando as músicas de cada cantor.

        LEFT JOIN mantém no resultado os cantores sem perfil e sem músicas.
        Filtros sobre linhas vão no WHERE; o filtro sobre a contagem vai no HAVING.
        """
        condicoes = []
        parametros = []
        if nome:
            condicoes.append("c.nome LIKE ?")
            parametros.append(f"%{nome}%")
        if nacionalidade:
            condicoes.append("c.nacionalidade LIKE ?")
            parametros.append(f"%{nacionalidade}%")
        if idGenero:
            # Subconsulta: o cantor entra se tiver alguma música do gênero, mas a
            # contagem e a lista de gêneros continuam considerando todas as músicas.
            condicoes.append("""c.idCantor IN (
                SELECT cm2.idCantor FROM cantor_musica cm2
                JOIN musica m2 ON m2.idMusica = cm2.idMusica
                WHERE m2.idGenero = ?)""")
            parametros.append(idGenero)
        if somente_com_perfil:
            condicoes.append("p.idPerfil IS NOT NULL")

        where = ("WHERE " + " AND ".join(condicoes)) if condicoes else ""
        having = ""
        if minimo_musicas:
            having = "HAVING COUNT(DISTINCT m.idMusica) >= ?"
            parametros.append(minimo_musicas)

        sql = f"""
            SELECT c.*,
                   CASE WHEN p.idPerfil IS NOT NULL THEN 1 ELSE 0 END AS tem_perfil,
                   COUNT(DISTINCT m.idMusica) AS total_musicas,
                   GROUP_CONCAT(DISTINCT g.nome) AS generos_nomes
            FROM cantor c
            LEFT JOIN perfil_cantor p ON p.idCantor = c.idCantor
            LEFT JOIN cantor_musica cm ON cm.idCantor = c.idCantor
            LEFT JOIN musica m ON m.idMusica = cm.idMusica
            LEFT JOIN genero g ON g.idGenero = m.idGenero
            {where}
            GROUP BY c.idCantor
            {having}
            ORDER BY c.nome
        """
        with conectar() as banco:
            linhas = banco.execute(sql, parametros).fetchall()

        cantores = []
        for linha in linhas:
            dados = dict(linha)
            cantor = cls(dados)
            # Atributos derivados: calculados pela consulta, não existem na tabela cantor.
            cantor.tem_perfil = bool(dados["tem_perfil"])
            cantor.total_musicas = dados["total_musicas"]
            cantor.generos_nomes = (dados["generos_nomes"] or "").replace(",", ", ")
            cantores.append(cantor)
        return cantores

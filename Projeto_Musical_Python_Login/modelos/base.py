from banco import conectar


class ModeloBase:
    tabela = ""
    chave = ""
    campos = ()

    def __init__(self, dados):
        for campo in (self.chave, *self.campos):
            setattr(self, campo, dados.get(campo))

    @classmethod
    def listar(cls):
        with conectar() as banco:
            linhas = banco.execute(f"SELECT * FROM {cls.tabela} ORDER BY {cls.chave}").fetchall()
        return [cls(dict(linha)) for linha in linhas]

    @classmethod
    def buscar(cls, identificador):
        with conectar() as banco:
            linha = banco.execute(
                f"SELECT * FROM {cls.tabela} WHERE {cls.chave} = ?", (identificador,)
            ).fetchone()
        return cls(dict(linha)) if linha else None

    @classmethod
    def cadastrar(cls, **dados):
        colunas = ", ".join(cls.campos)
        marcadores = ", ".join("?" for _ in cls.campos)
        valores = tuple(dados.get(campo) for campo in cls.campos)
        with conectar() as banco:
            cursor = banco.execute(
                f"INSERT INTO {cls.tabela} ({colunas}) VALUES ({marcadores})", valores
            )
            identificador = cursor.lastrowid
        return cls.buscar(identificador)

    def atualizar(self):
        atribuicoes = ", ".join(f"{campo} = ?" for campo in self.campos)
        valores = tuple(getattr(self, campo) for campo in self.campos)
        with conectar() as banco:
            banco.execute(
                f"UPDATE {self.tabela} SET {atribuicoes} WHERE {self.chave} = ?",
                (*valores, getattr(self, self.chave)),
            )

    def excluir(self):
        with conectar() as banco:
            banco.execute(
                f"DELETE FROM {self.tabela} WHERE {self.chave} = ?",
                (getattr(self, self.chave),),
            )

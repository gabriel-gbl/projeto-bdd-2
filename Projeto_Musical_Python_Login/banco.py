import sqlite3
from pathlib import Path

ARQUIVO_BANCO = Path(__file__).with_name("musical.db")


def conectar():
    conexao = sqlite3.connect(ARQUIVO_BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao

def criar_tabelas():
    with conectar() as conexao:
        sql = Path(__file__).with_name("banco.sql").read_text(encoding="utf-8")
        conexao.executescript(sql)

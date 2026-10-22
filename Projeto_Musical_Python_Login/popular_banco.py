"""Preenche o banco com um catálogo de exemplo para a apresentação.

Uso (Windows): py popular_banco.py      Linux/macOS: python3 popular_banco.py

Não apaga nada. Se o catálogo já tiver registros, o script não altera o banco.
Os usuários (login) não são tocados.

Os dados foram escolhidos para exercitar todos os relacionamentos e filtros:
- 1:1  -> alguns cantores têm perfil, outros não (Rita Lee tem perfil e nenhuma música);
- 1:N  -> cada música pertence a um álbum e a um gênero ("Samba" fica sem músicas);
- N:N  -> "Águas de Março" tem 2 cantores e as faixas dos Tribalistas têm 3.

Durações de "Águas de Março", "Velha Infância" e "Já Sei Namorar" são aproximadas,
assim como o dia de lançamento de "Elis & Tom" (agosto de 1974).
"""
from banco import criar_tabelas
from modelos.album import Album
from modelos.cantor import Cantor
from modelos.genero import Genero
from modelos.musica import Musica
from modelos.perfil_cantor import PerfilCantor

criar_tabelas()

if Genero.listar() or Album.listar() or Cantor.listar() or Musica.listar():
    print("O catálogo já tem registros; nada foi alterado.")
    raise SystemExit

generos = {
    "Rock": Genero.cadastrar(nome="Rock", descricao="Guitarra elétrica, baixo e bateria em destaque."),
    "Bossa Nova": Genero.cadastrar(nome="Bossa Nova", descricao="Samba com harmonia influenciada pelo jazz, surgido no Rio de Janeiro no fim dos anos 1950."),
    "MPB": Genero.cadastrar(nome="MPB", descricao="Música Popular Brasileira."),
    "Samba": Genero.cadastrar(nome="Samba", descricao="Gênero brasileiro de raiz afro-brasileira."),
}

albuns = {
    "Opera": Album.cadastrar(nome="A Night at the Opera", anoLancamento=1975, gravadora="EMI"),
    "Elis & Tom": Album.cadastrar(nome="Elis & Tom", anoLancamento=1974, gravadora="Polygram"),
    "Tribalistas": Album.cadastrar(nome="Tribalistas", anoLancamento=2002, gravadora="Phonomotor"),
    "Krig-ha": Album.cadastrar(nome="Krig-ha, Bandolo!", anoLancamento=1973, gravadora="Philips"),
}

cantores = {
    "Freddie": Cantor.cadastrar(nome="Freddie Mercury", dataNascimento="1946-09-05", nacionalidade="Britânica"),
    "Brian": Cantor.cadastrar(nome="Brian May", dataNascimento="1947-07-19", nacionalidade="Britânica"),
    "Elis": Cantor.cadastrar(nome="Elis Regina", dataNascimento="1945-03-17", nacionalidade="Brasileira"),
    "Tom": Cantor.cadastrar(nome="Tom Jobim", dataNascimento="1927-01-25", nacionalidade="Brasileira"),
    "Marisa": Cantor.cadastrar(nome="Marisa Monte", dataNascimento="1967-07-01", nacionalidade="Brasileira"),
    "Arnaldo": Cantor.cadastrar(nome="Arnaldo Antunes", dataNascimento="1960-09-02", nacionalidade="Brasileira"),
    "Carlinhos": Cantor.cadastrar(nome="Carlinhos Brown", dataNascimento="1962-11-23", nacionalidade="Brasileira"),
    "Raul": Cantor.cadastrar(nome="Raul Seixas", dataNascimento="1945-06-28", nacionalidade="Brasileira"),
    "Rita": Cantor.cadastrar(nome="Rita Lee", dataNascimento="1947-12-31", nacionalidade="Brasileira"),
}

perfis = [
    ("Freddie", "Vocalista e compositor da banda britânica Queen."),
    ("Elis", "Cantora gaúcha, considerada uma das maiores intérpretes da música brasileira."),
    ("Tom", "Compositor, pianista e maestro, um dos criadores da bossa nova."),
    ("Marisa", "Cantora e compositora carioca, integrante do trio Tribalistas."),
    ("Rita", "Cantora e compositora paulistana, ex-integrante d'Os Mutantes."),
]
for chave, biografia in perfis:
    PerfilCantor.cadastrar(idCantor=cantores[chave].idCantor, biografia=biografia)

# (título, duração, lançamento, álbum, gênero, cantores)
musicas = [
    ("Bohemian Rhapsody", "00:05:55", "1975-10-31", "Opera", "Rock", ["Freddie"]),
    ("Love of My Life", "00:03:38", "1975-11-28", "Opera", "Rock", ["Freddie"]),
    ("'39", "00:03:30", "1975-11-28", "Opera", "Rock", ["Brian"]),
    ("Águas de Março", "00:03:32", "1974-08-01", "Elis & Tom", "Bossa Nova", ["Elis", "Tom"]),
    ("Por Toda a Minha Vida", "00:02:04", "1974-08-01", "Elis & Tom", "Bossa Nova", ["Elis"]),
    ("Velha Infância", "00:04:09", "2002-11-04", "Tribalistas", "MPB", ["Marisa", "Arnaldo", "Carlinhos"]),
    ("Já Sei Namorar", "00:02:56", "2002-11-04", "Tribalistas", "MPB", ["Marisa", "Arnaldo", "Carlinhos"]),
    ("Mosca na Sopa", "00:03:58", "1973-07-21", "Krig-ha", "Rock", ["Raul"]),
    ("Al Capone", "00:02:38", "1973-07-21", "Krig-ha", "Rock", ["Raul"]),
]
for titulo, duracao, data, album, genero, interpretes in musicas:
    musica = Musica.cadastrar(titulo=titulo, duracao=duracao, dataLancamento=data,
                              idAlbum=albuns[album].idAlbum, idGenero=generos[genero].idGenero)
    for chave in interpretes:
        musica.associar_cantor(cantores[chave].idCantor)

print(f"Catálogo criado: {len(generos)} gêneros, {len(albuns)} álbuns, {len(cantores)} cantores, "
      f"{len(perfis)} perfis e {len(musicas)} músicas.")

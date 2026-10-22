CREATE TABLE IF NOT EXISTS cantor (
    idCantor INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    dataNascimento TEXT NOT NULL,
    nacionalidade TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS perfil_cantor (
    idPerfil INTEGER PRIMARY KEY AUTOINCREMENT,
    idCantor INTEGER NOT NULL UNIQUE,
    biografia TEXT NOT NULL,
    instagram TEXT,
    foto TEXT,
    FOREIGN KEY (idCantor) REFERENCES cantor(idCantor) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS album (
    idAlbum INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    anoLancamento INTEGER NOT NULL,
    gravadora TEXT
);
CREATE TABLE IF NOT EXISTS genero (
    idGenero INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT
);
CREATE TABLE IF NOT EXISTS musica (
    idMusica INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    duracao TEXT NOT NULL,
    dataLancamento TEXT NOT NULL,
    idAlbum INTEGER NOT NULL,
    idGenero INTEGER NOT NULL,
    FOREIGN KEY (idAlbum) REFERENCES album(idAlbum) ON DELETE RESTRICT,
    FOREIGN KEY (idGenero) REFERENCES genero(idGenero) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS cantor_musica (
    idCantor INTEGER NOT NULL,
    idMusica INTEGER NOT NULL,
    PRIMARY KEY (idCantor, idMusica),
    FOREIGN KEY (idCantor) REFERENCES cantor(idCantor) ON DELETE CASCADE,
    FOREIGN KEY (idMusica) REFERENCES musica(idMusica) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS usuario (
    idUsuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    senha_hash TEXT NOT NULL,
    papel TEXT NOT NULL DEFAULT 'usuario' CHECK (papel IN ('admin', 'usuario'))
);

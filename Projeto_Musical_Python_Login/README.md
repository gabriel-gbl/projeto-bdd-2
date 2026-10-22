# Sistema Musical — Python POO, Flask e SQLite

Projeto web com cadastro/login e duas permissões: **admin** (CRUD) e **usuario** (consulta).

## Executar no Windows

1. Abra o terminal na pasta do projeto.
2. Instale as dependências: `py -m pip install -r requirements.txt`
3. Crie o primeiro administrador: `py configurar_admin.py`
4. (Opcional) Preencha o catálogo com dados de exemplo: `py popular_banco.py`
5. Inicie o site: `py app.py`
6. Abra `http://127.0.0.1:5000` no navegador.

No Linux/macOS, use `python3` no lugar de `py`.

**Cadastro público:** clique em “Cadastrar conta”. Toda conta criada pelo site recebe papel `usuario` e pode apenas consultar. O administrador é criado localmente pelo script `configurar_admin.py`. Não existe senha padrão.

**Segurança:** senhas armazenadas com hash; sessões; CSRF nos formulários; verificações de autorização nas rotas, não só nos botões; consultas parametrizadas. Para publicar na internet é necessário configurar HTTPS, `SECRET_KEY` fixa e secreta no ambiente, proteção contra tentativas repetidas de login e infraestrutura de produção. A versão entregue é para demonstração local.

## Banco e classes

O SQLite cria `musical.db` na primeira execução. `banco.sql` define as tabelas cantor, perfil_cantor, album, genero, musica, cantor_musica e usuario. As classes estão em `modelos/`. `ModeloBase` implementa CRUD reutilizável. `Usuario` implementa autenticação; não utiliza o CRUD público.

## Relações

Cantor 1:1 PerfilCantor; Cantor N:N Música por `cantor_musica`; Álbum 1:N Música; Gênero 1:N Música. Um perfil exige cantor existente; uma música exige álbum e gênero existentes. Cantor com perfil tem exclusão em cascata do perfil; álbum e gênero com músicas não podem ser excluídos.

## Consultas com junção e filtros

As telas `/musicas` e `/cantores` usam seleções complexas em vez do `SELECT *` simples:

- `Musica.pesquisar()` junta `musica`, `album`, `genero`, `cantor_musica` e `cantor` (JOIN e LEFT JOIN) e mostra os nomes do álbum, do gênero e de todos os cantores no lugar dos IDs. Filtros: título (LIKE), gênero, álbum, cantor (subconsulta) e intervalo de ano de lançamento.
- `Cantor.pesquisar()` junta `cantor`, `perfil_cantor` (1:1), `cantor_musica`/`musica` (N:N) e `genero` (1:N), conta as músicas de cada cantor (COUNT + GROUP BY) e lista os gêneros que ele canta. Filtros: nome, nacionalidade, gênero, "somente com perfil" (WHERE) e mínimo de músicas (HAVING).

Os filtros entram no WHERE só quando são preenchidos, sempre como parâmetros `?`.

## Dados de exemplo

`popular_banco.py` cadastra 4 gêneros, 4 álbuns, 9 cantores, 5 perfis e 9 músicas usando as próprias classes do modelo. Os dados cobrem os três tipos de relacionamento: cantores com e sem perfil, uma música com dois cantores, músicas com três cantores, um gênero sem músicas e uma cantora sem músicas. O script não roda se o catálogo já tiver registros e não mexe nos usuários.

## Telas

`/login`, `/cadastro`, `/cantores`, `/perfis`, `/albuns`, `/generos`, `/musicas`. Somente admin acessa rotas `/novo`, `/editar`, `/excluir` e associação de cantor/música. Usuários não autenticados são redirecionados ao login para acessar o catálogo.

## Apresentação

Veja `documentacao/Relatorio_Explicacao_3_Integrantes.docx` e os diagramas `.mmd`.

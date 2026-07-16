# obsidian-mcp

Servidor MCP que expõe um vault do Obsidian (busca, leitura, criação e atualização de notas) via Streamable HTTP.

Ver a SPEC completa na nota do vault: `01-Projetos/Servidor MCP do Obsidian.md`.

## Status

`config.py`, `auth.py`, `sync.py`, `server.py`, `vault.py` e `tools.py` estão implementados
e funcionais.

## Tools disponíveis

O servidor expõe 5 tools MCP (`src/tools.py`, registradas em `src/server.py`):

- `search_notes(query, tag=None, limit=10)` — busca por conteúdo, título e tags.
- `read_note(path)` — lê uma nota e devolve conteúdo + frontmatter.
- `list_notes(folder=None, tag=None)` — lista notas, opcionalmente filtradas.
- `write_note(path, content, frontmatter=None)` — cria uma nota nova; não sobrescreve
  a menos que `ALLOW_DESTRUCTIVE=true` (erro `note_exists` / 409 caso contrário).
- `replace_section(path, heading, new_content, mode="replace", occurrence=None)` —
  substitui ou anexa (`mode="append"`) o conteúdo de uma seção sem tocar no resto da nota.
  Se o `heading` se repetir na nota, a chamada recusa com `code: "ambiguous_heading"` e
  informa quantas ocorrências existem — use `occurrence` (1-based, na ordem do documento)
  para escolher qual editar. Substituir um heading pai (ex: `## Fase 1`) troca a seção
  inteira, incluindo qualquer subseção aninhada.

Todas retornam `{"error": ..., "code": ...}` em vez de lançar exceção — ver `tools.py` para
o mapeamento completo de códigos de erro (`unsafe_path_error`, `note_not_found`,
`note_exists`, `heading_not_found`, `ambiguous_heading`, `sync_conflict`,
`invalid_content`, `internal_error`).

Write tools (`write_note`, `replace_section`) fazem `sync_pull()` antes de editar e
`sync_write()` (commit + push) depois, mantendo o repo git do vault sincronizado.

## Setup local

```bash
uv sync
cp .env.example .env
# editar .env: VAULT_PATH deve apontar para a subpasta do vault dentro do clone
# (ex: .../SecondBrain/SecondBrain), MCP_AUTH_TOKEN para um token forte,
# e ALLOWED_HOST para o host que vai servir o Streamable HTTP.
uv run uvicorn src.server:app --reload
```

Rodar os testes:

```bash
uv run pytest
```

Testar com o MCP Inspector antes de expor remotamente:

```bash
npx @modelcontextprotocol/inspector uv run python -m src.server
```

## Variáveis de ambiente

Definidas em `src/config.py` (`Settings`), carregadas de `.env`. Ver `.env.example` para
os comentários completos.

| Variável | Obrigatória | Default | Descrição |
|---|---|---|---|
| `VAULT_PATH` | sim | — | Caminho absoluto para a subpasta do vault dentro do clone git (ex: `.../SecondBrain/SecondBrain`). |
| `MCP_AUTH_TOKEN` | sim | — | Token exigido em `Authorization: Bearer <token>` em toda requisição HTTP. |
| `ALLOWED_HOST` | sim | — | Host(s) permitido(s) para proteção contra DNS rebinding do Streamable HTTP (ex: `localhost:8000` local, domínio público em produção). |
| `GIT_REMOTE` | não | `origin` | Remote git usado para pull/push automático. |
| `GIT_AUTHOR` | não | `MCP Bot <mcp@bot>` | Autor dos commits automáticos feitos pelo servidor. |
| `SYNC_PULL_INTERVAL` | não | `300` | Segundos entre pulls de frescor em background. `0` desliga o pull periódico. |
| `ALLOW_DESTRUCTIVE` | não | `false` | Libera overwrite/delete de notas. Mantenha `false` em produção. |
| `PORT` | não | `8000` | Porta do uvicorn. |

## Deploy (EasyPanel)

Build via `Dockerfile`, expor por trás do Traefik com TLS. O container precisa de uma
deploy key SSH com permissão de push no repo do vault.

## Conectar no Claude Code

```bash
claude mcp add --transport http obsidian https://SEU-DOMINIO/mcp \
  --header "Authorization: Bearer SEU_TOKEN"
```

Depois, `/mcp` dentro do Claude Code lista as tools disponíveis.

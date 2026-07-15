# obsidian-mcp

Servidor MCP que expõe um vault do Obsidian (busca, leitura, criação e atualização de notas) via Streamable HTTP.

Ver a SPEC completa na nota do vault: `01-Projetos/Servidor MCP do Obsidian.md`.

## Status

Scaffold inicial. `config.py`, `auth.py`, `sync.py` e `server.py` estão funcionais.
`vault.py` e `tools.py` são esqueletos (`NotImplementedError`) — implementação pendente.

## Setup local

```bash
uv sync
cp .env.example .env
# editar .env: VAULT_PATH deve apontar para a subpasta do vault dentro do clone
# (ex: .../SecondBrain/SecondBrain), e MCP_AUTH_TOKEN para um token forte.
uv run uvicorn src.server:app --reload
```

Testar com o MCP Inspector antes de expor remotamente:

```bash
npx @modelcontextprotocol/inspector uv run python -m src.server
```

## Variáveis de ambiente

Ver `.env.example` para a lista completa (`VAULT_PATH`, `MCP_AUTH_TOKEN`, `GIT_REMOTE`,
`GIT_AUTHOR`, `SYNC_PULL_INTERVAL`, `ALLOW_DESTRUCTIVE`, `PORT`).

## Deploy (EasyPanel)

Build via `Dockerfile`, expor por trás do Traefik com TLS. O container precisa de uma
deploy key SSH com permissão de push no repo do vault.

## Conectar no Claude Code

```bash
claude mcp add --transport http obsidian https://SEU-DOMINIO/mcp \
  --header "Authorization: Bearer SEU_TOKEN"
```

Depois, `/mcp` dentro do Claude Code lista as tools disponíveis.

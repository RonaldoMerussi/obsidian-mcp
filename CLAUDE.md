# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

MCP server exposing an Obsidian vault (search/read/list/create/update notes) over Streamable HTTP, backed by a git-synced vault directory. The full SPEC lives in the Obsidian vault itself (`01-Projetos/Servidor MCP do Obsidian.md`), not in this repo.

## Status

Scaffold stage. `config.py`, `auth.py`, `sync.py`, `server.py` are functional. `vault.py` and `tools.py` are stubs (`raise NotImplementedError`) with matching `pytest.skip("TODO...")` tests in `tests/` — implementing these per the SPEC is the main pending work.

When implementing them, keep the existing `TODO(ronaldo)` contract documented in their docstrings:
- `tools.py` functions must return `{"error": ...}` dicts instead of raising, per the SPEC's error-handling requirement.
- `vault.py`'s `resolve_safe_path` (path-traversal defense) is the priority, per the test file's own comment — it's the bug that would leak the whole filesystem.

## Commands

- Setup: `uv sync`, then `cp .env.example .env` and edit `VAULT_PATH` (must point at the vault subfolder inside a git clone, e.g. `.../SecondBrain/SecondBrain`) and `MCP_AUTH_TOKEN`.
- Run dev server: `uv run uvicorn src.server:app --reload`
- Run tests: `uv run pytest`
- Manual MCP testing (do before exposing remotely): `npx @modelcontextprotocol/inspector uv run python -m src.server`

## Architecture

Request flow spans several small files:

- `server.py` builds a `FastMCP` app, registers the 5 tools from `tools.py`, and wraps it in `BearerAuthMiddleware` (`auth.py`), which checks `Authorization: Bearer <MCP_AUTH_TOKEN>` on every HTTP request.
- `tools.py` holds the 5 MCP tool entry points (`search_notes`, `read_note`, `list_notes`, `create_note`, `update_section`). Write tools call `sync.py`'s `sync_pull()` before editing and `sync_write()` (commit+push) after, keeping the vault's git repo in sync with the remote around every mutation.
- `vault.py` is the filesystem layer: safe path resolution scoped to `VAULT_PATH` (must reject `..`, absolute paths, and symlink escapes), note read/write, frontmatter parsing, and section-level replace/append editing.
- `sync.py` wraps GitPython operations (`pull`/`commit`/`push`) against the vault's git repo, raising `SyncConflictError` on merge conflicts.
- `config.py` is a `pydantic-settings` `Settings` object (`VAULT_PATH`, `MCP_AUTH_TOKEN`, `GIT_REMOTE`, `GIT_AUTHOR`, `SYNC_PULL_INTERVAL`, `ALLOW_DESTRUCTIVE`, `PORT`) loaded from `.env`. `ALLOW_DESTRUCTIVE` gates overwrite/delete behavior and should stay `false` in production.
- Deploy: `Dockerfile` builds on `python:3.11-slim` with `git` + `openssh-client` installed (needed for the container's deploy key to push to the vault's git remote), run behind Traefik/TLS on EasyPanel.

## Notes

README and existing code comments are in Portuguese — mirror that when editing them.

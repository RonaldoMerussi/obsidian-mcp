#!/bin/sh
set -e

# 1. escrever a chave SSH que veio por env var
mkdir -p /root/.ssh
echo "$SSH_PRIVATE_KEY_B64" | base64 -d > /root/.ssh/id_ed25519
chmod 600 /root/.ssh/id_ed25519
ssh-keyscan github.com >> /root/.ssh/known_hosts

# 2. clonar o vault se ainda não existe
if [ ! -d /data/vault/.git ]; then
    git clone "$GIT_REPO_URL" /data/vault
fi

# 3. identidade dos commits
git config --global user.name "MCP Bot"
git config --global user.email "mcp@bot"
git config --global --add safe.directory /data/vault

# 4. sobe o servidor
exec uv run python -m src.server
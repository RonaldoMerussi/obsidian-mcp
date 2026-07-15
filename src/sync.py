from git import GitCommandError, Repo

from .config import settings


class SyncConflictError(Exception):
    """Raised when a git pull fails due to a merge conflict."""


def _repo() -> Repo:
    return Repo(settings.vault_path)


def sync_pull() -> None:
    repo = _repo()
    try:
        repo.remotes[settings.git_remote].pull()
    except GitCommandError as exc:
        raise SyncConflictError(
            "Conflito de merge ao dar pull no vault — resolva no Obsidian."
        ) from exc


def sync_commit(message: str) -> None:
    repo = _repo()
    repo.git.add(A=True)
    if repo.is_dirty():
        repo.git.commit(m=message, author=settings.git_author)


def sync_push() -> None:
    repo = _repo()
    repo.remotes[settings.git_remote].push()


def sync_write(message: str) -> None:
    """Call after a tool writes to the vault: commit then push."""
    sync_commit(message)
    sync_push()

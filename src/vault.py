"""Filesystem access to the vault: safe path resolution, note read/write, frontmatter parsing.

TODO(ronaldo): implement the bodies below. Signatures and docstrings mirror
the SPEC (section 7 for resolve_safe_path, section 9 for the tool contracts).
"""

from dataclasses import dataclass
from pathlib import Path

from .config import settings
import frontmatter


class UnsafePathError(ValueError):
    """Raised when a requested path resolves outside the vault root."""


class NoteNotFoundError(FileNotFoundError):
    """Raised when a note does not exist at the given path."""


class NoteExistsError(FileExistsError):
    """Raised when create_note would overwrite an existing note and ALLOW_DESTRUCTIVE is false."""


class HeadingNotFoundError(ValueError):
    """Raised when update_section can't find the requested heading."""


@dataclass
class Note:
    path: str
    content: str
    frontmatter: dict


def resolve_safe_path(rel_path: str, vault_root: Path | None = None) -> Path:
    if vault_root is None:
        vault_root = settings.vault_path
    path = (vault_root / rel_path).resolve()
    if not path.is_relative_to(vault_root.resolve()):
        raise UnsafePathError(f"Caminho fora do vault: {rel_path}")
    return path


def read_note(path: str) -> Note:
    full_path = resolve_safe_path(path)
    if not full_path.exists():
        raise NoteNotFoundError(path)
    raw = full_path.read_text(encoding="utf-8")
    post = frontmatter.loads(raw)
    return Note(path=path, content=post.content, frontmatter=post.metadata)
    
    


def write_note(path: str, content: str, frontmatter_dict: dict | None = None, overwrite: bool = False) -> None:
    full_path = resolve_safe_path(path)
    if full_path.exists() and not overwrite:
        raise NoteExistsError(path)
    post = frontmatter.Post(content, **(frontmatter_dict or {}))
    final_text = frontmatter.dumps(post)
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(final_text, encoding="utf-8")


def list_notes(folder: str | None = None, tag: str | None = None) -> list[Note]:
    vault_root = settings.vault_path
    notes = []
    for path in vault_root.rglob("*.md"):
        rel = path.relative_to(vault_root).as_posix()
        note = read_note(str(rel))
        notes.append(note)
    if folder:
        notes = [note for note in notes if note.path.startswith(folder)]
    if tag:
        notes = [note for note in notes if tag in note.frontmatter.get("tags", [])]
    return notes


def search_notes(query: str, tag: str | None = None, limit: int = 10) -> list[Note]:
    if not query:
        raise ValueError("query não pode ser vazia")
    if not 1 <= limit <= 50:
        raise ValueError("limit deve estar entre 1 e 50")
    notes = list_notes(tag=tag)
    q = query.lower()
    resultados = []
    for note in notes:
        if q in note.path.lower() or q in note.content.lower() or q in str(note.frontmatter).lower():
            resultados.append(note)
    return resultados[:limit]


def replace_section(path: str, heading: str, new_content: str, mode: str = "replace") -> None:
    note = read_note(path)
    lines = note.content.split("\n")
    start_index = None
    for i, line in enumerate(lines):
        if line.strip() == heading:
            start_index = i
            break
    if start_index is None:
        raise HeadingNotFoundError(heading)
    end_index = len(lines)
    for i in range(start_index + 1, len(lines)):
        if lines[i].startswith("#"):
            end_index = i
            break
    if new_content.strip().startswith(heading):
        raise ValueError(f"new_content não deve começar com {heading} - ele é preservado automaticamente")
    if mode == "append":
        middle = lines[start_index+1:end_index]
        new_text = "\n".join(lines[:start_index+1] + middle + [new_content] + lines[end_index:])
    else:
        middle = [new_content]
        new_text = "\n".join(lines[:start_index+1] + middle + lines[end_index:])
    write_note(path, new_text, frontmatter_dict=note.frontmatter, overwrite=True)
    

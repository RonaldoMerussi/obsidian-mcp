"""The 5 v1 MCP tools. Contract per SPEC section 9.

TODO(ronaldo): implement the bodies below, wiring vault.py + sync.py together.
Each tool must return a structured {"error": "..."} dict instead of raising,
per the SPEC's error-handling requirement.
"""

from . import vault
##from .sync import sync_pull, sync_write





def search_notes(query: str, tag: str | None = None, limit: int = 10) -> list[dict]:
    """Pesquisa notas por conteúdo, título e tags."""
    try:
        notes = vault.search_notes(query, tag, limit)
        return [
            {
                "path": note.path,
                "content": note.content,
                "frontmatter": note.frontmatter,
            }
            for note in notes
        ]
    except vault.UnsafePathError as e:
        return{"error":str(e), "code": "unsafe_path_error"}
    except vault.NoteNotFoundError as e:
        return{"error":str(e), "code": "note_not_found"}
    


def read_note(path: str) -> dict:
    """Lê uma nota do vault e devolve o conteúdo e o frontmatter"""
    try:
        note = vault.read_note(path)
        return {
        "path": note.path,
        "content": note.content,
        "frontmatter": note.frontmatter,
    }
    except vault.UnsafePathError as e:
        return{"error":str(e), "code": "unsafe_path_error"}
    except vault.NoteNotFoundError as e:
        return{"error":str(e), "code": "note_not_found"}
    


def list_notes(folder: str | None = None, tag: str | None = None) -> list[dict]:
    """Lista notas, opcionalmente filtradas por pasta ou tag.
    Returns: list of {path, title, tags, modified_at}.
    """
    try:
        notes = vault.list_notes(folder, tag)
        return [
            {
                "path": note.path,
                "title": note.frontmatter.get("title"),
                "tags": note.frontmatter.get("tags", []),
                "atualizado": note.frontmatter.get("atualizado"),
            }
            for note in notes
        ]
    except vault.UnsafePathError as e:
        return{"error":str(e), "code": "unsafe_path_error"}
    except vault.NoteNotFoundError as e:
        return{"error":str(e), "code": "note_not_found"}
    


def write_note(path: str, content: str, frontmatter: dict | None = None) -> dict:
    """Cria uma nova nota. Não sobrescreve a menos que ALLOW_DESTRUCTIVE esteja ativo.
    Retorna: {path, created: true}.
    Erros: 409 se o arquivo já existir e ALLOW_DESTRUCTIVE for false.
    """
    try:
        vault.write_note(path, content, frontmatter)
        return {"path": path, "created": True}
    except vault.UnsafePathError as e:
        return{"error":str(e), "code": "unsafe_path_error"}
    except vault.NoteExistsError as e:
        return{"error":str(e), "code": "note_exists"}
    


def replace_section(path: str, heading: str, new_content: str, mode: str = "replace") -> dict:
    """Edição cirúrgica: encontra um `## heading` e substitui ou adiciona o conteúdo da seção.
    mode: "replace" | "append".
    Comportamento: pull -> edita apenas a seção -> commit -> push.
    Retorna: {path, updated: true, heading}.
    Erros: 404 se o heading não existir.
    """
    try:
        vault.replace_section(path, heading, new_content, mode)
        return {"path": path, "updated": True, "heading": heading}
    except vault.UnsafePathError as e:
        return{"error":str(e), "code": "unsafe_path_error"}
    except vault.HeadingNotFoundError as e:
        return{"error":str(e), "code": "heading_not_found"}
    

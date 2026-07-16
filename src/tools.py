from . import vault
from .sync import sync_pull, sync_write, SyncConflictError
from .vault import AmbiguousHeadingError





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
        sync_pull()
        vault.write_note(path, content, frontmatter)
        sync_write(f"update: {path}")
        return {"path": path, "created": True}
    except vault.UnsafePathError as e:
        return{"error":str(e), "code": "unsafe_path_error"}
    except vault.NoteExistsError as e:
        return{"error":str(e), "code": "note_exists"}
    except SyncConflictError as e:
        return {"error": str(e), "code": "sync_conflict"}
    except Exception as e:
        return {"error": f"{type(e).__name__}:{str(e)}", "code": "internal_error"}


def replace_section(path: str, heading: str, new_content: str, mode: str = "replace") -> dict:
    """Substitui ou anexa conteúdo em uma seção específica de uma nota.

    Use quando quiser editar apenas uma parte da nota, sem tocar no resto.

    Args:
        path: caminho relativo da nota, ex: "01-Projetos/nota.md"
        heading: o heading completo, incluindo os #, ex: "## Ideias"
        occurrence: qual ocorrência do heading editar, quando ele aparece
            mais de uma vez na nota. 1 = primeira, na ordem do documento.
            Omita quando o heading for único. Se o heading repetir e você
            omitir, a função recusa e informa quantas ocorrências existem.
        new_content: APENAS o corpo da seção, SEM repetir o heading.
            A função preserva o heading original.
        mode: "replace" troca o conteúdo da seção; "append" adiciona ao final dela.

    Exemplo:
        replace_section("01-Projetos/nota.md", "## Ideias", "texto novo")
        → a seção "## Ideias" passa a conter "texto novo"
        Exemplo com heading repetido:
        # a nota tem "### Checklist" em "## Fase 1" e em "## Fase 2"
        replace_section("nota.md", "### Checklist", "novo item", occurrence=2)
        → edita o Checklist da Fase 2; o da Fase 1 fica intacto

    Nota: assume que o heading é único na nota. Se houver repetidos,
    a primeira ocorrência é usada.
    """
    try:
        sync_pull()
        vault.replace_section(path, heading, new_content, mode)
        sync_write(f"update: {path}")
        return {"path": path, "updated": True, "heading": heading}
    except vault.UnsafePathError as e:
        return{"error":str(e), "code": "unsafe_path_error"}
    except vault.HeadingNotFoundError as e:
        return{"error":str(e), "code": "heading_not_found"}
    except SyncConflictError as e:
        return {"error": str(e), "code": "sync_conflict"}
    except ValueError as e:
        return {"error": str(e), "code": "invalid_content"}
    except AmbiguousHeadingError as e:
        return {"error": str(e), "code": "ambiguous_heading"}
    except Exception as e:
        return {"error": f"{type(e).__name__}:{str(e)}", "code": "internal_error"}
    

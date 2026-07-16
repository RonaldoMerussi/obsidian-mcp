"""TODO(ronaldo): fill these in alongside vault.py's implementation.

Priority: path traversal first — it's the bug that leaks the whole filesystem.
"""

import pytest
from src.vault import resolve_safe_path, UnsafePathError, NoteNotFoundError, read_note, list_notes, write_note, NoteExistsError
from src.vault import search_notes, replace_section, HeadingNotFoundError

def test_resolve_safe_path_rejects_dotdot_traversal(tmp_path):
    with pytest.raises(UnsafePathError):
        resolve_safe_path("../CLAUDE.md", tmp_path)

def test_resolve_safe_path_rejects_absolute_escape(tmp_path):
    with pytest.raises(UnsafePathError):
        resolve_safe_path("/etc/passwd", tmp_path)


def test_resolve_safe_path_rejects_symlink_escape():
    pytest.skip("TODO: implement alongside vault.resolve_safe_path")


def test_resolve_safe_path_allows_path_inside_vault(tmp_path):
    result = resolve_safe_path("00-Inbox/nota.md", tmp_path)
    assert result == (tmp_path / "00-Inbox/nota.md").resolve()
    


def test_read_note_returns_content_and_frontmatter(tmp_path, monkeypatch):
    monkeypatch.setattr("src.vault.settings.vault_path", tmp_path)
    note_path = tmp_path / "nota.md"
    note_path.write_text("---\ntype: projeto\n---\nconteúdo", encoding="utf-8")
    note = read_note("nota.md")
    assert note.path == "nota.md"
    assert note.content == "conteúdo"
    assert note.frontmatter == {"type": "projeto"}


def test_read_note_raises_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("src.vault.settings.vault_path", tmp_path)
    with pytest.raises(NoteNotFoundError):
        read_note("não-existe.md")


def test_write_note_raises_when_exists_and_not_overwrite(tmp_path, monkeypatch):
    monkeypatch.setattr("src.vault.settings.vault_path", tmp_path)
    (tmp_path / "exist.md").write_text("conteudo antigo", encoding="utf-8")
    with pytest.raises(NoteExistsError):
        write_note("exist.md", "conteudo novo")
    


def test_list_notes_filters_by_folder_and_tag(tmp_path, monkeypatch):
    monkeypatch.setattr("src.vault.settings.vault_path", tmp_path)

    nota_com_tag = """---
tags: [projeto]
---
conteúdo"""

    nota_sem_tag = """---
tags: []
---
conteúdo"""

    (tmp_path / "folder").mkdir()
    (tmp_path / "folder" / "nota1.md").write_text(nota_com_tag, encoding="utf-8")
    (tmp_path / "nota2.md").write_text(nota_com_tag, encoding="utf-8")
    (tmp_path / "nota3.md").write_text(nota_sem_tag, encoding="utf-8")

    notes = list_notes(folder="folder", tag="projeto")
    assert len(notes) == 1
    assert notes[0].path == "folder/nota1.md"



def test_replace_section_replace_mode(tmp_path, monkeypatch):
    monkeypatch.setattr("src.vault.settings.vault_path", tmp_path)
    nota = """# Titulo

## Ideias
texto antigo

## Tarefas
nao pode tocar"""
    (tmp_path / "nota.md").write_text(nota, encoding="utf-8")

    replace_section("nota.md", "## Ideias", "texto novo")

    resultado = read_note("nota.md")
    assert "texto novo" in resultado.content
    assert "texto antigo" not in resultado.content
    assert "nao pode tocar" in resultado.content   # ← a prova de fogo


def test_replace_section_append_mode(tmp_path, monkeypatch):
    monkeypatch.setattr("src.vault.settings.vault_path", tmp_path)
    nota = """# Titulo

## Ideias
texto antigo

## Tarefas
nao pode tocar"""
    (tmp_path / "nota.md").write_text(nota, encoding="utf-8")

    replace_section("nota.md", "## Ideias", "texto novo", mode="append")

    resultado = read_note("nota.md")
    assert "texto novo" in resultado.content
    assert "nao pode tocar" in resultado.content  



def test_replace_section_raises_when_heading_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("src.vault.settings.vault_path", tmp_path)
    (tmp_path / "sem-heading.md").write_text("conteudo antigo", encoding="utf-8")
    with pytest.raises(HeadingNotFoundError):
        replace_section("sem-heading.md", "# Titulo", "texto novo")

def test_search_notes_finds_by_content(tmp_path, monkeypatch):
    monkeypatch.setattr("src.vault.settings.vault_path", tmp_path)
    (tmp_path / "nota1.md").write_text("falando sobre python", encoding="utf-8")
    (tmp_path / "nota2.md").write_text("falando sobre javascript", encoding="utf-8")
    resultados = search_notes("python")
    assert len(resultados) == 1
    assert resultados[0].path == "nota1.md"

def test_replace_section_rejects_content_with_heading(tmp_path, monkeypatch):
    monkeypatch.setattr("src.vault.settings.vault_path", tmp_path)
    nota = """# Titulo

## Ideias
texto antigo"""
    (tmp_path / "nota.md").write_text(nota, encoding="utf-8")

    with pytest.raises(ValueError):
        replace_section("nota.md", "## Ideias", "## Ideias\ntexto novo")
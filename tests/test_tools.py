"""TODO(ronaldo): fill these in alongside tools.py's implementation.

Each tool needs a happy-path case plus its documented error cases
(404 / 409 / unsafe path), per SPEC section 9.
"""

import pytest


def test_search_notes_happy_path():
    pytest.skip("TODO: implement alongside tools.search_notes")


def test_search_notes_rejects_empty_query():
    pytest.skip("TODO: implement alongside tools.search_notes")


def test_read_note_happy_path():
    pytest.skip("TODO: implement alongside tools.read_note")


def test_read_note_404_when_missing():
    pytest.skip("TODO: implement alongside tools.read_note")


def test_list_notes_happy_path():
    pytest.skip("TODO: implement alongside tools.list_notes")


def test_create_note_happy_path():
    pytest.skip("TODO: implement alongside tools.create_note")


def test_create_note_409_when_exists_and_not_allow_destructive():
    pytest.skip("TODO: implement alongside tools.create_note")


def test_update_section_replace_mode():
    pytest.skip("TODO: implement alongside tools.update_section")


def test_update_section_append_mode():
    pytest.skip("TODO: implement alongside tools.update_section")


def test_update_section_404_when_heading_missing():
    pytest.skip("TODO: implement alongside tools.update_section")

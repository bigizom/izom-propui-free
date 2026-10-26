# SPDX-License-Identifier: GPL-3.0-or-later

import ast
import hashlib

from .generated_registry_common import (
    _IZOM_PROPUI_FREE_TEXT_REGISTRY_KEY_PROP,
    _izom_propui_free_is_generated_panel_class_name,
    _izom_propui_free_is_managed_portable_text_name,
    _izom_propui_free_is_portable_registry_key,
)
from ..core.diagnostics import (
    IZOM_PROPUI_FREE_RECOVERABLE_ERRORS,
    izom_propui_free_log_debug,
    izom_propui_free_log_warning,
)
from .generated_state import _izom_propui_free_data_collection


def _izom_propui_free_text_sources_for_registry_key(registry_key):
    key = str(registry_key or '').strip()
    if not key:
        return []
    sources = []
    for text in list(_izom_propui_free_data_collection('texts') or []):
        if _izom_propui_free_text_registry_key(text) != key:
            continue
        try:
            sources.append(str(text.as_string() or ''))
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_warning(
                f"Could not read generated UI Text datablock {getattr(text, 'name', '')}",
                category='Generated UI',
                exception=exc,
            )
    return sources

def _izom_propui_free_text_registry_key(text, *, use_cached=False):
    text_name = str(getattr(text, 'name', '') or '').strip()
    if not text_name or not text_name.lower().endswith('.py'):
        return ''
    if use_cached:
        try:
            cached_key = str(text.get(_IZOM_PROPUI_FREE_TEXT_REGISTRY_KEY_PROP, '') or '').strip()
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS:
            cached_key = ''
        if _izom_propui_free_is_portable_registry_key(cached_key):
            return cached_key
    try:
        source = str(text.as_string() or '')
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_warning(
            f"Could not read generated UI Text datablock {text_name}",
            category='Generated UI',
            exception=exc,
        )
        return ''
    registry_key = _izom_propui_free_registry_key_from_source(source, source_name=text_name)
    _izom_propui_free_mark_text_registry_key(text, registry_key)
    return registry_key


def _izom_propui_free_mark_text_registry_key(text, registry_key):
    key = str(registry_key or '').strip()
    if text is None or not _izom_propui_free_is_portable_registry_key(key):
        return
    try:
        text[_IZOM_PROPUI_FREE_TEXT_REGISTRY_KEY_PROP] = key
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_debug(
            f"Could not cache generated UI registry key on Text {getattr(text, 'name', '')}",
            category='Generated UI',
            exception=exc,
        )


def _izom_propui_free_registry_key_from_source(source, *, source_name=''):
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped.startswith('_REGISTRY_KEY') or '=' not in stripped:
            continue
        try:
            value = ast.literal_eval(stripped.split('=', 1)[1].strip())
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_debug(
                f"Could not parse generated UI registry key line in {source_name or 'generated source'}",
                category='Generated UI',
                exception=exc,
            )
            return ''
        return str(value or '').strip()
    return ''


def _izom_propui_free_is_portable_generated_text(text):
    name = str(getattr(text, 'name', '') or '').strip()
    if _izom_propui_free_is_managed_portable_text_name(name):
        return True
    return _izom_propui_free_is_portable_registry_key(_izom_propui_free_text_registry_key(text))


def _izom_propui_free_text_registry_key_map(texts=None, *, use_cached=False):
    if texts is None:
        texts = _izom_propui_free_data_collection('texts')
    key_map = {}
    for text in list(texts or []):
        key = _izom_propui_free_text_registry_key(text, use_cached=use_cached)
        if _izom_propui_free_is_portable_registry_key(key):
            key_map[key] = str(getattr(text, 'name', '') or '').strip()
    return key_map


def _izom_propui_free_text_generated_panel_class_names(text):
    text_name = str(getattr(text, 'name', '') or '').strip()
    if not text_name or not text_name.lower().endswith('.py'):
        return set()
    try:
        source = str(text.as_string() or '')
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_warning(
            f"Could not read generated UI Text datablock {text_name}",
            category='Generated UI',
            exception=exc,
        )
        return set()
    class_names = set()
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped.startswith('class ') or '(' not in stripped:
            continue
        name = stripped[6:].split('(', 1)[0].strip()
        if _izom_propui_free_is_generated_panel_class_name(name):
            class_names.add(name)
    return class_names


def _izom_propui_free_generated_panel_class_names_from_texts(texts=None):
    if texts is None:
        texts = _izom_propui_free_data_collection('texts')
    class_names = set()
    for text in list(texts or []):
        if not _izom_propui_free_is_portable_generated_text(text):
            continue
        class_names.update(_izom_propui_free_text_generated_panel_class_names(text))
    return class_names


def _izom_propui_free_text_lifecycle_fingerprint(text, *, include_source_hash=True):
    name = str(getattr(text, 'name', '') or '').strip()
    if not name or not name.lower().endswith('.py'):
        return None
    try:
        pointer = int(text.as_pointer())
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS:
        pointer = id(text)
    if not include_source_hash:
        return (name, pointer)
    try:
        source = str(text.as_string() or '')
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_warning(
            f"Could not read generated UI Text datablock {name}",
            category='Generated UI',
            exception=exc,
        )
        return (name, '', 0, '')
    digest = hashlib.sha1(source.encode('utf-8')).hexdigest()[:16]
    return (
        name,
        _izom_propui_free_registry_key_from_source(source, source_name=name),
        len(source),
        digest,
    )

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

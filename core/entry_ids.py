# SPDX-License-Identifier: GPL-3.0-or-later

from .diagnostics import izom_propui_free_log_recovered
import re
import uuid

from .constants import IZOM_PROPUI_FREE_MAX_PROP_ID_TEXT
from .text import (
    _izom_propui_free_limit_label_input_text,
    _izom_propui_free_limit_prop_id_input_text,
    _izom_propui_free_limit_tooltip_input_text,
    izom_propui_free_entry_display_name,
)

_IZOM_PROPUI_FREE_ENTRY_ID_ACCESS_ERRORS = (
    AttributeError,
    TypeError,
    ValueError,
    RuntimeError,
    ReferenceError,
)


def _izom_propui_free_limit_entry_snapshot_strings(entry):
    if entry is None:
        return entry

    if isinstance(entry, dict):
        entry['prop_id'] = _izom_propui_free_limit_prop_id_input_text(entry.get('prop_id', ''))
        entry['label'] = _izom_propui_free_limit_label_input_text(entry.get('label', ''))
        entry['editor_label'] = _izom_propui_free_limit_label_input_text(entry.get('editor_label', ''))
        entry['description'] = _izom_propui_free_limit_tooltip_input_text(entry.get('description', ''))
        for attr_name in (
            'bool_label_true',
            'bool_label_false',
        ):
            entry[attr_name] = _izom_propui_free_limit_label_input_text(entry.get(attr_name, ''))
        for collection_name in ('value_labels',):
            for item in entry.get(collection_name, []) or []:
                if isinstance(item, dict):
                    item['label'] = _izom_propui_free_limit_label_input_text(item.get('label', ''))
        return entry

    try:
        entry.prop_id = _izom_propui_free_limit_prop_id_input_text(getattr(entry, 'prop_id', ''))
    except _IZOM_PROPUI_FREE_ENTRY_ID_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )

    for attr_name in (
        'label',
        'editor_label',
        'bool_label_true',
        'bool_label_false',
    ):
        try:
            setattr(entry, attr_name, _izom_propui_free_limit_label_input_text(getattr(entry, attr_name, '')))
        except _IZOM_PROPUI_FREE_ENTRY_ID_ACCESS_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='Core',
                exception=exc,
        )

    for attr_name in ('description',):
        try:
            setattr(entry, attr_name, _izom_propui_free_limit_tooltip_input_text(getattr(entry, attr_name, '')))
        except _IZOM_PROPUI_FREE_ENTRY_ID_ACCESS_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='Core',
                exception=exc,
        )

    try:
        for collection_name in ('value_labels',):
            for item in getattr(entry, collection_name, []) or []:
                item.label = _izom_propui_free_limit_label_input_text(getattr(item, 'label', ''))
    except _IZOM_PROPUI_FREE_ENTRY_ID_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )

    return entry


def _izom_propui_free_string_limit_updated(field_name, limit_func):
    def _update(entry, _context):
        try:
            current = getattr(entry, field_name, '')
        except _IZOM_PROPUI_FREE_ENTRY_ID_ACCESS_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='Core',
                exception=exc,
            )
            return

        limited = limit_func(current)
        if current == limited:
            return

        try:
            setattr(entry, field_name, limited)
        except _IZOM_PROPUI_FREE_ENTRY_ID_ACCESS_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='Core',
                exception=exc,
        )

    return _update


def _izom_propui_free_new_uid():
    return uuid.uuid4().hex


_IZOM_PROPUI_FREE_DEFAULT_PROP_ID_PATTERN = re.compile(r"^prop_(\d+)$")


def _izom_propui_free_next_default_entry_n(snapshots):
    """Pick the next ``N`` for a new entry's default ``prop_id`` / ``label``.

    Returns the smallest positive integer ``N`` such that ``prop_N`` is not
    currently used by any of ``snapshots``. This keeps the default naming
    convention (``prop_1`` + ``Property 1``, ``prop_2`` + ``Property 2``, ...)
    truly unique even after mid-list deletions, instead of the older
    ``len(snapshots) + 1`` heuristic which would silently reuse a freed slot
    and collide with the entry that took it.
    """
    used = set()
    for snap in snapshots or ():
        prop_id = str((snap or {}).get('prop_id', '') or '').strip()
        match = _IZOM_PROPUI_FREE_DEFAULT_PROP_ID_PATTERN.match(prop_id)
        if match is None:
            continue
        try:
            used.add(int(match.group(1)))
        except (TypeError, ValueError):
            continue
    candidate = 1
    while candidate in used:
        candidate += 1
    return candidate


def _izom_propui_free_unique_prop_id(desired, existing_ids):
    base = _izom_propui_free_limit_prop_id_input_text(desired) or 'prop'
    if base not in existing_ids:
        return base

    suffix_match = re.match(r"^(.*?)(?:\.(\d+))$", base)
    if suffix_match:
        suffix_base = (suffix_match.group(1) or '').rstrip('. ') or 'prop'
        index = int(suffix_match.group(2) or '0') + 1
    else:
        suffix_base = base
        index = 1

    while True:
        suffix = f".{index:03d}"
        trimmed_base = suffix_base[:max(1, IZOM_PROPUI_FREE_MAX_PROP_ID_TEXT - len(suffix))].rstrip('. ')
        candidate = f"{trimmed_base}{suffix}"
        candidate = _izom_propui_free_limit_prop_id_input_text(candidate) or f"prop{suffix}"
        if candidate not in existing_ids:
            return candidate
        index += 1


def _izom_propui_free_ensure_unique_snapshot_ids(snapshots):
    existing_ids = set()
    renamed = []

    for snap in snapshots:
        if snap.get('prop_type') == 'TEXT':
            continue

        raw = str(snap.get('prop_id', '') or '').strip()
        candidate = _izom_propui_free_unique_prop_id(raw or 'prop', existing_ids)
        if candidate != raw:
            renamed.append((raw, candidate, snap.get('uid', '')))
            snap['prop_id'] = candidate
        existing_ids.add(candidate)

    return renamed


def _izom_propui_free_entry_label(entry_or_snap):
    return izom_propui_free_entry_display_name(entry_or_snap, default='Entry')

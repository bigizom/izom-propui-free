# SPDX-License-Identifier: GPL-3.0-or-later

from .editor_hooks import izom_propui_free_invalidate_editor_entry_cache

from .diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .diagnostics import izom_propui_free_log_recovered
from .value_access_entries import izom_propui_free_clear_value_access_memo
import json
import sys



_IZOM_PROPUI_FREE_PARAMS_STATE_CACHE = {}
_IZOM_PROPUI_FREE_VALUE_LABEL_OWNER_CACHE = {}
_IZOM_PROPUI_FREE_CACHED_ENTRY_DISPLAY_FIELDS = (
    'label',
    'editor_label',
    'description',
    'bool_label_true',
    'bool_label_false',
)
_IZOM_PROPUI_FREE_CACHE_FIELD_DEPENDENTS = {
    'entry_snapshots': (
        'entry_index_by_uid',
        'same_type_peer_counts',
        'runtime_entry_snapshots',
        'runtime_entries',
        'visible_layout_rows',
        'generated_layout_state',
        'entry_navigation_snapshots',
    ),
    'runtime_entry_snapshots': (
        'runtime_tree_state',
        'runtime_entries',
        'runtime_layout_entries',
        'parent_lookup',
        'visibility_scopes',
        'visibility_inheritance_info',
        'entry_draw_state',
    ),
    'entry_tree_snapshots': ('tree_state',),
    'entry_navigation_snapshots': (
        'entry_navigation_tree_state',
        'entry_navigation_index_by_uid',
        'entry_navigation_draw_state',
        'generated_layout_state',
    ),
    'entry_navigation_tree_state': ('entry_navigation_draw_state',),
    'tree_state': ('visibility_scopes', 'entry_draw_state'),
    'layout_snapshots': (
        'layout_item_lookup',
        'visible_layout_rows',
        'generated_layout_state',
        'runtime_layout_entries',
    ),
    'visible_layout_rows': ('generated_layout_state', 'runtime_layout_entries'),
    'runtime_entries': (
        'runtime_layout_entries',
        'parent_lookup',
        'visibility_scopes',
        'visibility_inheritance_info',
        'entry_draw_state',
    ),
    'visibility_scopes': ('visibility_inheritance_info',),
    'entry_collapsed_uids': ('entry_collapsed_uid_set', 'entry_draw_state', 'entry_navigation_draw_state'),
    'layout_collapsed_row_uids': ('layout_collapsed_row_uid_set',),
}


def _izom_propui_free_pointer_guard_key(item):
    try:
        return int(item.as_pointer())
    except (AttributeError, TypeError, ValueError, ReferenceError) as exc:
        izom_propui_free_log_recovered(category='Core', exception=exc)
        return id(item)




def _izom_propui_free_params_cache_entry(params):
    if params is None:
        return None
    cache_key = _izom_propui_free_pointer_guard_key(params)
    return _IZOM_PROPUI_FREE_PARAMS_STATE_CACHE.setdefault(
        cache_key,
        {
            'params': params,
            'fields': {},
            'assembled_bundles': {},
        },
    )


def _izom_propui_free_cache_public(name, fallback=None):
    module = sys.modules.get(f"{__package__}.cache")
    if module is not None and hasattr(module, name):
        return getattr(module, name)
    if fallback is not None:
        return fallback
    return globals().get(name)


def _izom_propui_free_invalidate_assembled_bundles(cache_entry):
    if cache_entry is None:
        return
    assembled = cache_entry.get('assembled_bundles')
    if assembled:
        assembled.clear()


def _izom_propui_free_cached_params_field(params, field_name, builder):
    cache_entry = _izom_propui_free_params_cache_entry(params)
    if cache_entry is None:
        return builder()
    fields = cache_entry['fields']
    if field_name not in fields:
        fields[field_name] = builder()
    return fields[field_name]


def _izom_propui_free_normalize_cache_field_names(field_names):
    if not field_names:
        return set()

    pending = [field_names] if isinstance(field_names, str) else list(field_names)
    normalized = set()
    while pending:
        raw_name = pending.pop()
        field_name = str(raw_name or '').strip()
        if not field_name or field_name in normalized:
            continue
        normalized.add(field_name)
        pending.extend(_IZOM_PROPUI_FREE_CACHE_FIELD_DEPENDENTS.get(field_name, ()))
    return normalized


def _izom_propui_free_cached_uid_json_list(raw_value):
    try:
        parsed = json.loads(str(raw_value or '[]'))
    except (TypeError, ValueError, json.JSONDecodeError):
        parsed = []
    if not isinstance(parsed, (list, tuple)):
        return []

    ordered = []
    seen = set()
    for item in parsed:
        uid = str(item or '').strip()
        if not uid or uid in seen:
            continue
        ordered.append(uid)
        seen.add(uid)
    return ordered


def _izom_propui_free_patch_cached_entry_display_fields(params, entry):
    if params is None or entry is None:
        return False
    try:
        entry_uid = str(getattr(entry, 'uid', '') or '').strip()
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS:
        entry_uid = ''
    if not entry_uid:
        return False

    cache_entry = _IZOM_PROPUI_FREE_PARAMS_STATE_CACHE.get(_izom_propui_free_pointer_guard_key(params))
    if cache_entry is None:
        return False
    fields = cache_entry.get('fields', {})
    patched = False
    for field_name in ('entry_snapshots', 'runtime_entry_snapshots', 'entry_navigation_snapshots'):
        snapshots = fields.get(field_name)
        if not snapshots:
            continue
        for snapshot in snapshots:
            if not isinstance(snapshot, dict):
                continue
            if str(snapshot.get('uid', '') or '').strip() != entry_uid:
                continue
            for display_field in _IZOM_PROPUI_FREE_CACHED_ENTRY_DISPLAY_FIELDS:
                if display_field not in snapshot or not hasattr(entry, display_field):
                    continue
                try:
                    snapshot[display_field] = getattr(entry, display_field)
                    patched = True
                except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                    izom_propui_free_log_recovered(
                        category='Core',
                        exception=exc,
                    )
            break
    return patched


def izom_propui_free_invalidate_params_cache_fields(
    params=None,
    field_names=None,
    *,
    clear_value_label_owner=False,
):
    normalized_field_names = _izom_propui_free_normalize_cache_field_names(field_names)
    if not normalized_field_names and not clear_value_label_owner:
        return

    if (
        'entry_snapshots' in normalized_field_names
        or 'runtime_entry_snapshots' in normalized_field_names
        or 'runtime_entries' in normalized_field_names
    ):
        izom_propui_free_clear_value_access_memo()

    if params is None:
        for cache_entry in _IZOM_PROPUI_FREE_PARAMS_STATE_CACHE.values():
            fields = cache_entry.get('fields', {})
            for field_name in normalized_field_names:
                fields.pop(field_name, None)
            _izom_propui_free_invalidate_assembled_bundles(cache_entry)
        if clear_value_label_owner:
            _IZOM_PROPUI_FREE_VALUE_LABEL_OWNER_CACHE.clear()
        return

    cache_key = _izom_propui_free_pointer_guard_key(params)
    cache_entry = _IZOM_PROPUI_FREE_PARAMS_STATE_CACHE.get(cache_key)
    if cache_entry is not None:
        fields = cache_entry.get('fields', {})
        for field_name in normalized_field_names:
            fields.pop(field_name, None)
        _izom_propui_free_invalidate_assembled_bundles(cache_entry)

    if clear_value_label_owner:
        _IZOM_PROPUI_FREE_VALUE_LABEL_OWNER_CACHE.pop(cache_key, None)


def izom_propui_free_invalidate_params_cache(params=None):
    izom_propui_free_clear_value_access_memo()
    if params is None:
        _IZOM_PROPUI_FREE_PARAMS_STATE_CACHE.clear()
        _IZOM_PROPUI_FREE_VALUE_LABEL_OWNER_CACHE.clear()
    else:
        cache_key = _izom_propui_free_pointer_guard_key(params)
        _IZOM_PROPUI_FREE_PARAMS_STATE_CACHE.pop(cache_key, None)
        _IZOM_PROPUI_FREE_VALUE_LABEL_OWNER_CACHE.pop(cache_key, None)
    izom_propui_free_invalidate_editor_entry_cache(params)


from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

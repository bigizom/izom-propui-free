# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import izom_propui_free_log_recovered
import json

import bpy

from ..core.cache import izom_propui_free_cached_entry_navigation_bundle
from ..core.constants import izom_propui_free_normalize_multi_component_draw_mode
from ..core.value_access import izom_propui_free_entry_value_kind


_IZOM_PROPUI_FREE_COLLECTION_STATE_CACHE = {}
_IZOM_PROPUI_FREE_COLLECTION_STATE_CACHE_LIMIT = 128
_IZOM_PROPUI_FREE_COLLECTION_REVISION = {}
_IZOM_PROPUI_FREE_TRANSIENT_OPERATOR_REPORT = None
_IZOM_PROPUI_FREE_SELECTION_ACCESS_ERRORS = (
    AttributeError,
    TypeError,
    ValueError,
    RuntimeError,
    ReferenceError,
)


def _izom_propui_free_clear_selection_session_caches():
    global _IZOM_PROPUI_FREE_TRANSIENT_OPERATOR_REPORT

    _IZOM_PROPUI_FREE_COLLECTION_STATE_CACHE.clear()
    _IZOM_PROPUI_FREE_COLLECTION_REVISION.clear()
    _IZOM_PROPUI_FREE_TRANSIENT_OPERATOR_REPORT = None


def _izom_propui_free_set_transient_operator_report(level, message):
    global _IZOM_PROPUI_FREE_TRANSIENT_OPERATOR_REPORT

    level_text = str(level or 'INFO').strip().upper() or 'INFO'
    message_text = str(message or '').strip()
    if not message_text:
        _IZOM_PROPUI_FREE_TRANSIENT_OPERATOR_REPORT = None
        return
    _IZOM_PROPUI_FREE_TRANSIENT_OPERATOR_REPORT = (level_text, message_text)


def _izom_propui_free_pop_transient_operator_report():
    global _IZOM_PROPUI_FREE_TRANSIENT_OPERATOR_REPORT

    report = _IZOM_PROPUI_FREE_TRANSIENT_OPERATOR_REPORT
    _IZOM_PROPUI_FREE_TRANSIENT_OPERATOR_REPORT = None
    return report


def _izom_propui_free_report_operator(operator, level, message):
    level_text = str(level or 'INFO').strip().upper() or 'INFO'
    message_text = str(message or '').strip()
    if not message_text:
        return
    try:
        operator.report({level_text}, message_text)
    except _IZOM_PROPUI_FREE_SELECTION_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
    _izom_propui_free_set_transient_operator_report(level_text, message_text)


def _izom_propui_free_tag_all_redraw():
    try:
        window_manager = getattr(bpy.context, 'window_manager', None)
        windows = getattr(window_manager, 'windows', None) or []
    except _IZOM_PROPUI_FREE_SELECTION_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        windows = []
    for window in windows:
        screen = getattr(window, 'screen', None)
        areas = getattr(screen, 'areas', None) or []
        for area in areas:
            try:
                area.tag_redraw()
            except _IZOM_PROPUI_FREE_SELECTION_ACCESS_ERRORS as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )
                continue


def _izom_propui_free_uid_list_from_json(raw_value):
    try:
        data = json.loads(str(raw_value or '[]'))
    except (json.JSONDecodeError, TypeError, ValueError):
        data = []
    result = []
    seen = set()
    for item in data if isinstance(data, list) else []:
        uid = str(item or '').strip()
        if not uid or uid in seen:
            continue
        seen.add(uid)
        result.append(uid)
    return result


def _izom_propui_free_json_dumps(data):
    try:
        return json.dumps(data, separators=(',', ':'))
    except (TypeError, ValueError, OverflowError):
        return json.dumps(data)


def _izom_propui_free_set_attr_if_changed(owner, attr_name, value):
    try:
        if getattr(owner, attr_name) == value:
            return False
    except _IZOM_PROPUI_FREE_SELECTION_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
    try:
        setattr(owner, attr_name, value)
        return True
    except (AttributeError, TypeError, ValueError):
        return False


def _izom_propui_free_store_uid_list(owner, attr_name, uids):
    cleaned = []
    seen = set()
    for item in uids or []:
        uid = str(item or '').strip()
        if not uid or uid in seen:
            continue
        seen.add(uid)
        cleaned.append(uid)
    encoded = _izom_propui_free_json_dumps(cleaned)
    try:
        if getattr(owner, attr_name, '') != encoded:
            setattr(owner, attr_name, encoded)
    except (AttributeError, TypeError, ValueError) as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
    return cleaned


def _izom_propui_free_ensure_collection_item_uid(item):
    return str(getattr(item, 'uid', '') or '').strip()


def _izom_propui_free_collection_index_by_uid_live(collection, uid):
    target_uid = str(uid or '').strip()
    if not target_uid:
        return -1
    try:
        iterable = list(collection or [])
    except _IZOM_PROPUI_FREE_SELECTION_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(category='UI', exception=exc)
        iterable = []
    for index, item in enumerate(iterable):
        if _izom_propui_free_ensure_collection_item_uid(item) == target_uid:
            return index
    return -1


def _izom_propui_free_collection_selection_fields(collection_name):
    name = str(collection_name or '')
    return (
        f"{name}_active_index",
        f"{name}_active_uid",
        f"{name}_selected_uids_json",
        f"{name}_selection_anchor_uid",
    )


def _izom_propui_free_resolve_collection_active_index(owner, collection_name, *, default=0, strict_uid=False):
    collection = getattr(owner, collection_name, None) if owner is not None else None
    try:
        count = len(collection) if collection is not None else 0
    except _IZOM_PROPUI_FREE_SELECTION_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(category='UI', exception=exc)
        count = 0
    if count <= 0:
        return -1

    active_attr, active_uid_attr, _selected_attr, _anchor_attr = _izom_propui_free_collection_selection_fields(collection_name)
    active_uid = str(getattr(owner, active_uid_attr, '') or '').strip()
    index = _izom_propui_free_collection_index_by_uid_live(collection, active_uid)
    if index >= 0:
        return index
    if active_uid and strict_uid:
        return -1

    try:
        index = int(getattr(owner, active_attr, default) or default)
    except (AttributeError, TypeError, ValueError):
        index = default
    return max(0, min(index, count - 1))


def _izom_propui_free_data_value(data, attr_name, default=None):
    if isinstance(data, dict):
        return data.get(attr_name, default)
    return getattr(data, attr_name, default)


def _izom_propui_free_entry_index_by_uid(params):
    if params is None:
        return {}
    return izom_propui_free_cached_entry_navigation_bundle(params).get('entry_index_by_uid', {})


def _izom_propui_free_entry_by_uid(params, uid):
    target_uid = str(uid or '').strip()
    if not target_uid:
        return None
    index_by_uid = _izom_propui_free_entry_index_by_uid(params)
    index = index_by_uid.get(target_uid)
    entries = getattr(params, 'izom_propui_free_entries', None) or []
    if index is not None and 0 <= index < len(entries):
        candidate = entries[index]
        if str(getattr(candidate, 'uid', '') or '').strip() == target_uid:
            return candidate
    for candidate in entries:
        if str(getattr(candidate, 'uid', '') or '').strip() == target_uid:
            return candidate
    return None


def _izom_propui_free_collection_has_items(owner, attr_name):
    try:
        return len(getattr(owner, attr_name, None) or []) > 0
    except (AttributeError, TypeError, ValueError):
        return False


def _izom_propui_free_entry_uses_dynamic_labels(entry):
    return (
        bool(getattr(entry, 'use_bool_state_labels', False))
        or bool(getattr(entry, 'use_value_labels', False))
        or bool(str(getattr(entry, 'bool_label_true', '') or '').strip())
        or bool(str(getattr(entry, 'bool_label_false', '') or '').strip())
        or _izom_propui_free_collection_has_items(entry, 'value_labels')
    )


def _izom_propui_free_entry_uses_display_features(entry):
    prop_type = str(getattr(entry, 'prop_type', '') or '').strip().upper()
    if prop_type == 'TEXT':
        return True
    return (
        bool(getattr(entry, 'alert_style', False))
        or bool(getattr(entry, 'slider', False))
        or str(getattr(entry, 'value_label_layout', 'INLINE') or 'INLINE').strip().upper() != 'INLINE'
        or str(getattr(entry, 'multi_component_layout', 'INLINE') or 'INLINE').strip().upper() != 'INLINE'
        or izom_propui_free_normalize_multi_component_draw_mode(
            getattr(entry, 'multi_component_draw_mode', 'WIDGET')
        ) != 'WIDGET'
    )


def _izom_propui_free_smart_expand_selected_entry_sections_for_entry(params, entry, active_uid):
    uid = str(active_uid or '').strip()
    if not uid:
        _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_smart_expanded_active_uid', '')
        return
    if str(getattr(params, 'izom_propui_free_smart_expanded_active_uid', '') or '').strip() == uid:
        return
    if entry is None:
        _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_smart_expanded_active_uid', '')
        return

    _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_smart_expanded_active_uid', uid)

    prop_type = str(getattr(entry, 'prop_type', '') or '').strip().upper()
    if prop_type != 'TEXT':
        _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_custom_prop_expanded', True)
    if _izom_propui_free_entry_uses_display_features(entry):
        _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_display_expanded', True)
    if _izom_propui_free_entry_uses_dynamic_labels(entry):
        _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_copy_settings_expanded', True)
    if str(getattr(entry, 'parent_uid', '') or '').strip():
        _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_child_behavior_expanded', True)
    if prop_type != 'TEXT' and not bool(getattr(entry, 'library_overridable', True)):
        _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_storage_expanded', True)


def _izom_propui_free_smart_expand_selected_entry_sections(params, active_uid):
    uid = str(active_uid or '').strip()
    if not uid:
        _izom_propui_free_smart_expand_selected_entry_sections_for_entry(params, None, '')
        return
    if str(getattr(params, 'izom_propui_free_smart_expanded_active_uid', '') or '').strip() == uid:
        return
    _izom_propui_free_smart_expand_selected_entry_sections_for_entry(
        params,
        _izom_propui_free_entry_by_uid(params, uid),
        uid,
    )


def _izom_propui_free_set_last_editor_context(params, editor_context):
    mode = str(editor_context or 'HIERARCHY').strip().upper() or 'HIERARCHY'
    try:
        params.izom_propui_free_last_editor_context = mode
    except _IZOM_PROPUI_FREE_SELECTION_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

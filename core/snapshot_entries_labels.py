# SPDX-License-Identifier: GPL-3.0-or-later

from .diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .snapshot_entries_common import (
    IZOM_PROPUI_FREE_VALUE_LABEL_SERIALIZED_FIELDS,
    _IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS,
    _IZOM_PROPUI_FREE_FRESH_ENTRY_ALWAYS_SET_FIELDS,
    _IZOM_PROPUI_FREE_IMPORT_EXCEPTIONS,
    _IZOM_PROPUI_FREE_NUMERIC_EXCEPTIONS,
    _IZOM_PROPUI_FREE_VALUE_LABEL_ARRAY_FIELDS,
    _IZOM_PROPUI_FREE_VALUE_LABEL_RUNTIME_SCALAR_FIELDS,
    _IZOM_PROPUI_FREE_VALUE_LABEL_SERIALIZED_SCALAR_FIELDS,
    _izom_propui_free_ensure_item_uid,
    _izom_propui_free_fresh_entry_default_values,
    _izom_propui_free_snapshot_typed_array_value,
    izom_propui_free_log_recovered,
)
from .collection_sync import (
    _izom_propui_free_sync_uid_collection,
    _izom_propui_free_values_differ,
)
from .text import _izom_propui_free_limit_label_input_text



def _izom_propui_free_runtime_rule_needs_array_values(item):
    try:
        mode = str(getattr(item, 'match_mode', 'GREATER') or 'GREATER').strip().upper()
    except _IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS:
        mode = 'GREATER'
    return mode == 'EQUAL'


def _izom_propui_free_apply_snapshot_fields(owner, field_names, snap, *, assume_fresh=False):
    if assume_fresh:
        default_values = _izom_propui_free_fresh_entry_default_values()
        for name in field_names:
            if name not in snap:
                continue
            new_value = snap[name]
            if name not in _IZOM_PROPUI_FREE_FRESH_ENTRY_ALWAYS_SET_FIELDS:
                default_value = default_values.get(name)
                try:
                    if default_value == new_value:
                        continue
                except _IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS:
                    pass
                if not _izom_propui_free_values_differ(default_value, new_value):
                    continue
            try:
                setattr(owner, name, new_value)
            except _IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS:
                continue
        return

    for name in field_names:
        if name not in snap:
            continue
        new_value = snap[name]
        try:
            current_value = getattr(owner, name)
        except _IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS:
            continue
        if _izom_propui_free_values_differ(current_value, new_value):
            setattr(owner, name, new_value)


def _izom_propui_free_restore_collection_active_index(owner, collection_name, active_attr_name, value):
    try:
        from ..ui.helper_selection import _izom_propui_free_set_collection_active_index_guarded

        _izom_propui_free_set_collection_active_index_guarded(
            owner,
            collection_name,
            active_attr_name,
            value,
            category='Core',
        )
        return
    except _IZOM_PROPUI_FREE_IMPORT_EXCEPTIONS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )

    try:
        if getattr(owner, active_attr_name) == value:
            return
        setattr(owner, active_attr_name, value)
    except _IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )


def _izom_propui_free_restored_collection_active_index(collection, current_active):
    try:
        collection_len = len(collection)
    except _IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS:
        collection_len = 0
    try:
        active_index = max(0, int(current_active or 0))
    except _IZOM_PROPUI_FREE_NUMERIC_EXCEPTIONS:
        active_index = 0
    return min(active_index, max(0, collection_len - 1))


def _izom_propui_free_refresh_restored_collection_state(owner, collection_name, active_attr_name, current_active):
    collection = getattr(owner, collection_name)
    active_index = _izom_propui_free_restored_collection_active_index(collection, current_active)
    try:
        from ..ui.helper_selection import (
            _izom_propui_free_bump_collection_revision,
            _izom_propui_free_set_collection_selection_direct,
        )

        _izom_propui_free_bump_collection_revision(owner, collection_name)
        try:
            active_uid = str(getattr(collection[active_index], 'uid', '') or '').strip() if collection else ''
        except _IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS:
            active_uid = ''
        _izom_propui_free_set_collection_selection_direct(
            owner,
            collection_name,
            [active_uid] if active_uid else [],
            active_uid=active_uid,
            active_index=active_index,
            anchor_uid=active_uid,
        )
        return
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )

    _izom_propui_free_restore_collection_active_index(
        owner,
        collection_name,
        active_attr_name,
        active_index,
    )


def _izom_propui_free_snapshot_value_label(item, *, runtime=False, force_arrays=False):
    field_names = (
        _IZOM_PROPUI_FREE_VALUE_LABEL_RUNTIME_SCALAR_FIELDS
        if runtime else
        _IZOM_PROPUI_FREE_VALUE_LABEL_SERIALIZED_SCALAR_FIELDS
    )
    snap = {name: getattr(item, name) for name in field_names}
    snap['uid'] = _izom_propui_free_ensure_item_uid(item)
    snap['label'] = _izom_propui_free_limit_label_input_text(snap['label'])
    if force_arrays or not runtime or _izom_propui_free_runtime_rule_needs_array_values(item):
        for attr_name, (element_type, default_value) in _IZOM_PROPUI_FREE_VALUE_LABEL_ARRAY_FIELDS.items():
            snap[attr_name] = _izom_propui_free_snapshot_typed_array_value(
                getattr(item, attr_name),
                element_type,
                default_value,
            )
    return snap


def _izom_propui_free_restore_value_labels_collection_full(entry, attr_name, active_attr_name, snapshots):
    collection = getattr(entry, attr_name)
    while collection:
        collection.remove(len(collection) - 1)
    for snap in snapshots:
        item = collection.add()
        for name in IZOM_PROPUI_FREE_VALUE_LABEL_SERIALIZED_FIELDS:
            if name in snap:
                setattr(item, name, snap[name])
    current_active = getattr(entry, active_attr_name, 0)
    _izom_propui_free_refresh_restored_collection_state(
        entry,
        attr_name,
        active_attr_name,
        current_active,
    )


def _izom_propui_free_sync_value_label_item(item, snap):
    _izom_propui_free_apply_snapshot_fields(item, IZOM_PROPUI_FREE_VALUE_LABEL_SERIALIZED_FIELDS, snap)


def _izom_propui_free_restore_value_labels_collection(entry, attr_name, active_attr_name, snapshots):
    collection = getattr(entry, attr_name)
    current_active = getattr(entry, active_attr_name, 0)
    try:
        _izom_propui_free_sync_uid_collection(
            collection,
            snapshots,
            sync_item=_izom_propui_free_sync_value_label_item,
        )
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        _izom_propui_free_restore_value_labels_collection_full(entry, attr_name, active_attr_name, snapshots)
        return
    _izom_propui_free_refresh_restored_collection_state(
        entry,
        attr_name,
        active_attr_name,
        current_active,
    )


def _izom_propui_free_restore_value_labels(entry, snapshots):
    _izom_propui_free_restore_value_labels_collection(
        entry,
        'value_labels',
        'value_labels_active_index',
        snapshots,
    )

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

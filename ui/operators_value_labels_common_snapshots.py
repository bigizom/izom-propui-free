# SPDX-License-Identifier: GPL-3.0-or-later


def _izom_propui_free_value_label_fields_for_item(item):
    return IZOM_PROPUI_FREE_VALUE_LABEL_SERIALIZED_FIELDS


def _izom_propui_free_snapshot_value_label_field(item, name):
    value = getattr(item, name, None)
    if str(name or '').endswith('_array'):
        try:
            return tuple(value)
        except TypeError:
            return value
    return value


def _izom_propui_free_snapshot_value_label_item(item):
    fields = _izom_propui_free_value_label_fields_for_item(item)
    snap = {name: _izom_propui_free_snapshot_value_label_field(item, name) for name in fields}
    if not snap.get('uid'):
        snap['uid'] = _izom_propui_free_new_uid()
    return snap


def _izom_propui_free_restore_value_label_item(collection, snapshot, *, params=None):
    item = collection.add()
    fields = _izom_propui_free_value_label_fields_for_item(item)
    guard_key = _izom_propui_free_suspend_entry_updates(params) if params is not None else None
    try:
        for name in fields:
            if name in snapshot:
                setattr(item, name, snapshot[name])
    finally:
        if guard_key is not None:
            _izom_propui_free_resume_entry_updates(params)
    return item


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401
from ..core.constants_serialized import (
    IZOM_PROPUI_FREE_VALUE_LABEL_SERIALIZED_FIELDS,
)
from ..core.entry_ids import _izom_propui_free_new_uid
from .helper_cache_updates_entry_params import (
    _izom_propui_free_resume_entry_updates,
    _izom_propui_free_suspend_entry_updates,
)


__all__ = izom_propui_free_public_names(globals(), all_public=True)

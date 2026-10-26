# SPDX-License-Identifier: GPL-3.0-or-later

from .diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .snapshot_entries_labels import (
    _IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS,
    _izom_propui_free_apply_snapshot_fields,
    _izom_propui_free_restore_value_labels,
    _izom_propui_free_values_differ,
    izom_propui_free_log_recovered,
)
from .constants_serialized import IZOM_PROPUI_FREE_ENTRY_SERIALIZED_FIELDS



def _izom_propui_free_apply_entry_snapshot(item, snap, *, assume_fresh=False):
    _izom_propui_free_apply_snapshot_fields(
        item,
        IZOM_PROPUI_FREE_ENTRY_SERIALIZED_FIELDS,
        snap,
        assume_fresh=bool(assume_fresh),
    )
    try:
        from .text import izom_propui_free_entry_display_name
        item.name = izom_propui_free_entry_display_name(
            item,
            fallback_index=int(getattr(item, 'ui_order', 1) or 1),
        )
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )

    try:
        target_cached_subtype = getattr(item, 'float_array_subtype', 'NONE')
        if target_cached_subtype != 'NONE' and assume_fresh:
            item.float_array_subtype_cached = target_cached_subtype
        else:
            current_cached_subtype = getattr(item, 'float_array_subtype_cached', 'NONE')
            if _izom_propui_free_values_differ(current_cached_subtype, target_cached_subtype):
                item.float_array_subtype_cached = target_cached_subtype
    except _IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )

    value_labels = snap.get('value_labels') or []
    if value_labels or len(getattr(item, 'value_labels', []) or []):
        _izom_propui_free_restore_value_labels(item, value_labels)

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

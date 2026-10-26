# SPDX-License-Identifier: GPL-3.0-or-later

from .diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .runtime_ui_kwargs import (
    izom_propui_free_log_recovered,
)
from .entry_normalization import _izom_propui_free_disable_slider_for_soft_limits
from .snapshot_entries_runtime import izom_propui_free_snapshot_entries
from .snapshot_tree import _izom_propui_free_build_state_from_snapshots
from .value_access_common import (
    izom_propui_free_is_numeric_value_kind,
    izom_propui_free_normalize_value_kind,
)
from .value_access_entries import (
    izom_propui_free_entry_value_kind,
    izom_propui_free_is_managed_entry,
)
from .value_labels_runtime import _izom_propui_free_value_labels_runtime


def _izom_propui_free_runtime_entries_from_snapshot_state(snapshots, state):
    full_by_uid = {}
    for s in snapshots:
        uid = str(s.get('uid', '') or '').strip()
        if uid:
            full_by_uid[uid] = s

    runtime = []
    for index, snap in enumerate(state['snapshots'], start=1):
        uid = snap['uid']
        full_snap = full_by_uid.get(uid)
        if full_snap is not None:
            entry = dict(full_snap)
            entry['parent_uid'] = snap.get('parent_uid', entry.get('parent_uid', ''))
        else:
            entry = dict(snap)
        entry['tree_index'] = index
        entry['depth'] = state['depth_by_uid'][uid]
        entry['has_children'] = uid in state['children_by_uid']
        entry['_value_access_memo_token'] = (entry.get('uid', ''), index, id(entry))
        entry['value_kind'] = izom_propui_free_entry_value_kind(entry, 'FLOAT')
        _izom_propui_free_disable_slider_for_soft_limits(entry)
        entry['is_managed_entry'] = izom_propui_free_is_managed_entry(entry)
        value_kind = izom_propui_free_normalize_value_kind(entry.get('value_kind', 'FLOAT'), 'FLOAT')
        if izom_propui_free_is_numeric_value_kind(value_kind) and not bool(entry.get('use_value_labels', False)):
            entry['value_labels'] = []
        elif value_kind == 'BOOL' and not bool(entry.get('use_bool_state_labels', False)):
            entry['bool_label_true'] = ''
            entry['bool_label_false'] = ''

        runtime.append(entry)

    runtime_lookup = {entry['uid']: entry for entry in runtime}
    for entry in runtime:
        entry['_runtime_entry_lookup'] = runtime_lookup

    for entry in runtime:
        prop_type = str(entry.get('prop_type', 'FLOAT') or 'FLOAT')
        value_kind = izom_propui_free_normalize_value_kind(entry.get('value_kind', prop_type), prop_type)

        if izom_propui_free_is_numeric_value_kind(value_kind) or value_kind in {'COLOR', 'VECTOR', 'INT_ARRAY', 'BOOL_ARRAY'}:
            if bool(entry.get('use_value_labels', False)):
                entry['value_labels'] = _izom_propui_free_value_labels_runtime(entry, 'value_labels', prop_type=value_kind)
            else:
                entry['value_labels'] = []
        elif prop_type == 'TEXT':
            entry['value_labels'] = []
        else:
            entry['value_labels'] = []

    return runtime

def izom_propui_free_runtime_entries(params):
    if params is not None:
        try:
            from .cache import (
                izom_propui_free_cached_runtime_entries,
            )

            return izom_propui_free_cached_runtime_entries(params)
        except ImportError:
            pass
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            # Fall back to the standalone builder. This keeps the public runtime
            # API usable during unusual import/bootstrap moments before the
            # shared cache module is fully ready.
            izom_propui_free_log_recovered(category='Core', exception=exc)
            pass
    snapshots = izom_propui_free_snapshot_entries(params, limit_strings=False)
    state = _izom_propui_free_build_state_from_snapshots(snapshots)
    return _izom_propui_free_runtime_entries_from_snapshot_state(
        snapshots,
        state,
    )

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

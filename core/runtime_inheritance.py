# SPDX-License-Identifier: GPL-3.0-or-later

from .diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .runtime_common import (
    _izom_propui_free_build_state_from_snapshots,
    _izom_propui_free_clamp_visibility_inheritance_depth,
    _izom_propui_free_entry_ancestor_chain_from_state,
    _izom_propui_free_entry_value,
    izom_propui_free_log_recovered,
    izom_propui_free_snapshot_entries,
)

def _izom_propui_free_inheritance_scope(params, entry, *, depth_field, state=None, layout_entry_uids=None):
    if entry is None:
        return {
            'requested_depth': 1,
            'available_depth': 0,
            'selected_depth': 1,
            'applied_depth': 0,
            'raw_ancestors': [],
            'usable_ancestors': [],
            'applied_ancestors': [],
        }

    if state is None and params is not None:
        state = _izom_propui_free_build_state_from_snapshots(
            izom_propui_free_snapshot_entries(params, limit_strings=False)
        )

    entry_uid = str(_izom_propui_free_entry_value(entry, 'uid', '') or '').strip()
    try:
        requested_depth = max(1, int(_izom_propui_free_entry_value(entry, depth_field, 1) or 1))
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        requested_depth = 1

    raw_ancestors = _izom_propui_free_entry_ancestor_chain_from_state(state, entry_uid) if state is not None else []

    usable_ancestors = []
    allowed_uids = None
    if layout_entry_uids is not None:
        allowed_uids = {
            str(uid or '').strip()
            for uid in layout_entry_uids
            if str(uid or '').strip()
        }

    for ancestor in raw_ancestors:
        ancestor_uid = str(_izom_propui_free_entry_value(ancestor, 'uid', '') or '').strip()
        if allowed_uids is not None and ancestor_uid not in allowed_uids:
            break
        usable_ancestors.append(ancestor)

    available_depth = len(usable_ancestors)
    if available_depth > 0:
        selected_depth = _izom_propui_free_clamp_visibility_inheritance_depth(requested_depth, available_depth)
        applied_depth = selected_depth
    else:
        selected_depth = 1
        applied_depth = 0

    return {
        'requested_depth': requested_depth,
        'available_depth': available_depth,
        'selected_depth': selected_depth,
        'applied_depth': applied_depth,
        'raw_ancestors': raw_ancestors,
        'usable_ancestors': usable_ancestors,
        'applied_ancestors': usable_ancestors[:applied_depth],
    }

def _izom_propui_free_visibility_inheritance_scope(params, entry, *, state=None, layout_entry_uids=None):
    return _izom_propui_free_inheritance_scope(
        params, entry,
        depth_field='visibility_inheritance_depth',
        state=state, layout_entry_uids=layout_entry_uids,
    )

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

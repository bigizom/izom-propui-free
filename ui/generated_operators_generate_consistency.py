# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from ..core.diagnostics import izom_propui_free_log_recovered
from ..core.snapshot_entries_consistency import (
    izom_propui_free_ensure_consistency,
)

def _izom_propui_free_generate_needs_full_consistency(params):
    entries = getattr(params, 'izom_propui_free_entries', None) or []
    layout_items = getattr(params, 'izom_propui_free_layout_items', None) or []

    entry_uids = set()
    syncable_prop_ids = set()
    parent_uids = []
    for entry in entries:
        uid = str(getattr(entry, 'uid', '') or '').strip()
        if not uid or uid in entry_uids:
            return True
        entry_uids.add(uid)
        parent_uid = str(getattr(entry, 'parent_uid', '') or '').strip()
        if parent_uid:
            parent_uids.append(parent_uid)
        prop_type = str(getattr(entry, 'prop_type', 'FLOAT') or 'FLOAT').strip().upper()
        if prop_type != 'TEXT':
            prop_id = str(getattr(entry, 'prop_id', '') or '').strip()
            if not prop_id or prop_id in syncable_prop_ids:
                return True
            syncable_prop_ids.add(prop_id)
    if any(parent_uid not in entry_uids for parent_uid in parent_uids):
        return True

    layout_uids = set()
    for item in layout_items:
        uid = str(getattr(item, 'uid', '') or '').strip()
        entry_uid = str(getattr(item, 'entry_uid', '') or '').strip()
        if not uid or uid in layout_uids:
            return True
        if not entry_uid or entry_uid not in entry_uids:
            return True
        layout_uids.add(uid)
    return False


def _izom_propui_free_ensure_generate_consistency(params):
    try:
        needs_full_consistency = _izom_propui_free_generate_needs_full_consistency(params)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(category='Generated UI', exception=exc)
        needs_full_consistency = True
    if needs_full_consistency:
        izom_propui_free_ensure_consistency(params)



from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .helper_layout_selection import (
    _izom_propui_free_uid_list_from_json,
    izom_propui_free_log_recovered,
)
from ..core.cache_common import (
    _izom_propui_free_cached_params_field,
    _izom_propui_free_cached_uid_json_list,
)
from ..core.snapshot_layout_common import (
    _izom_propui_free_layout_row_field_values,
)
from ..core.snapshot_layout_ensure import (
    _izom_propui_free_layout_view_row_uid,
)
from .helper_cache_updates_invalidation import _izom_propui_free_invalidate_cache_fields
from .helper_selection_common import (
    _izom_propui_free_data_value,
    _izom_propui_free_store_uid_list,
)



def _izom_propui_free_row_slot_value(data):
    try:
        return max(1, min(3, int(_izom_propui_free_data_value(data, 'row_slot', 1) or 1)))
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        return 1


def _izom_propui_free_ordered_layout_snapshots(layout_snapshots):
    ordered = []
    for index, snap in enumerate(layout_snapshots or []):
        if isinstance(snap, dict):
            item = {
                'uid': str(snap.get('uid', '') or '').strip(),
                'entry_uid': str(snap.get('entry_uid', '') or '').strip(),
                'row_index': max(1, int(snap.get('row_index', 1) or 1)),
                'column_index': max(1, min(3, int(snap.get('column_index', 1) or 1))),
                **_izom_propui_free_layout_row_field_values(snap),
            }
        else:
            item = {
                'uid': str(_izom_propui_free_data_value(snap, 'uid', '') or '').strip(),
                'entry_uid': str(_izom_propui_free_data_value(snap, 'entry_uid', '') or '').strip(),
                'row_index': max(1, int(_izom_propui_free_data_value(snap, 'row_index', 1) or 1)),
                'column_index': max(1, min(3, int(_izom_propui_free_data_value(snap, 'column_index', 1) or 1))),
                **_izom_propui_free_layout_row_field_values({
                    'row_height_scale': _izom_propui_free_data_value(snap, 'row_height_scale', 1.0),
                    'row_inset_left_enabled': _izom_propui_free_data_value(snap, 'row_inset_left_enabled', False),
                    'row_inset_left_amount': _izom_propui_free_data_value(snap, 'row_inset_left_amount', 1.0),
                }),
            }
        item['_order'] = index
        if item['uid'] and item['entry_uid']:
            ordered.append(item)
    ordered.sort(
        key=lambda item: (
            int(item.get('row_index', 1) or 1),
            int(item.get('column_index', 1) or 1),
            int(item.get('_order', 0) or 0),
        )
    )
    return ordered


def _izom_propui_free_normalize_layout_view_uid(view_uid):
    target_uid = str(view_uid or '').strip()
    if not target_uid.startswith('ROW_HEADER:'):
        return target_uid
    suffix = target_uid[len('ROW_HEADER:'):]
    if not suffix or '|' not in suffix:
        return target_uid
    members = [member for member in suffix.split('|') if str(member or '').strip()]
    return _izom_propui_free_layout_view_row_uid(members)


def _izom_propui_free_layout_view_row_member_uids(view_item):
    return _izom_propui_free_uid_list_from_json(getattr(view_item, 'row_member_uids_json', '[]'))


def _izom_propui_free_layout_collapsed_row_uids(params):
    if params is None:
        return []
    raw_collapsed = _izom_propui_free_cached_params_field(
        params,
        'layout_collapsed_row_uids',
        lambda: _izom_propui_free_cached_uid_json_list(
            getattr(params, 'izom_propui_free_layout_collapsed_row_uids_json', '[]')
        ),
    )
    collapsed = []
    seen = set()
    for uid in raw_collapsed:
        normalized_uid = _izom_propui_free_normalize_layout_view_uid(uid)
        if not normalized_uid or normalized_uid in seen:
            continue
        seen.add(normalized_uid)
        collapsed.append(normalized_uid)
    return collapsed


def _izom_propui_free_set_layout_collapsed_row_uids(params, row_uids):
    if params is None:
        return []
    normalized = [_izom_propui_free_normalize_layout_view_uid(uid) for uid in (row_uids or [])]
    stored = _izom_propui_free_store_uid_list(params, 'izom_propui_free_layout_collapsed_row_uids_json', normalized)
    _izom_propui_free_invalidate_cache_fields(params, 'layout_collapsed_row_uids')
    return stored


def _izom_propui_free_layout_row_group_collapsed(params, row_uid):
    target_uid = _izom_propui_free_normalize_layout_view_uid(row_uid)
    return bool(target_uid) and target_uid in set(_izom_propui_free_layout_collapsed_row_uids(params))


def _izom_propui_free_toggle_layout_row_group_collapsed(params, row_uid):
    target_uid = _izom_propui_free_normalize_layout_view_uid(row_uid)
    if not target_uid:
        return False
    collapsed = _izom_propui_free_layout_collapsed_row_uids(params)
    collapsed_set = set(collapsed)
    if target_uid in collapsed_set:
        collapsed = [uid for uid in collapsed if uid != target_uid]
        new_state = False
    else:
        collapsed.append(target_uid)
        new_state = True
    _izom_propui_free_set_layout_collapsed_row_uids(params, collapsed)
    return new_state

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

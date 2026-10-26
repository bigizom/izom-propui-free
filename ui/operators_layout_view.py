# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from types import SimpleNamespace

from .operators_layout_base import (
    _izom_propui_free_layout_visible_snapshots,
    _izom_propui_free_rows_by_layout_container,
)
from ..core.cache_layout import izom_propui_free_cached_layout_item_lookup
from ..core.collection_sync import (
    _izom_propui_free_collection_clear,
    _izom_propui_free_collection_order_matches,
    _izom_propui_free_sync_uid_collection,
    _izom_propui_free_values_differ,
)
from ..core.diagnostics import izom_propui_free_log_recovered
from ..core.snapshot_layout_ensure import (
    _izom_propui_free_layout_view_entry_uid,
    _izom_propui_free_layout_view_row_uid,
)
from .helper_layout_common import _IZOM_PROPUI_FREE_LAYOUT_VIEW_STATE_CACHE
from .helper_layout_containers import (
    _izom_propui_free_prune_layout_collapsed_row_uids,
)
from .helper_layout_rows import (
    _izom_propui_free_layout_collapsed_row_uids,
    _izom_propui_free_layout_view_row_member_uids,
    _izom_propui_free_normalize_layout_view_uid,
)
from .helper_layout_view import (
    _izom_propui_free_layout_view_item_by_uid,
    _izom_propui_free_layout_view_state,
)
from .helper_selection_common import (
    _izom_propui_free_json_dumps,
    _izom_propui_free_set_attr_if_changed,
    _izom_propui_free_uid_list_from_json,
)
from .helper_selection_context import (
    _izom_propui_free_resume_list_context_updates,
    _izom_propui_free_suspend_list_context_updates,
)



def _emit_layout_rows_for_container(view_snapshots, snapshot_by_uid, rows, collapsed_row_uids, ui_order):
    for row in rows or ():
        member_uids = list(row or ())
        if not member_uids:
            continue
        first_snap = snapshot_by_uid.get(member_uids[0], {})
        try:
            row_index = max(1, int(first_snap.get('row_index', 1) or 1))
        except (TypeError, ValueError):
            row_index = 1
        header_uid = ''
        if len(member_uids) >= 2:
            header_uid = _izom_propui_free_layout_view_row_uid(member_uids)
            row_member_uids_json = _izom_propui_free_json_dumps(member_uids)
            view_snapshots.append({
                'uid': header_uid,
                'kind': 'ROW_HEADER',
                'layout_uid': '',
                'entry_uid': '',
                'parent_uid': '',
                'row_index': row_index,
                'column_index': 1,
                'row_member_uids_json': row_member_uids_json,
                'ui_order': ui_order,
            })
            ui_order += 1
        row_collapsed = bool(header_uid and header_uid in collapsed_row_uids)
        for column_index, layout_uid in enumerate(member_uids, start=1):
            if row_collapsed:
                continue
            snap = snapshot_by_uid.get(layout_uid, {})
            view_snapshots.append({
                'uid': _izom_propui_free_layout_view_entry_uid(layout_uid),
                'kind': 'ENTRY_ITEM',
                'layout_uid': layout_uid,
                'entry_uid': str(snap.get('entry_uid', '') or '').strip(),
                'parent_uid': header_uid,
                'row_index': row_index,
                'column_index': column_index,
                # Only row headers need the full member payload.
                'row_member_uids_json': '[]',
                'ui_order': ui_order,
            })
            ui_order += 1
    return ui_order

def _izom_propui_free_build_layout_view_snapshots(
    params,
    layout_snapshots=None,
    *,
    layout_snapshots_are_ordered=False,
):
    visible_snapshots = _izom_propui_free_layout_visible_snapshots(
        params,
        layout_snapshots,
        snapshots_are_ordered=bool(layout_snapshots_are_ordered),
    )
    view_snapshots = []
    previous_row_index = 0
    fast_single_rows = True
    for ui_order, snap in enumerate(visible_snapshots, start=1):
        layout_uid = str(snap.get('uid', '') or '').strip()
        try:
            row_index = max(1, int(snap.get('row_index', 1) or 1))
            column_index = max(1, int(snap.get('column_index', 1) or 1))
        except (TypeError, ValueError):
            fast_single_rows = False
            break
        if (
            not layout_uid
            or column_index != 1
            or row_index <= previous_row_index
        ):
            fast_single_rows = False
            break
        previous_row_index = row_index
        view_snapshots.append({
            'uid': _izom_propui_free_layout_view_entry_uid(layout_uid),
            'kind': 'ENTRY_ITEM',
            'layout_uid': layout_uid,
            'entry_uid': str(snap.get('entry_uid', '') or '').strip(),
            'parent_uid': '',
            'row_index': row_index,
            'column_index': 1,
            'row_member_uids_json': '[]',
            'ui_order': ui_order,
        })
    if fast_single_rows:
        return view_snapshots

    snapshot_by_uid = {
        str(snap.get('uid', '') or '').strip(): snap
        for snap in visible_snapshots
        if str(snap.get('uid', '') or '').strip()
    }
    rows_by_container = _izom_propui_free_rows_by_layout_container(visible_snapshots, snapshot_by_uid)
    collapsed_row_uids = set(_izom_propui_free_layout_collapsed_row_uids(params))
    view_snapshots = []
    ui_order = 1
    ui_order = _emit_layout_rows_for_container(
        view_snapshots,
        snapshot_by_uid,
        rows_by_container.get('', ()),
        collapsed_row_uids,
        ui_order,
    )
    return view_snapshots

def _izom_propui_free_set_raw_layout_item_selection(params, layout_uid):
    target_uid = str(layout_uid or '').strip()
    layout_lookup = izom_propui_free_cached_layout_item_lookup(params) if params is not None else {}
    order = list(layout_lookup.get('ordered_uids', ()))
    if target_uid not in order:
        target_uid = order[0] if order else ''
    active_index = int(layout_lookup.get('index_by_uid', {}).get(target_uid, 0) or 0)
    _izom_propui_free_suspend_list_context_updates(params)
    try:
        _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_active_index', active_index)
        _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_active_uid', target_uid)
        _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_selected_uids_json', _izom_propui_free_json_dumps([target_uid] if target_uid else []))
        _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_selection_anchor_uid', target_uid)
    finally:
        _izom_propui_free_resume_list_context_updates(params)
    return target_uid

def _izom_propui_free_sync_layout_view_selection(params, *, preferred_active_uid=None, preferred_active_index=None, persist=True):
    if params is None:
        return []
    view_state = _izom_propui_free_layout_view_state(params)
    by_uid = view_state.get('by_uid', {}) or {}
    raw_uids = list(view_state.get('raw_uids', ()) or ())
    order = [
        uid for uid in raw_uids
        if str(getattr(by_uid.get(uid), 'kind', '') or '').strip() != 'DIVIDER'
    ]
    if not order:
        if persist:
            _izom_propui_free_suspend_list_context_updates(params)
            try:
                _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_view_active_index', 0)
                _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_view_active_uid', '')
                _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_view_selected_uids_json', '[]')
                _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_view_selection_anchor_uid', '')
            finally:
                _izom_propui_free_resume_list_context_updates(params)
        _izom_propui_free_set_raw_layout_item_selection(params, '')
        return []

    plain_index_selection = preferred_active_index is not None and preferred_active_uid is None
    selected = _izom_propui_free_uid_list_from_json(getattr(params, 'izom_propui_free_layout_view_selected_uids_json', '[]'))
    selected = [_izom_propui_free_normalize_layout_view_uid(uid) for uid in selected]
    selected = [uid for uid in selected if uid in order]

    def _selectable_uid_from_collection_index(index_value):
        try:
            index = max(0, min(int(index_value), len(raw_uids) - 1))
        except (TypeError, ValueError):
            index = 0
        if not raw_uids:
            return ''
        candidate = _izom_propui_free_normalize_layout_view_uid(raw_uids[index])
        if candidate in order:
            return candidate
        for offset in range(index + 1, len(raw_uids)):
            candidate = _izom_propui_free_normalize_layout_view_uid(raw_uids[offset])
            if candidate in order:
                return candidate
        for offset in range(index - 1, -1, -1):
            candidate = _izom_propui_free_normalize_layout_view_uid(raw_uids[offset])
            if candidate in order:
                return candidate
        return ''

    target_uid = _izom_propui_free_normalize_layout_view_uid(preferred_active_uid)
    if not target_uid and preferred_active_index is not None:
        target_uid = _selectable_uid_from_collection_index(preferred_active_index)
    if not target_uid:
        target_uid = _izom_propui_free_normalize_layout_view_uid(getattr(params, 'izom_propui_free_layout_view_active_uid', ''))
        if target_uid not in order:
            target_uid = ''
    if not target_uid and selected:
        target_uid = selected[-1]
    if not target_uid and order:
        target_uid = _selectable_uid_from_collection_index(
            getattr(params, 'izom_propui_free_layout_view_active_index', 0)
        )
    if target_uid not in order:
        target_uid = selected[0] if selected else order[0]
    if plain_index_selection and target_uid:
        selected = [target_uid]
    elif not selected and target_uid:
        selected = [target_uid]
    elif target_uid and target_uid not in selected:
        selected = [target_uid]
    active_index = int(view_state.get('collection_index_by_uid', {}).get(target_uid, 0) or 0)
    anchor_uid = _izom_propui_free_normalize_layout_view_uid(getattr(params, 'izom_propui_free_layout_view_selection_anchor_uid', ''))
    if plain_index_selection and target_uid:
        anchor_uid = target_uid
    if anchor_uid not in order:
        anchor_uid = selected[0] if selected else target_uid

    if persist:
        active_view_item = _izom_propui_free_layout_view_item_by_uid(params, target_uid)
        layout_uid = ''
        if active_view_item is not None:
            if str(getattr(active_view_item, 'kind', '') or '').strip() == 'ENTRY_ITEM':
                layout_uid = str(getattr(active_view_item, 'layout_uid', '') or '').strip()
            else:
                row_members = _izom_propui_free_layout_view_row_member_uids(active_view_item)
                layout_uid = row_members[0] if row_members else ''
        _izom_propui_free_set_raw_layout_item_selection(params, layout_uid)
        _izom_propui_free_suspend_list_context_updates(params)
        try:
            _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_view_active_index', active_index)
            _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_view_active_uid', target_uid)
            _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_view_selected_uids_json', _izom_propui_free_json_dumps(selected))
            _izom_propui_free_set_attr_if_changed(params, 'izom_propui_free_layout_view_selection_anchor_uid', anchor_uid)
        finally:
            _izom_propui_free_resume_list_context_updates(params)
    return selected

def _izom_propui_free_restore_layout_view_items_full(
    params,
    view_snapshots,
    *,
    active_view_uid='',
    return_snapshots=True,
    sync_selection=True,
):
    collection = getattr(params, 'izom_propui_free_layout_view_items', None)
    if collection is None:
        return []
    _izom_propui_free_suspend_list_context_updates(params)
    try:
        _izom_propui_free_collection_clear(collection)

        resolved = [] if return_snapshots else None
        for index, snap in enumerate(view_snapshots or [], start=1):
            if hasattr(collection, 'add') and not isinstance(collection, list):
                item = collection.add()
            else:
                item = SimpleNamespace()
                collection.append(item)
            item.uid = str(snap.get('uid', '') or '').strip()
            item.kind = str(snap.get('kind', 'ENTRY_ITEM') or 'ENTRY_ITEM')
            item.layout_uid = str(snap.get('layout_uid', '') or '').strip()
            item.entry_uid = str(snap.get('entry_uid', '') or '').strip()
            item.parent_uid = str(snap.get('parent_uid', '') or '').strip()
            item.row_index = max(1, int(snap.get('row_index', 1) or 1))
            item.column_index = max(1, int(snap.get('column_index', 1) or 1))
            item.row_member_uids_json = str(snap.get('row_member_uids_json', '[]') or '[]')
            item.ui_order = max(1, int(snap.get('ui_order', index) or index))
            if resolved is not None:
                resolved.append({
                    'uid': item.uid,
                    'kind': item.kind,
                    'layout_uid': item.layout_uid,
                    'entry_uid': item.entry_uid,
                    'parent_uid': item.parent_uid,
                    'row_index': item.row_index,
                    'column_index': item.column_index,
                    'row_member_uids_json': item.row_member_uids_json,
                    'ui_order': item.ui_order,
                })

        _IZOM_PROPUI_FREE_LAYOUT_VIEW_STATE_CACHE.clear()
        if bool(sync_selection):
            preferred_uid = str(active_view_uid or getattr(params, 'izom_propui_free_layout_view_active_uid', '') or '').strip()
            _izom_propui_free_sync_layout_view_selection(params, preferred_active_uid=preferred_uid or None)
    finally:
        _izom_propui_free_resume_list_context_updates(params)
    return resolved if resolved is not None else []

def _izom_propui_free_apply_layout_view_snapshot_item(item, snap):
    item_uid = str(snap.get('uid', '') or '').strip()
    try:
        existing_uid = str(getattr(item, 'uid', '') or '').strip()
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        existing_uid = ''
    if not existing_uid:
        item.uid = item_uid
        item.kind = str(snap.get('kind', 'ENTRY_ITEM') or 'ENTRY_ITEM')
        item.layout_uid = str(snap.get('layout_uid', '') or '').strip()
        item.entry_uid = str(snap.get('entry_uid', '') or '').strip()
        item.parent_uid = str(snap.get('parent_uid', '') or '').strip()
        item.row_index = max(1, int(snap.get('row_index', 1) or 1))
        item.column_index = max(1, int(snap.get('column_index', 1) or 1))
        item.row_member_uids_json = str(snap.get('row_member_uids_json', '[]') or '[]')
        item.ui_order = max(1, int(snap.get('ui_order', 1) or 1))
        return
    for attr_name, new_value in (
        ('uid', item_uid),
        ('kind', str(snap.get('kind', 'ENTRY_ITEM') or 'ENTRY_ITEM')),
        ('layout_uid', str(snap.get('layout_uid', '') or '').strip()),
        ('entry_uid', str(snap.get('entry_uid', '') or '').strip()),
        ('parent_uid', str(snap.get('parent_uid', '') or '').strip()),
        ('row_index', max(1, int(snap.get('row_index', 1) or 1))),
        ('column_index', max(1, int(snap.get('column_index', 1) or 1))),
        ('row_member_uids_json', str(snap.get('row_member_uids_json', '[]') or '[]')),
        ('ui_order', max(1, int(snap.get('ui_order', 1) or 1))),
    ):
        try:
            current_value = getattr(item, attr_name)
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            continue
        if _izom_propui_free_values_differ(current_value, new_value):
            setattr(item, attr_name, new_value)

def _izom_propui_free_resolved_layout_view_item_snapshot(item, fallback_order):
    return {
        'uid': str(getattr(item, 'uid', '') or '').strip(),
        'kind': str(getattr(item, 'kind', 'ENTRY_ITEM') or 'ENTRY_ITEM'),
        'layout_uid': str(getattr(item, 'layout_uid', '') or '').strip(),
        'entry_uid': str(getattr(item, 'entry_uid', '') or '').strip(),
        'parent_uid': str(getattr(item, 'parent_uid', '') or '').strip(),
        'row_index': max(1, int(getattr(item, 'row_index', 1) or 1)),
        'column_index': max(1, int(getattr(item, 'column_index', 1) or 1)),
        'row_member_uids_json': str(getattr(item, 'row_member_uids_json', '[]') or '[]'),
        'ui_order': max(1, int(getattr(item, 'ui_order', fallback_order) or fallback_order)),
    }

def _izom_propui_free_restore_layout_view_items_incremental(
    params,
    view_snapshots,
    *,
    active_view_uid='',
    return_snapshots=True,
    sync_selection=True,
):
    collection = getattr(params, 'izom_propui_free_layout_view_items', None)
    if collection is None:
        return []

    target_uids = [
        str((snap or {}).get('uid', '') or '').strip()
        for snap in (view_snapshots or ())
        if str((snap or {}).get('uid', '') or '').strip()
    ]
    current_uids = [
        str(getattr(item, 'uid', '') or '').strip()
        for item in (collection or ())
        if str(getattr(item, 'uid', '') or '').strip()
    ]
    if len(target_uids) >= 128:
        return _izom_propui_free_restore_layout_view_items_full(
            params,
            view_snapshots,
            active_view_uid=active_view_uid,
            return_snapshots=return_snapshots,
            sync_selection=sync_selection,
        )
    fallback_required = False
    resolved = []
    _izom_propui_free_suspend_list_context_updates(params)
    try:
        try:
            _izom_propui_free_sync_uid_collection(
                collection,
                view_snapshots,
                sync_item=_izom_propui_free_apply_layout_view_snapshot_item,
            )
            if not _izom_propui_free_collection_order_matches(collection, view_snapshots):
                raise RuntimeError("layout view incremental restore order mismatch")
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            fallback_required = True

        if not fallback_required:
            if return_snapshots:
                for index, item in enumerate(collection, start=1):
                    resolved.append(_izom_propui_free_resolved_layout_view_item_snapshot(item, index))
            _IZOM_PROPUI_FREE_LAYOUT_VIEW_STATE_CACHE.clear()
            if bool(sync_selection):
                preferred_uid = str(active_view_uid or getattr(params, 'izom_propui_free_layout_view_active_uid', '') or '').strip()
                _izom_propui_free_sync_layout_view_selection(params, preferred_active_uid=preferred_uid or None)
    finally:
        _izom_propui_free_resume_list_context_updates(params)

    if fallback_required:
        return _izom_propui_free_restore_layout_view_items_full(
            params,
            view_snapshots,
            active_view_uid=active_view_uid,
            return_snapshots=return_snapshots,
            sync_selection=sync_selection,
        )
    return resolved

def _izom_propui_free_restore_layout_view_items(
    params,
    view_snapshots,
    *,
    active_view_uid='',
    return_snapshots=True,
    sync_selection=True,
):
    return _izom_propui_free_restore_layout_view_items_incremental(
        params,
        view_snapshots,
        active_view_uid=active_view_uid,
        return_snapshots=return_snapshots,
        sync_selection=sync_selection,
    )

def _izom_propui_free_rebuild_layout_view_items(
    params,
    *,
    preferred_active_uid='',
    layout_snapshots=None,
    layout_snapshots_are_ordered=False,
    return_snapshots=False,
    sync_selection=True,
):
    if params is None or not hasattr(params, 'izom_propui_free_layout_view_items'):
        return []
    view_snapshots = _izom_propui_free_build_layout_view_snapshots(
        params,
        layout_snapshots=layout_snapshots,
        layout_snapshots_are_ordered=layout_snapshots_are_ordered,
    )
    valid_row_uids = [
        str(snap.get('uid', '') or '').strip()
        for snap in view_snapshots
        if str(snap.get('kind', '') or '').strip() == 'ROW_HEADER'
    ]
    _izom_propui_free_prune_layout_collapsed_row_uids(params, valid_row_uids)
    return _izom_propui_free_restore_layout_view_items(
        params,
        view_snapshots,
        active_view_uid=preferred_active_uid,
        return_snapshots=return_snapshots,
        sync_selection=sync_selection,
    )


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

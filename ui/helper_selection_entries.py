# SPDX-License-Identifier: GPL-3.0-or-later

from .helper_selection_context import (
    _izom_propui_free_clicked_list_context_for_editor,
    _izom_propui_free_resume_list_context_updates,
    _izom_propui_free_set_last_clicked_list_context,
    _izom_propui_free_suspend_list_context_updates,
    izom_propui_free_log_recovered,
)
from .helper_layout_lookup import (
    _izom_propui_free_layout_item_by_entry_uid,
    _izom_propui_free_layout_item_by_uid,
)
from .helper_layout_rows import (
    _izom_propui_free_layout_view_row_member_uids,
)
from .helper_layout_selection import (
    _izom_propui_free_entry_order_for_editor,
    _izom_propui_free_set_layout_selection,
)
from .helper_layout_view import (
    _izom_propui_free_active_layout_view_item,
    _izom_propui_free_layout_view_item_by_uid,
)
from ..core.cache_state import izom_propui_free_cached_entry_navigation_bundle
from .helper_selection_common import (
    _izom_propui_free_entry_index_by_uid,
    _izom_propui_free_set_attr_if_changed,
    _izom_propui_free_set_last_editor_context,
    _izom_propui_free_smart_expand_selected_entry_sections,
    _izom_propui_free_store_uid_list,
    _izom_propui_free_uid_list_from_json,
)



def _izom_propui_free_editor_selection_fields(editor_context='HIERARCHY'):
    mode = str(editor_context or 'HIERARCHY').strip().upper()
    if mode == 'LAYOUT':
        return (
            'izom_propui_free_layout_active_index',
            'izom_propui_free_layout_active_uid',
            'izom_propui_free_layout_selected_uids_json',
            'izom_propui_free_layout_selection_anchor_uid',
        )
    return (
        'izom_propui_free_active_index',
        'izom_propui_free_active_uid',
        'izom_propui_free_selected_uids_json',
        'izom_propui_free_selection_anchor_uid',
    )


def _izom_propui_free_ordered_selection(order, selected_uids, *, allowed_extra=None):
    target = {
        str(uid or '').strip()
        for uid in selected_uids or []
        if str(uid or '').strip()
    }
    allowed_extra = set(allowed_extra or ())
    ordered = []
    seen = set()
    for uid in order or []:
        uid = str(uid or '').strip()
        if uid and uid in target and uid not in seen:
            ordered.append(uid)
            seen.add(uid)
    for uid in selected_uids or []:
        uid = str(uid or '').strip()
        if not uid or uid in seen or uid not in target:
            continue
        if allowed_extra and uid not in allowed_extra:
            continue
        ordered.append(uid)
        seen.add(uid)
    return ordered


def _izom_propui_free_selection_with_modifiers(order, current_selection, target_uid, anchor_uid, *, extend=False, toggle=False):
    ordered = [str(uid or '').strip() for uid in order or [] if str(uid or '').strip()]
    available = set(ordered)
    target = str(target_uid or '').strip()
    if target not in available:
        return _izom_propui_free_ordered_selection(ordered, current_selection), '', ''

    current = _izom_propui_free_ordered_selection(ordered, current_selection)
    anchor = str(anchor_uid or '').strip()
    if anchor not in available:
        anchor = current[-1] if current else target

    if extend:
        try:
            anchor_index = ordered.index(anchor)
            target_index = ordered.index(target)
        except ValueError:
            return [target], target, target
        start = min(anchor_index, target_index)
        end = max(anchor_index, target_index)
        return ordered[start:end + 1], target, anchor

    if toggle:
        if target in current:
            if len(current) <= 1:
                return [target], target, target
            selected = [uid for uid in current if uid != target]
            active = selected[-1] if selected else target
            if anchor not in selected:
                anchor = active
            return selected, active, anchor
        selected = _izom_propui_free_ordered_selection(ordered, [*current, target])
        return selected, target, anchor if anchor in available else target

    return [target], target, target


def _izom_propui_free_sync_entry_selection(params, *, preferred_active_uid=None, preferred_active_index=None, editor_context='HIERARCHY', persist=True):
    from .helper_layout import (
        _izom_propui_free_sync_layout_selection,
    )

    mode = str(editor_context or 'HIERARCHY').strip().upper()
    if mode == 'LAYOUT':
        active_item = None
        preferred_layout_uid = str(preferred_active_uid or '').strip()
        if preferred_layout_uid:
            active_item = _izom_propui_free_layout_item_by_uid(params, preferred_layout_uid) or _izom_propui_free_layout_item_by_entry_uid(params, preferred_layout_uid)
        selected_item_uids = _izom_propui_free_sync_layout_selection(
            params,
            preferred_active_uid=str(getattr(active_item, 'uid', '') or '').strip() or None,
            preferred_active_index=preferred_active_index,
            persist=persist,
        )
        result = []
        for item_uid in selected_item_uids:
            item = _izom_propui_free_layout_item_by_uid(params, item_uid)
            entry_uid = str(getattr(item, 'entry_uid', '') or '').strip() if item is not None else ''
            if entry_uid:
                result.append(entry_uid)
        return result
    active_attr, active_uid_attr, selected_attr, anchor_attr = _izom_propui_free_editor_selection_fields(mode)
    state_bundle = izom_propui_free_cached_entry_navigation_bundle(params)
    # Fast read-only path: resize redraws call this per frame with persist=False
    # and unchanged inputs. Cache the resolved active uid on the state bundle,
    # keyed on the fields that actually drive the result, so repeated calls skip
    # the O(N) set rebuilds and RNA walk below.
    if not persist and preferred_active_uid is None and preferred_active_index is None:
        try:
            memo_active_index = int(getattr(params, active_attr, 0) or 0)
        except (AttributeError, TypeError, ValueError):
            memo_active_index = 0
        memo_active_uid_attr = str(getattr(params, active_uid_attr, '') or '')
        memo_selected_attr = str(getattr(params, selected_attr, '') or '')
        memo_anchor_attr = str(getattr(params, anchor_attr, '') or '')
        memo_key = (mode, memo_active_index, memo_active_uid_attr, memo_selected_attr, memo_anchor_attr)
        sync_memo = state_bundle.get('_sync_entry_selection_memo')
        if sync_memo is not None:
            cached = sync_memo.get(memo_key)
            if cached is not None:
                return list(cached)
    entry_snapshots = state_bundle.get('entry_snapshots', []) or []
    entry_count = len(entry_snapshots)
    if entry_count == 0:
        if persist:
            _izom_propui_free_set_attr_if_changed(params, active_attr, 0)
            _izom_propui_free_set_attr_if_changed(params, active_uid_attr, '')
            _izom_propui_free_set_attr_if_changed(params, anchor_attr, '')
            _izom_propui_free_set_attr_if_changed(params, selected_attr, '[]')
            if mode == 'HIERARCHY':
                _izom_propui_free_smart_expand_selected_entry_sections(params, '')
        return []

    order = _izom_propui_free_entry_order_for_editor(params, mode)
    available = set(order)
    index_by_uid = state_bundle.get('entry_index_by_uid', {}) or {}
    existing = set(index_by_uid)
    active_uid = str(preferred_active_uid or '').strip()

    def _uid_at_index(index):
        if 0 <= index < entry_count:
            snap = entry_snapshots[index]
            if isinstance(snap, dict):
                return str(snap.get('uid', '') or '').strip()
            return str(getattr(snap, 'uid', '') or '').strip()
        return ''

    if not active_uid and preferred_active_index is not None:
        try:
            current_index = max(0, min(int(preferred_active_index), entry_count - 1))
        except (TypeError, ValueError):
            current_index = 0
        active_uid = _uid_at_index(current_index)

    if not active_uid:
        candidate_uid = str(getattr(params, active_uid_attr, '') or '').strip()
        if candidate_uid in available or (mode == 'HIERARCHY' and candidate_uid in existing):
            active_uid = candidate_uid

    if not active_uid:
        try:
            current_index = max(0, min(int(getattr(params, active_attr, 0)), entry_count - 1))
        except (AttributeError, TypeError, ValueError):
            current_index = 0
        candidate_uid = _uid_at_index(current_index)
        if candidate_uid in available or (mode == 'HIERARCHY' and candidate_uid in existing):
            active_uid = candidate_uid

    if not active_uid or (active_uid not in available and not (mode == 'HIERARCHY' and active_uid in existing)):
        active_uid = order[0] if order else ''

    selected_allowed = set(available)
    if mode == 'HIERARCHY':
        selected_allowed.update(existing)
    if preferred_active_index is not None and preferred_active_uid is None and active_uid:
        selected = [active_uid]
    else:
        selected = _izom_propui_free_ordered_selection(
            order,
            _izom_propui_free_uid_list_from_json(getattr(params, selected_attr, '[]')),
            allowed_extra=selected_allowed,
        )
    if not selected and active_uid:
        selected = [active_uid]
    elif active_uid and active_uid not in selected:
        selected.append(active_uid)
    active_index = index_by_uid.get(active_uid, 0) if active_uid else 0
    anchor_uid = str(getattr(params, anchor_attr, '') or '').strip()
    if preferred_active_index is not None and preferred_active_uid is None and active_uid:
        anchor_uid = active_uid
    if anchor_uid not in selected_allowed:
        anchor_uid = selected[0] if selected else active_uid
    if persist:
        guard_key = _izom_propui_free_suspend_list_context_updates(params)
        try:
            _izom_propui_free_set_attr_if_changed(params, active_uid_attr, active_uid)
            _izom_propui_free_set_attr_if_changed(params, active_attr, int(active_index))
            _izom_propui_free_set_attr_if_changed(params, anchor_attr, anchor_uid)
        finally:
            _izom_propui_free_resume_list_context_updates(params)
        _izom_propui_free_store_uid_list(params, selected_attr, selected)
        if mode == 'HIERARCHY':
            _izom_propui_free_smart_expand_selected_entry_sections(params, active_uid)
    elif preferred_active_uid is None and preferred_active_index is None:
        try:
            memo_active_index = int(getattr(params, active_attr, 0) or 0)
        except (AttributeError, TypeError, ValueError):
            memo_active_index = 0
        memo_active_uid_attr = str(getattr(params, active_uid_attr, '') or '')
        memo_selected_attr = str(getattr(params, selected_attr, '') or '')
        memo_anchor_attr = str(getattr(params, anchor_attr, '') or '')
        memo_key = (mode, memo_active_index, memo_active_uid_attr, memo_selected_attr, memo_anchor_attr)
        sync_memo = state_bundle.get('_sync_entry_selection_memo')
        if sync_memo is None:
            sync_memo = {}
            try:
                state_bundle['_sync_entry_selection_memo'] = sync_memo
            except TypeError:
                sync_memo = None
        if sync_memo is not None:
            sync_memo[memo_key] = tuple(selected)
    return selected


def _izom_propui_free_selected_entry_uids(params, editor_context='HIERARCHY'):
    from .operators_layout_support import _izom_propui_free_sync_layout_view_selection

    def _layout_view_entry_uids(*, view_uid='', view_item=None):
        resolved_view_item = view_item
        if resolved_view_item is None:
            resolved_view_item = _izom_propui_free_layout_view_item_by_uid(params, view_uid)
        if resolved_view_item is None:
            return []

        kind = str(getattr(resolved_view_item, 'kind', '') or '').strip().upper()
        if kind == 'ENTRY_ITEM':
            layout_uid = str(getattr(resolved_view_item, 'layout_uid', '') or '').strip()
            layout_item = _izom_propui_free_layout_item_by_uid(params, layout_uid)
            entry_uid = str(getattr(layout_item, 'entry_uid', '') or getattr(resolved_view_item, 'entry_uid', '') or '').strip()
            return [entry_uid] if entry_uid else []

        if kind != 'ROW_HEADER':
            return []

        entry_uids = []
        seen = set()
        for layout_uid in _izom_propui_free_layout_view_row_member_uids(resolved_view_item):
            layout_item = _izom_propui_free_layout_item_by_uid(params, layout_uid)
            entry_uid = str(getattr(layout_item, 'entry_uid', '') or '').strip() if layout_item is not None else ''
            if not entry_uid or entry_uid in seen:
                continue
            seen.add(entry_uid)
            entry_uids.append(entry_uid)
        return entry_uids

    if str(editor_context or 'HIERARCHY').strip().upper() == 'LAYOUT':
        selected_view_uids = _izom_propui_free_sync_layout_view_selection(params, persist=False)
        result = []
        seen = set()
        if not selected_view_uids:
            active_view_item = _izom_propui_free_active_layout_view_item(params)
            selected_view_uids = [str(getattr(active_view_item, 'uid', '') or '').strip()] if active_view_item is not None else []
        for view_uid in selected_view_uids:
            for entry_uid in _layout_view_entry_uids(view_uid=view_uid):
                if entry_uid in seen:
                    continue
                seen.add(entry_uid)
                result.append(entry_uid)
        return result
    return _izom_propui_free_sync_entry_selection(params, editor_context=editor_context)


def _izom_propui_free_active_entry_uids(params, editor_context='HIERARCHY', persist=True):
    from .helper_layout import (
        _izom_propui_free_active_layout_view_item,
    )

    mode = str(editor_context or 'HIERARCHY').strip().upper()
    if mode == 'LAYOUT':
        active_view_item = _izom_propui_free_active_layout_view_item(params)
        if active_view_item is None:
            return []
        kind = str(getattr(active_view_item, 'kind', '') or '').strip().upper()
        if kind == 'ENTRY_ITEM':
            layout_uid = str(getattr(active_view_item, 'layout_uid', '') or '').strip()
            layout_item = _izom_propui_free_layout_item_by_uid(params, layout_uid)
            entry_uid = str(getattr(layout_item, 'entry_uid', '') or getattr(active_view_item, 'entry_uid', '') or '').strip()
            return [entry_uid] if entry_uid else []
        if kind != 'ROW_HEADER':
            return []
        result = []
        seen = set()
        for layout_uid in _izom_propui_free_layout_view_row_member_uids(active_view_item):
            layout_item = _izom_propui_free_layout_item_by_uid(params, layout_uid)
            entry_uid = str(getattr(layout_item, 'entry_uid', '') or '').strip() if layout_item is not None else ''
            if not entry_uid or entry_uid in seen:
                continue
            seen.add(entry_uid)
            result.append(entry_uid)
        return result
    active_uid = _izom_propui_free_active_entry_uid(params, editor_context=mode, persist=persist)
    return [active_uid] if active_uid else []


def _izom_propui_free_active_entry_uid(params, editor_context='HIERARCHY', persist=True):
    from .helper_layout import _izom_propui_free_active_layout_entry_uid

    if str(editor_context or 'HIERARCHY').strip().upper() == 'LAYOUT':
        active_uids = _izom_propui_free_active_entry_uids(params, editor_context='LAYOUT', persist=persist)
        return active_uids[0] if active_uids else _izom_propui_free_active_layout_entry_uid(params)
    selection = _izom_propui_free_sync_entry_selection(params, editor_context=editor_context, persist=persist)
    _active_attr, active_uid_attr, _selected_attr, _anchor_attr = _izom_propui_free_editor_selection_fields(editor_context)
    active_uid = str(getattr(params, active_uid_attr, '') or '').strip()
    return active_uid if active_uid and active_uid in set(selection) else (selection[-1] if selection else '')


def _izom_propui_free_set_entry_selection(params, selected_uids, *, active_uid=None, anchor_uid=None, editor_context='HIERARCHY', update_list_context=False):
    from .helper_layout import (
        _izom_propui_free_layout_item_uid_order,
    )

    mode = str(editor_context or 'HIERARCHY').strip().upper()
    if mode == 'LAYOUT':
        available_item_uids = set(_izom_propui_free_layout_item_uid_order(params, visible_only=False))
        item_uids = []
        for entry_uid in selected_uids or []:
            item_uid = str(entry_uid or '').strip()
            if item_uid not in available_item_uids:
                item = _izom_propui_free_layout_item_by_entry_uid(params, item_uid)
                item_uid = str(getattr(item, 'uid', '') or '').strip() if item is not None else ''
            if item_uid:
                item_uids.append(item_uid)
        target_active_uid = str(active_uid or '').strip()
        if target_active_uid not in available_item_uids:
            active_item = _izom_propui_free_layout_item_by_entry_uid(params, target_active_uid) if target_active_uid else None
            target_active_uid = str(getattr(active_item, 'uid', '') or '').strip() if active_item is not None else ''
        target_anchor_uid = str(anchor_uid or '').strip()
        if target_anchor_uid not in available_item_uids:
            anchor_item = _izom_propui_free_layout_item_by_entry_uid(params, target_anchor_uid) if target_anchor_uid else None
            target_anchor_uid = str(getattr(anchor_item, 'uid', '') or '').strip() if anchor_item is not None else ''
        _izom_propui_free_set_layout_selection(
            params,
            item_uids,
            active_uid=target_active_uid,
            anchor_uid=target_anchor_uid,
            update_list_context=update_list_context,
        )
        return
    active_attr, active_uid_attr, selected_attr, anchor_attr = _izom_propui_free_editor_selection_fields(mode)
    order = _izom_propui_free_entry_order_for_editor(params, mode)
    available = set(order)
    existing = set(_izom_propui_free_entry_index_by_uid(params))
    target_active = str(active_uid or '').strip()
    allow_hidden_active = mode == 'HIERARCHY' and target_active in existing
    if not target_active or (target_active not in available and not allow_hidden_active):
        cleaned = [
            str(uid or '').strip()
            for uid in selected_uids or ()
            if str(uid or '').strip() in available or (mode == 'HIERARCHY' and str(uid or '').strip() in existing)
        ]
        target_active = cleaned[-1] if cleaned else (order[0] if order else '')
    selected_allowed = set(available)
    if mode == 'HIERARCHY':
        selected_allowed.update(existing)
    cleaned = _izom_propui_free_ordered_selection(order, selected_uids, allowed_extra=selected_allowed)
    if not cleaned and target_active:
        cleaned = [target_active]
    elif target_active and target_active not in cleaned:
        cleaned.append(target_active)
    target_anchor = str(anchor_uid or '').strip()
    if target_anchor not in selected_allowed:
        target_anchor = cleaned[0] if cleaned else target_active
    guard_key = None
    if not update_list_context:
        guard_key = _izom_propui_free_suspend_list_context_updates(params)
    try:
        _izom_propui_free_store_uid_list(params, selected_attr, cleaned)
        try:
            setattr(params, active_uid_attr, target_active)
            setattr(params, anchor_attr, target_anchor)
        except (AttributeError, TypeError, ValueError) as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
        _izom_propui_free_sync_entry_selection(params, preferred_active_uid=target_active, editor_context=mode)
    finally:
        if guard_key is not None:
            _izom_propui_free_resume_list_context_updates(params)
    if update_list_context and editor_context is not None:
        _izom_propui_free_set_last_editor_context(params, mode)
        _izom_propui_free_set_last_clicked_list_context(params, _izom_propui_free_clicked_list_context_for_editor(mode))


def _izom_propui_free_select_entry_uid(params, target_uid, *, editor_context='HIERARCHY', extend=False, toggle=False):
    from .helper_layout import (
        _izom_propui_free_entry_order_for_editor,
        _izom_propui_free_layout_item_by_entry_uid,
        _izom_propui_free_layout_item_by_uid,
        _izom_propui_free_layout_view_item_by_uid,
        _izom_propui_free_layout_view_row_member_uids,
        _izom_propui_free_layout_view_uid_order,
        _izom_propui_free_normalize_layout_view_uid,
        _izom_propui_free_set_layout_selection,
        _izom_propui_free_set_layout_view_selection,
    )
    from ..core.snapshot_layout import _izom_propui_free_layout_view_entry_uid

    mode = str(editor_context or 'HIERARCHY').strip().upper()
    if mode == 'LAYOUT':
        target_view_uid = _izom_propui_free_normalize_layout_view_uid(target_uid)
        if _izom_propui_free_layout_view_item_by_uid(params, target_view_uid) is None:
            target_item_uid = str(target_uid or '').strip()
            item = _izom_propui_free_layout_item_by_uid(params, target_item_uid)
            if item is None:
                item = _izom_propui_free_layout_item_by_entry_uid(params, target_item_uid)
            item_uid = str(getattr(item, 'uid', '') or '').strip() if item is not None else ''
            target_view_uid = _izom_propui_free_layout_view_entry_uid(item_uid) if item_uid else ''
        if not target_view_uid:
            visible_order = [
                uid for uid in _izom_propui_free_layout_view_uid_order(params)
                if str(getattr(_izom_propui_free_layout_view_item_by_uid(params, uid), 'kind', '') or '').strip().upper() != 'DIVIDER'
            ]
            target_view_uid = visible_order[0] if visible_order else ''
        if not target_view_uid:
            return []
        view_order = [
            uid for uid in _izom_propui_free_layout_view_uid_order(params)
            if str(getattr(_izom_propui_free_layout_view_item_by_uid(params, uid), 'kind', '') or '').strip().upper() != 'DIVIDER'
        ]
        selected, active_view_uid, anchor_view_uid = _izom_propui_free_selection_with_modifiers(
            view_order,
            _izom_propui_free_uid_list_from_json(getattr(params, 'izom_propui_free_layout_view_selected_uids_json', '[]')),
            target_view_uid,
            getattr(params, 'izom_propui_free_layout_view_selection_anchor_uid', ''),
            extend=extend,
            toggle=toggle,
        )
        active_view_uid = active_view_uid or target_view_uid
        anchor_view_uid = anchor_view_uid or active_view_uid
        _izom_propui_free_set_layout_view_selection(
            params,
            selected or [active_view_uid],
            active_uid=active_view_uid,
            anchor_uid=anchor_view_uid,
            update_list_context=True,
        )
        target_view_item = _izom_propui_free_layout_view_item_by_uid(params, active_view_uid)
        target_item_uid = str(getattr(target_view_item, 'layout_uid', '') or '').strip() if target_view_item is not None else ''
        if target_item_uid:
            _izom_propui_free_set_layout_selection(
                params,
                [target_item_uid],
                active_uid=target_item_uid,
                anchor_uid=target_item_uid,
                update_list_context=False,
            )
        result = []
        seen = set()
        for view_uid in selected or [active_view_uid]:
            view_item = _izom_propui_free_layout_view_item_by_uid(params, view_uid)
            if view_item is None:
                continue
            kind = str(getattr(view_item, 'kind', '') or '').strip().upper()
            layout_uids = []
            if kind == 'ENTRY_ITEM':
                layout_uids = [str(getattr(view_item, 'layout_uid', '') or '').strip()]
            elif kind == 'ROW_HEADER':
                layout_uids = _izom_propui_free_layout_view_row_member_uids(view_item)
            for layout_uid in layout_uids:
                layout_item = _izom_propui_free_layout_item_by_uid(params, layout_uid)
                entry_uid = str(getattr(layout_item, 'entry_uid', '') or '').strip() if layout_item is not None else ''
                if entry_uid and entry_uid not in seen:
                    seen.add(entry_uid)
                    result.append(entry_uid)
        return result
    order = _izom_propui_free_entry_order_for_editor(params, mode)
    if not order:
        return []
    target_uid = str(target_uid or '').strip()
    if target_uid not in order:
        target_uid = order[0]
    selected, active_uid, anchor_uid = _izom_propui_free_selection_with_modifiers(
        order,
        _izom_propui_free_uid_list_from_json(getattr(params, 'izom_propui_free_selected_uids_json', '[]')),
        target_uid,
        getattr(params, 'izom_propui_free_selection_anchor_uid', ''),
        extend=extend,
        toggle=toggle,
    )
    active_uid = active_uid or target_uid
    anchor_uid = anchor_uid or active_uid
    _izom_propui_free_set_entry_selection(
        params,
        selected or [active_uid],
        active_uid=active_uid,
        anchor_uid=anchor_uid,
        editor_context=mode,
        update_list_context=True,
    )
    return selected or [active_uid]

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

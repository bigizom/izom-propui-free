# SPDX-License-Identifier: GPL-3.0-or-later

from .diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .diagnostics import izom_propui_free_log_recovered
from bisect import bisect_left
from types import SimpleNamespace


def _izom_propui_free_collection_items(collection):
    if collection is None:
        return []
    try:
        return list(collection)
    except TypeError:
        return []


def _izom_propui_free_collection_remove(collection, index):
    if hasattr(collection, 'remove') and not isinstance(collection, list):
        collection.remove(index)
    else:
        collection.pop(index)


def _izom_propui_free_collection_clear(collection):
    if collection is None:
        return
    if hasattr(collection, 'clear'):
        try:
            collection.clear()
            return
        except (AttributeError, TypeError):
            pass
    while collection:
        _izom_propui_free_collection_remove(collection, len(collection) - 1)


def _izom_propui_free_collection_move(collection, from_index, to_index):
    if from_index == to_index:
        return
    if hasattr(collection, 'move') and not isinstance(collection, list):
        collection.move(from_index, to_index)
    else:
        item = collection.pop(from_index)
        collection.insert(to_index, item)


def _izom_propui_free_add_collection_item(collection):
    if hasattr(collection, 'add') and not isinstance(collection, list):
        return collection.add()
    item = SimpleNamespace()
    collection.append(item)
    return item


def _izom_propui_free_collection_uid_order(collection, uid_getter=None):
    uid_getter = uid_getter or (lambda item: str(getattr(item, 'uid', '') or '').strip())
    ordered = []
    for item in _izom_propui_free_collection_items(collection):
        uid = str(uid_getter(item) or '').strip()
        if uid:
            ordered.append(uid)
    return ordered


def _izom_propui_free_snapshot_uid_order(snapshots):
    ordered = []
    for snap in snapshots or []:
        uid = str((snap or {}).get('uid', '') or '').strip()
        if uid:
            ordered.append(uid)
    return ordered


def _izom_propui_free_collection_order_matches(collection, snapshots, uid_getter=None):
    return _izom_propui_free_collection_uid_order(collection, uid_getter) == _izom_propui_free_snapshot_uid_order(snapshots)


def _izom_propui_free_estimated_existing_reorder_count(current_order, target_order):
    if not current_order or not target_order:
        return 0
    current_index_by_uid = {
        str(uid or '').strip(): index
        for index, uid in enumerate(current_order)
        if str(uid or '').strip()
    }
    sequence = [
        current_index_by_uid[uid]
        for uid in target_order
        if uid in current_index_by_uid
    ]
    if not sequence:
        return 0

    # Existing entries that are already in relative order form an LIS. The
    # entries outside that sequence are the ones incremental sync must move.
    tails = []
    for value in sequence:
        cursor = bisect_left(tails, value)
        if cursor == len(tails):
            tails.append(value)
        else:
            tails[cursor] = value
    return max(0, len(sequence) - len(tails))


def _izom_propui_free_values_differ(current_value, new_value):
    try:
        if current_value == new_value:
            return False
        if isinstance(current_value, str) or isinstance(new_value, str):
            return str(current_value or '') != str(new_value or '')
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )

    try:
        return tuple(current_value) != tuple(new_value)
    except TypeError:
        return current_value != new_value
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        return current_value != new_value


def _izom_propui_free_sync_uid_collection(
    collection,
    snapshots,
    *,
    uid_getter=None,
    add_item=None,
    sync_item=None,
):
    if collection is None:
        return []

    uid_getter = uid_getter or (lambda item: str(getattr(item, 'uid', '') or '').strip())
    add_item = add_item or _izom_propui_free_add_collection_item
    normalized_snapshots = list(snapshots or [])
    target_uids = [str((snap or {}).get('uid', '') or '').strip() for snap in normalized_snapshots]
    target_uid_set = {uid for uid in target_uids if uid}

    items = _izom_propui_free_collection_items(collection)

    def _full_rebuild_from_snapshots():
        _izom_propui_free_collection_clear(collection)
        items[:] = []

        rebuilt = []
        for snap, target_uid in zip(normalized_snapshots, target_uids):
            if not target_uid:
                continue
            item = add_item(collection)
            if sync_item is not None:
                sync_item(item, snap)
            rebuilt.append(item)
        return rebuilt

    current_order = []
    existing_uids = set()
    stale_or_duplicate_count = 0
    for item in items:
        item_uid = uid_getter(item)
        if not item_uid or item_uid not in target_uid_set or item_uid in existing_uids:
            stale_or_duplicate_count += 1
            continue
        current_order.append(item_uid)
        existing_uids.add(item_uid)

    target_uid_count = sum(1 for uid in target_uids if uid)
    target_existing_order = [uid for uid in target_uids if uid and uid in existing_uids]
    missing_uid_count = sum(1 for uid in target_uids if uid and uid not in existing_uids)
    existing_reorder_count = _izom_propui_free_estimated_existing_reorder_count(current_order, target_existing_order)
    heavy_change_threshold = max(16, target_uid_count // 12)
    if sync_item is not None and (
        stale_or_duplicate_count > heavy_change_threshold
        or existing_reorder_count > heavy_change_threshold
        or missing_uid_count > heavy_change_threshold
    ):
        return _full_rebuild_from_snapshots()

    # Remove stale or duplicate items first so later moves operate on a unique
    # uid set that mirrors the target snapshot list.
    seen_uids = set()
    for index in range(len(items) - 1, -1, -1):
        item_uid = uid_getter(items[index])
        if not item_uid or item_uid not in target_uid_set or item_uid in seen_uids:
            _izom_propui_free_collection_remove(collection, index)
            items.pop(index)
            continue
        seen_uids.add(item_uid)

    index_by_uid = {}
    for index, item in enumerate(items):
        item_uid = uid_getter(item)
        if item_uid:
            index_by_uid[item_uid] = index

    def _reindex_range(start, end):
        if not items:
            return
        start = max(0, int(start or 0))
        end = min(len(items) - 1, int(end or 0))
        if end < start:
            start, end = end, start
        for cursor in range(start, end + 1):
            item_uid = uid_getter(items[cursor])
            if item_uid:
                index_by_uid[item_uid] = cursor

    resolved = []
    for index, snap in enumerate(normalized_snapshots):
        target_uid = target_uids[index]
        if not target_uid:
            continue

        if index < len(items) and uid_getter(items[index]) == target_uid:
            item = items[index]
        else:
            existing_index = index_by_uid.get(target_uid)
            if existing_index is None:
                item = add_item(collection)
                items.append(item)
                existing_index = len(items) - 1
                index_by_uid[target_uid] = existing_index
            else:
                item = items[existing_index]

            if existing_index != index:
                _izom_propui_free_collection_move(collection, existing_index, index)
                moved = items.pop(existing_index)
                items.insert(index, moved)
                item = moved
                _reindex_range(index, existing_index)

        if sync_item is not None:
            sync_item(item, snap)
        resolved.append(item)

    for index in range(len(items) - 1, len(resolved) - 1, -1):
        _izom_propui_free_collection_remove(collection, index)

    return resolved

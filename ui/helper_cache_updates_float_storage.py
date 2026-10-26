# SPDX-License-Identifier: GPL-3.0-or-later

from .helper_cache_updates_invalidation import (
    _izom_propui_free_pointer_guard_key,
    bpy,
    izom_propui_free_log_recovered,
)
import time
from ..core.collection_sync import _izom_propui_free_values_differ
from .helper_cache_updates_common import (
    _IZOM_PROPUI_FREE_DEFERRED_FLOAT_ARRAY_STORAGE_COMMITS,
    _IZOM_PROPUI_FREE_DEFERRED_FLOAT_ARRAY_STORAGE_INTERVAL,
)
from .lifecycle import izom_propui_free_register_lifecycle_timer


_IZOM_PROPUI_FREE_FLOAT_STORAGE_ACCESS_ERRORS = (
    AttributeError,
    TypeError,
    ValueError,
    RuntimeError,
    ReferenceError,
)
_IZOM_PROPUI_FREE_FLOAT_STORAGE_TIMER_NAME = 'float_array_storage_commit'


def _izom_propui_free_deferred_float_array_storage_key(owner, field_name):
    return (_izom_propui_free_pointer_guard_key(owner), str(field_name or ''))


def _izom_propui_free_pending_float_array_storage(owner, field_name):
    normalized_field_name = str(field_name or '').strip()
    if owner is None or not normalized_field_name:
        return None
    commit_key = _izom_propui_free_deferred_float_array_storage_key(owner, normalized_field_name)
    pending_commit = _IZOM_PROPUI_FREE_DEFERRED_FLOAT_ARRAY_STORAGE_COMMITS.get(commit_key)
    if pending_commit is None:
        return None
    try:
        return tuple(pending_commit[2])
    except _IZOM_PROPUI_FREE_FLOAT_STORAGE_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        return None


def _izom_propui_free_flush_deferred_float_array_storage_commits(force=False):
    global _IZOM_PROPUI_FREE_DEFERRED_FLOAT_ARRAY_STORAGE_TIMER_ACTIVE

    now = time.monotonic()
    pending = []
    next_interval = None

    for commit_key, payload in list(_IZOM_PROPUI_FREE_DEFERRED_FLOAT_ARRAY_STORAGE_COMMITS.items()):
        owner, field_name, storage, due_time = payload
        if force:
            remaining = 0.0
        else:
            try:
                remaining = float(due_time) - now
            except (TypeError, ValueError):
                remaining = 0.0
        if remaining <= 0.0:
            pending.append((owner, field_name, storage))
            _IZOM_PROPUI_FREE_DEFERRED_FLOAT_ARRAY_STORAGE_COMMITS.pop(commit_key, None)
            continue
        if next_interval is None or remaining < next_interval:
            next_interval = remaining

    for owner, field_name, storage in pending:
        if owner is None or not field_name:
            continue
        try:
            current_storage = getattr(owner, field_name, ())
        except _IZOM_PROPUI_FREE_FLOAT_STORAGE_ACCESS_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            current_storage = ()
        if not _izom_propui_free_values_differ(current_storage, storage):
            continue
        try:
            setattr(owner, field_name, storage)
        except _IZOM_PROPUI_FREE_FLOAT_STORAGE_ACCESS_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            continue

    if _IZOM_PROPUI_FREE_DEFERRED_FLOAT_ARRAY_STORAGE_COMMITS:
        _IZOM_PROPUI_FREE_DEFERRED_FLOAT_ARRAY_STORAGE_TIMER_ACTIVE = True
        return max(0.01, float(next_interval or _IZOM_PROPUI_FREE_DEFERRED_FLOAT_ARRAY_STORAGE_INTERVAL))

    _IZOM_PROPUI_FREE_DEFERRED_FLOAT_ARRAY_STORAGE_TIMER_ACTIVE = False
    return None


def _izom_propui_free_flush_float_array_storage_commits_now():
    return _izom_propui_free_flush_deferred_float_array_storage_commits(force=True)


def _izom_propui_free_schedule_float_array_storage_commit(owner, field_name, storage, *, delay=None):
    global _IZOM_PROPUI_FREE_DEFERRED_FLOAT_ARRAY_STORAGE_TIMER_ACTIVE

    if owner is None:
        return False

    normalized_field_name = str(field_name or '').strip()
    if not normalized_field_name:
        return False

    try:
        normalized_storage = tuple(storage)
    except _IZOM_PROPUI_FREE_FLOAT_STORAGE_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        normalized_storage = (storage,)

    commit_key = _izom_propui_free_deferred_float_array_storage_key(owner, normalized_field_name)
    pending_commit = _IZOM_PROPUI_FREE_DEFERRED_FLOAT_ARRAY_STORAGE_COMMITS.get(commit_key)

    if pending_commit is None:
        try:
            current_storage = getattr(owner, normalized_field_name, ())
        except _IZOM_PROPUI_FREE_FLOAT_STORAGE_ACCESS_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            current_storage = ()
        if not _izom_propui_free_values_differ(current_storage, normalized_storage):
            return True
    elif not _izom_propui_free_values_differ(pending_commit[2], normalized_storage):
        return True

    interval = _IZOM_PROPUI_FREE_DEFERRED_FLOAT_ARRAY_STORAGE_INTERVAL if delay is None else delay
    try:
        interval = max(0.01, float(interval))
    except (TypeError, ValueError):
        interval = _IZOM_PROPUI_FREE_DEFERRED_FLOAT_ARRAY_STORAGE_INTERVAL

    _IZOM_PROPUI_FREE_DEFERRED_FLOAT_ARRAY_STORAGE_COMMITS[commit_key] = (
        owner,
        normalized_field_name,
        normalized_storage,
        time.monotonic() + interval,
    )
    if _IZOM_PROPUI_FREE_DEFERRED_FLOAT_ARRAY_STORAGE_TIMER_ACTIVE:
        return True

    try:
        if not izom_propui_free_register_lifecycle_timer(
            _IZOM_PROPUI_FREE_FLOAT_STORAGE_TIMER_NAME,
            _izom_propui_free_flush_deferred_float_array_storage_commits,
            first_interval=interval,
        ):
            raise RuntimeError('PropUI Free lifecycle is not active')
    except _IZOM_PROPUI_FREE_FLOAT_STORAGE_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        pending_commit = _IZOM_PROPUI_FREE_DEFERRED_FLOAT_ARRAY_STORAGE_COMMITS.pop(commit_key, None)
        _IZOM_PROPUI_FREE_DEFERRED_FLOAT_ARRAY_STORAGE_TIMER_ACTIVE = False
        if pending_commit is None:
            pending_commit = (owner, normalized_field_name, normalized_storage, 0.0)
        try:
            current_storage = getattr(pending_commit[0], pending_commit[1], ())
        except _IZOM_PROPUI_FREE_FLOAT_STORAGE_ACCESS_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            current_storage = ()
        if _izom_propui_free_values_differ(current_storage, pending_commit[2]):
            try:
                setattr(pending_commit[0], pending_commit[1], pending_commit[2])
            except _IZOM_PROPUI_FREE_FLOAT_STORAGE_ACCESS_ERRORS as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )
                return False
        return True

    _IZOM_PROPUI_FREE_DEFERRED_FLOAT_ARRAY_STORAGE_TIMER_ACTIVE = True
    return True

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

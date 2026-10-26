# SPDX-License-Identifier: GPL-3.0-or-later

from .helper_cache_updates_entry_params import (
    _izom_propui_free_bulk_entry_updates_suspended,
    _izom_propui_free_pointer_guard_key,
    bpy,
    izom_propui_free_context_params,
    izom_propui_free_log_recovered,
)
from ..core.cache_common import izom_propui_free_invalidate_params_cache_fields
from .helper_cache_updates_common import (
    _IZOM_PROPUI_FREE_CHILD_COMPARE_INFO_CACHE,
    _IZOM_PROPUI_FREE_DISPLAY_RUNTIME_CACHE_FIELDS,
    _IZOM_PROPUI_FREE_FULL_RUNTIME_CACHE_FIELDS,
    _IZOM_PROPUI_FREE_LAYOUT_CACHE_FIELDS,
    _IZOM_PROPUI_FREE_LIST_CONTEXT_UPDATE_GUARD,
    _IZOM_PROPUI_FREE_RUNTIME_ENTRY_CACHE_FIELDS,
)



def _izom_propui_free_invalidate_cache_fields(
    params,
    *field_names,
    clear_value_label_owner=False,
):
    if params is None:
        return
    izom_propui_free_invalidate_params_cache_fields(
        params,
        field_names=field_names,
        clear_value_label_owner=clear_value_label_owner,
    )
    if any(
        str(field_name or '').strip() in {'entry_snapshots', 'entry_tree_snapshots', 'tree_state', 'runtime_entries'}
        for field_name in field_names
    ):
        _IZOM_PROPUI_FREE_CHILD_COMPARE_INFO_CACHE.clear()


def _izom_propui_free_invalidate_runtime_cache(params):
    if params is None:
        return
    _izom_propui_free_invalidate_cache_fields(
        params,
        *_IZOM_PROPUI_FREE_FULL_RUNTIME_CACHE_FIELDS,
    )


def _izom_propui_free_invalidate_entry_structure_cache(params):
    if params is None:
        return
    _izom_propui_free_invalidate_cache_fields(
        params,
        'entry_snapshots',
        'entry_tree_snapshots',
        'tree_state',
        'runtime_entries',
    )
    from .editor_session import izom_propui_free_invalidate_editor_session_bindings

    izom_propui_free_invalidate_editor_session_bindings()


def _izom_propui_free_invalidate_runtime_entry_cache(params):
    if params is None:
        return
    _izom_propui_free_invalidate_cache_fields(
        params,
        *_IZOM_PROPUI_FREE_RUNTIME_ENTRY_CACHE_FIELDS,
    )


def _izom_propui_free_invalidate_runtime_display_cache(params):
    if params is None:
        return
    _izom_propui_free_invalidate_cache_fields(
        params,
        *_IZOM_PROPUI_FREE_DISPLAY_RUNTIME_CACHE_FIELDS,
    )


def _izom_propui_free_invalidate_layout_cache(params):
    if params is None:
        return
    _izom_propui_free_invalidate_cache_fields(
        params,
        *_IZOM_PROPUI_FREE_LAYOUT_CACHE_FIELDS,
    )


def _izom_propui_free_schedule_runtime_entry_cache_invalidate(params, *, delay=None):
    _izom_propui_free_invalidate_runtime_entry_cache(params)

def _izom_propui_free_invalidate_value_label_runtime_display_cache(item, context=None):
    from .helper_value_labels import _izom_propui_free_find_value_label_owner
    from .helper_selection import _izom_propui_free_bump_collection_revision

    candidate_params = []
    seen_params = set()
    for candidate_context in (context, bpy.context):
        params = izom_propui_free_context_params(candidate_context)
        if params is None:
            continue
        marker = _izom_propui_free_pointer_guard_key(params)
        if marker in seen_params:
            continue
        seen_params.add(marker)
        candidate_params.append(params)
        if _izom_propui_free_bulk_entry_updates_suspended(params):
            _izom_propui_free_invalidate_cache_fields(
                params,
                *_IZOM_PROPUI_FREE_DISPLAY_RUNTIME_CACHE_FIELDS,
                clear_value_label_owner=True,
            )
            return

    try:
        params, _entry, collection_owner, collection_name, _index = _izom_propui_free_find_value_label_owner(item, context)
    except (AttributeError, TypeError, ValueError, ReferenceError, RecursionError) as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        params = candidate_params[0] if candidate_params else None
        collection_owner = None
        collection_name = None
    if collection_owner is not None and collection_name == 'value_labels':
        _izom_propui_free_bump_collection_revision(collection_owner, collection_name)
    _izom_propui_free_invalidate_runtime_display_cache(params)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

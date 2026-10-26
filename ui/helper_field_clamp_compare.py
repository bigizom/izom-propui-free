# SPDX-License-Identifier: GPL-3.0-or-later



def _izom_propui_free_child_compare_info(params, entry, *, parent=None, use_component_attr='visibility_use_component', component_attr='visibility_component_index'):
    from .helper_selection import _izom_propui_free_data_value, _izom_propui_free_entry_by_uid
    from .helper_value_labels import _izom_propui_free_entry_numeric_bounds

    if entry is None:
        return None

    if params is None:
        params = _izom_propui_free_find_params_for_entry(entry, None)

    state_bundle = izom_propui_free_cached_entry_tree_bundle(params) if params is not None else None
    snapshot_token = id(state_bundle.get('entry_snapshots')) if isinstance(state_bundle, dict) else 0

    resolved_parent = parent
    if resolved_parent is None:
        parent_uid = str(_izom_propui_free_data_value(entry, 'parent_uid', '') or '').strip()
        if not parent_uid or params is None:
            return None
        resolved_parent = state_bundle.get('parent_lookup', {}).get(parent_uid) if isinstance(state_bundle, dict) else None
        if resolved_parent is None:
            resolved_parent = _izom_propui_free_entry_by_uid(params, parent_uid)

    if not resolved_parent:
        return None

    entry_uid = str(_izom_propui_free_data_value(entry, 'uid', '') or '').strip()
    parent_uid = str(_izom_propui_free_data_value(resolved_parent, 'uid', '') or '').strip()
    params_key = getattr(params, 'as_pointer', lambda: 0)() if params is not None else 0
    try:
        use_component_value = bool(getattr(entry, use_component_attr, False))
    except (AttributeError, TypeError, ValueError):
        use_component_value = False
    try:
        component_raw_value = int(getattr(entry, component_attr, 1) or 1)
    except (AttributeError, TypeError, ValueError):
        component_raw_value = 1

    cache_key = (
        params_key,
        entry_uid,
        parent_uid,
        use_component_attr,
        component_attr,
        use_component_value,
        component_raw_value,
        snapshot_token,
    )
    cached = _IZOM_PROPUI_FREE_CHILD_COMPARE_INFO_CACHE.get(cache_key)
    if cached is not None:
        return dict(cached)

    compare_parent = resolved_parent
    parent_value_kind = izom_propui_free_entry_value_kind(
        compare_parent,
        str(_izom_propui_free_data_value(compare_parent, 'prop_type', '') or '').strip().upper(),
    )
    component_meta = izom_propui_free_entry_component_meta(compare_parent, parent_value_kind)
    supports_component = bool(component_meta.get('supported', False))
    use_component = use_component_value

    component_slot = 1
    if supports_component:
        component_slot = izom_propui_free_clamp_component_slot(
            getattr(entry, component_attr, 1),
            component_meta.get('size', 1),
            default=1,
        )

    component_enabled = supports_component and use_component
    compare_prop_type = str(parent_value_kind or 'NONE').strip().upper() or 'NONE'
    if component_enabled:
        compare_prop_type = str(component_meta.get('component_kind', compare_prop_type) or compare_prop_type).strip().upper() or compare_prop_type

    min_value = None
    max_value = None
    if _izom_propui_free_is_numeric_type(compare_prop_type):
        min_value, max_value = _izom_propui_free_entry_numeric_bounds(compare_parent, compare_prop_type)

    info = {
        'parent': compare_parent,
        'display_parent': resolved_parent,
        'parent_value_kind': str(parent_value_kind or 'NONE').strip().upper() or 'NONE',
        'parent_prop_type': compare_prop_type,
        'component_meta': component_meta,
        'component_enabled': component_enabled,
        'component_slot': component_slot,
        'min_value': min_value,
        'max_value': max_value,
    }
    _IZOM_PROPUI_FREE_CHILD_COMPARE_INFO_CACHE[cache_key] = dict(info)
    return info


def _izom_propui_free_visibility_compare_info(params, entry, *, parent=None):
    return _izom_propui_free_child_compare_info(
        params,
        entry,
        parent=parent,
        use_component_attr='visibility_use_component',
        component_attr='visibility_component_index',
    )


def _izom_propui_free_normalize_entry_child_compare_component_settings(entry, *, params=None, parent=None, use_component_attr='visibility_use_component', component_attr='visibility_component_index'):
    if entry is None:
        return

    info = _izom_propui_free_child_compare_info(
        params,
        entry,
        parent=parent,
        use_component_attr=use_component_attr,
        component_attr=component_attr,
    )
    component_meta = info.get('component_meta', {}) if info else {}
    supports_component = bool(component_meta.get('supported', False))

    try:
        use_component = bool(getattr(entry, use_component_attr, False))
    except (AttributeError, TypeError, ValueError):
        use_component = False

    if not supports_component:
        if use_component:
            try:
                setattr(entry, use_component_attr, False)
            except (AttributeError, TypeError, ValueError) as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )
        try:
            if int(getattr(entry, component_attr, 1) or 1) != 1:
                setattr(entry, component_attr, 1)
        except (AttributeError, TypeError, ValueError) as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
        return

    component_slot = izom_propui_free_clamp_component_slot(
        getattr(entry, component_attr, 1),
        component_meta.get('size', 1),
        default=1,
    )
    try:
        current_slot = int(getattr(entry, component_attr, component_slot) or component_slot)
    except (AttributeError, TypeError, ValueError):
        current_slot = component_slot
    if current_slot != component_slot:
        try:
            setattr(entry, component_attr, component_slot)
        except (AttributeError, TypeError, ValueError) as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )


def _izom_propui_free_normalize_child_compare_component_dependents(params, parent_entry):
    from .helper_field_clamp_conditions import (
        _izom_propui_free_clamp_visibility_match_float,
        _izom_propui_free_clamp_visibility_match_int,
        _izom_propui_free_clamp_visibility_range_max_float,
        _izom_propui_free_clamp_visibility_range_max_int,
    )

    if params is None or parent_entry is None:
        return

    parent_uid = str(getattr(parent_entry, 'uid', '') or '').strip()
    if not parent_uid:
        return

    guard_key = (_izom_propui_free_pointer_guard_key(parent_entry), 'child_compare_components')
    if guard_key in _IZOM_PROPUI_FREE_NORMALIZE_DEPENDENT_GUARD:
        return

    _IZOM_PROPUI_FREE_NORMALIZE_DEPENDENT_GUARD.add(guard_key)
    update_guard = _izom_propui_free_suspend_entry_updates(params)
    try:
        state_bundle = izom_propui_free_cached_entry_tree_bundle(params)
        tree_state = state_bundle.get('tree_state', {}) or {}
        child_uids = tuple((tree_state.get('children_by_uid', {}) or {}).get(parent_uid, ()) or ())
        if not child_uids:
            return
        index_by_uid = state_bundle.get('entry_index_by_uid', {}) or {}
        entries = getattr(params, 'izom_propui_free_entries', None) or []
        for child_uid in child_uids:
            try:
                child_index = int(index_by_uid.get(str(child_uid or '').strip(), -1))
            except (TypeError, ValueError):
                child_index = -1
            if child_index < 0 or child_index >= len(entries):
                continue
            candidate = entries[child_index]
            if str(getattr(candidate, 'parent_uid', '') or '').strip() != parent_uid:
                continue
            _izom_propui_free_normalize_entry_child_compare_component_settings(
                candidate,
                params=params,
                parent=parent_entry,
                use_component_attr='visibility_use_component',
                component_attr='visibility_component_index',
            )
            visibility_info = _izom_propui_free_visibility_compare_info(params, candidate, parent=parent_entry)
            _izom_propui_free_clamp_visibility_match_float(candidate, params=params, parent=parent_entry, info=visibility_info)
            _izom_propui_free_clamp_visibility_match_int(candidate, params=params, parent=parent_entry, info=visibility_info)
            _izom_propui_free_clamp_visibility_range_max_float(candidate, params=params, parent=parent_entry, info=visibility_info)
            _izom_propui_free_clamp_visibility_range_max_int(candidate, params=params, parent=parent_entry, info=visibility_info)
    finally:
        if update_guard is not None:
            _izom_propui_free_resume_entry_updates(params)
        _IZOM_PROPUI_FREE_NORMALIZE_DEPENDENT_GUARD.discard(guard_key)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401
from ..core.cache_common import _izom_propui_free_pointer_guard_key
from ..core.cache_state import izom_propui_free_cached_entry_tree_bundle
from ..core.diagnostics import izom_propui_free_log_recovered
from ..core.value_access_common import izom_propui_free_clamp_component_slot
from ..core.value_access_entries import (
    izom_propui_free_entry_component_meta,
    izom_propui_free_entry_value_kind,
)
from ..core.value_labels_common import _izom_propui_free_is_numeric_type
from .helper_cache_updates_common import (
    _IZOM_PROPUI_FREE_CHILD_COMPARE_INFO_CACHE,
    _IZOM_PROPUI_FREE_NORMALIZE_DEPENDENT_GUARD,
)
from .helper_cache_updates_entry_params import (
    _izom_propui_free_find_params_for_entry,
    _izom_propui_free_resume_entry_updates,
    _izom_propui_free_suspend_entry_updates,
)


__all__ = izom_propui_free_public_names(globals())

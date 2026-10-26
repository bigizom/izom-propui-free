# SPDX-License-Identifier: GPL-3.0-or-later

from .helper_value_labels_common import (
    _izom_propui_free_entry_by_uid,
    _izom_propui_free_entry_component_rule_info,
    _izom_propui_free_entry_numeric_bounds,
    _izom_propui_free_normalize_threshold_collection,
    _izom_propui_free_normalize_value_label_collection,
    _izom_propui_free_pointer_guard_key,
    _izom_propui_free_self_value_label_companion_key,
    izom_propui_free_cached_entry_tree_bundle,
    izom_propui_free_entry_value_kind,
    izom_propui_free_is_numeric_value_kind,
)
from .helper_cache_updates_common import _IZOM_PROPUI_FREE_NORMALIZE_DEPENDENT_GUARD
from .helper_field_clamp_conditions import (
    _izom_propui_free_clamp_visibility_match_float,
    _izom_propui_free_clamp_visibility_match_int,
    _izom_propui_free_clamp_visibility_range_max_float,
    _izom_propui_free_clamp_visibility_range_max_int,
)



def _izom_propui_free_normalize_dependent_thresholds(changed_entry, params, *, prune_unresolvable_exact_arrays=False):
    if params is None:
        return
    guard_key = _izom_propui_free_pointer_guard_key(params)
    if guard_key in _IZOM_PROPUI_FREE_NORMALIZE_DEPENDENT_GUARD:
        return
    changed_uid = str(getattr(changed_entry, 'uid', '') or '')
    if not changed_uid:
        return

    _IZOM_PROPUI_FREE_NORMALIZE_DEPENDENT_GUARD.add(guard_key)
    try:
        changed_prop_type = izom_propui_free_entry_value_kind(changed_entry, str(getattr(changed_entry, 'prop_type', '') or ''))
        changed_is_numeric = izom_propui_free_is_numeric_value_kind(changed_prop_type)
        if changed_is_numeric:
            changed_min, changed_max = _izom_propui_free_entry_numeric_bounds(changed_entry, changed_prop_type)
            compare_info = {
                'parent': changed_entry,
                'parent_prop_type': changed_prop_type,
                'min_value': changed_min,
                'max_value': changed_max,
            }
            bundle = izom_propui_free_cached_entry_tree_bundle(params)
            tree_state = bundle.get('tree_state', {}) or {}
            children_by_uid = tree_state.get('children_by_uid', {}) or {}
            for child_uid in tuple(children_by_uid.get(changed_uid, ()) or ()):
                child_entry = _izom_propui_free_entry_by_uid(params, child_uid)
                if child_entry is None:
                    continue
                if changed_prop_type == 'FLOAT':
                    _izom_propui_free_clamp_visibility_match_float(child_entry, params=params, info=compare_info)
                    _izom_propui_free_clamp_visibility_range_max_float(child_entry, params=params, info=compare_info)
                else:
                    _izom_propui_free_clamp_visibility_match_int(child_entry, params=params, info=compare_info)
                    _izom_propui_free_clamp_visibility_range_max_int(child_entry, params=params, info=compare_info)

            _izom_propui_free_normalize_value_label_collection(changed_entry, params=params)
        elif changed_prop_type in {'COLOR', 'VECTOR', 'INT_ARRAY', 'BOOL_ARRAY'}:
            component_groups = {}
            for item in getattr(changed_entry, 'value_labels', None) or []:
                component_info = _izom_propui_free_entry_component_rule_info(changed_entry, item)
                if not component_info.get('use_component'):
                    continue
                component_kind = str(component_info.get('component_meta', {}).get('component_kind', '') or '').strip().upper()
                if not izom_propui_free_is_numeric_value_kind(component_kind):
                    continue
                group_key = _izom_propui_free_self_value_label_companion_key(changed_entry, item)
                component_groups.setdefault((component_kind, group_key), []).append(item)
            for (component_kind, _group_key), component_items in component_groups.items():
                _izom_propui_free_normalize_threshold_collection(
                    component_items,
                    'target_value_int' if component_kind == 'INT' else 'target_value_float',
                    component_kind,
                    params=params,
                    base_value=0,
                )

    finally:
        _IZOM_PROPUI_FREE_NORMALIZE_DEPENDENT_GUARD.discard(guard_key)


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

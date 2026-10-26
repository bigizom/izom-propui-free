# SPDX-License-Identifier: GPL-3.0-or-later

from .value_access import (
    _izom_propui_free_entry_value,
    izom_propui_free_clamp_component_slot,
    izom_propui_free_entry_component_meta,
    izom_propui_free_is_exact_match_value_kind,
    izom_propui_free_normalize_value_kind,
)
from .value_labels_common import (
    _izom_propui_free_is_numeric_type,
    _izom_propui_free_rule_kind_value,
    _izom_propui_free_value_label_match_mode,
)
from .value_labels_compare import (
    _izom_propui_free_normalize_bool_state,
    _izom_propui_free_numeric_entry_low,
    _izom_propui_free_rule_compare_range_value,
    _izom_propui_free_rule_compare_value,
)


def _izom_propui_free_value_label_rule_is_normalized(item):
    if not isinstance(item, dict):
        return False
    return (
        'threshold' in item
        or 'match_value' in item
        or 'value_kind' in item
        or 'component_index' in item
        or 'source_value_kind' in item
    )


def _izom_propui_free_value_labels_runtime(entry, collection_name='value_labels', prop_type=None):
    raw_items = _izom_propui_free_entry_value(entry, collection_name, []) or []
    normalized = []
    target_type = str(_izom_propui_free_entry_value(entry, 'prop_type', '') or '')
    if collection_name != 'value_labels' or target_type == 'TEXT':
        return []
    source_type = izom_propui_free_normalize_value_kind(prop_type or _izom_propui_free_entry_value(entry, 'value_kind', target_type) or target_type)
    component_meta = izom_propui_free_entry_component_meta(entry, source_type)
    entry_use_component = bool(component_meta.get('supported', False)) and bool(_izom_propui_free_entry_value(entry, 'value_labels_use_component', False))
    entry_component_slot = izom_propui_free_clamp_component_slot(
        _izom_propui_free_entry_value(entry, 'value_labels_component_index', 1),
        component_meta.get('size', 1),
        default=1,
    )

    for item in raw_items:
        if _izom_propui_free_value_label_rule_is_normalized(item):
            normalized_item = dict(item)
            normalized_item['match_mode'] = _izom_propui_free_value_label_match_mode(
                normalized_item.get('match_mode', 'GREATER')
            )
            normalized.append(normalized_item)
            continue

        if isinstance(item, dict):
            getter = item.get
        else:
            getter = lambda key, default=None, _item=item: getattr(_item, key, default)

        row_use_component = bool(component_meta.get('supported', False)) and (
            bool(getter('use_source_component', False)) or entry_use_component
        )
        row_component_slot = izom_propui_free_clamp_component_slot(
            getter('source_component_index', entry_component_slot),
            component_meta.get('size', 1),
            default=entry_component_slot,
        )
        row_effective_source_type = (
            str(component_meta.get('component_kind', source_type) or source_type)
            if row_use_component else source_type
        )
        threshold = None
        range_threshold = None
        match_value = None
        match_mode = _izom_propui_free_value_label_match_mode(getter('match_mode', 'GREATER'))
        if _izom_propui_free_is_numeric_type(row_effective_source_type):
            threshold = _izom_propui_free_rule_compare_value(getter, 'target_value', row_effective_source_type)
            range_threshold = _izom_propui_free_rule_compare_range_value(
                getter,
                'target_value',
                row_effective_source_type,
                default_value=threshold,
            )
        elif izom_propui_free_is_exact_match_value_kind(row_effective_source_type):
            match_mode = 'EQUAL'
            match_value = _izom_propui_free_rule_compare_value(getter, 'target_value', row_effective_source_type, reference_entry=entry)
        normalized.append({
            'uid': str(getter('uid', '') or ''),
            'rule_kind': _izom_propui_free_rule_kind_value(item),
            'label': str(getter('label', '') or ''),
            'match_mode': match_mode,
            'threshold': threshold,
            'range_threshold': range_threshold,
            'match_value': match_value,
            'value_kind': row_effective_source_type,
            'source_value_kind': source_type,
            'use_component': row_use_component,
            'component_index': row_component_slot - 1,
            'source_bool_state': _izom_propui_free_normalize_bool_state(getter('source_bool_state', 'WHEN_TRUE')),
        })

    return normalized


from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

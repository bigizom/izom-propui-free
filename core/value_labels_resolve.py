# SPDX-License-Identifier: GPL-3.0-or-later

from .value_access import (
    izom_propui_free_component_value,
    izom_propui_free_is_exact_match_value_kind,
    izom_propui_free_normalize_value_kind,
    izom_propui_free_values_match,
)
from .value_labels_common import (
    _izom_propui_free_rule_has_display_action,
    _izom_propui_free_rule_is_fallback,
    _izom_propui_free_is_numeric_type,
)
from .value_labels_compare import (
    _izom_propui_free_entry_compare_value,
    _izom_propui_free_normalize_bool_state,
    _izom_propui_free_numeric_compare_value,
    _izom_propui_free_numeric_rule_matches_value,
)


def _izom_propui_free_resolve_entry_value_label_item(entry, value_kind, items, current_value=None):
    resolved = None
    full_compare_value = _izom_propui_free_entry_compare_value(entry, value_kind, current_value=current_value)
    for item in items:
        label = str(item.get('label', '') or '').strip()
        if not label and not _izom_propui_free_rule_is_fallback(item):
            continue
        item_kind = izom_propui_free_normalize_value_kind(item.get('value_kind', value_kind), value_kind)
        compare_value = full_compare_value
        if bool(item.get('use_component', False)) and item_kind == 'BOOL':
            compare_value = izom_propui_free_component_value(
                full_compare_value,
                item.get('source_value_kind', value_kind),
                int(item.get('component_index', 0) or 0),
                default=False,
            )
        elif bool(item.get('use_component', False)) and _izom_propui_free_is_numeric_type(item_kind):
            compare_value = izom_propui_free_component_value(
                full_compare_value,
                item.get('source_value_kind', value_kind),
                int(item.get('component_index', 0) or 0),
                default=0 if item_kind == 'INT' else 0.0,
            )
        elif item_kind != value_kind:
            compare_value = _izom_propui_free_entry_compare_value(entry, item_kind, current_value=current_value)

        if _izom_propui_free_is_numeric_type(item_kind):
            threshold = item.get('threshold', 0 if item_kind == 'INT' else 0.0)
            if _izom_propui_free_numeric_rule_matches_value(
                compare_value,
                threshold,
                item_kind,
                match_mode=item.get('match_mode', 'GREATER'),
                range_threshold=item.get('range_threshold'),
            ):
                return item
        elif item_kind == 'BOOL':
            required_state = _izom_propui_free_normalize_bool_state(item.get('source_bool_state', 'WHEN_TRUE'))
            if bool(compare_value) == (required_state != 'WHEN_FALSE'):
                return item
        elif izom_propui_free_is_exact_match_value_kind(item_kind):
            if izom_propui_free_values_match(compare_value, item.get('match_value'), item_kind):
                return item
        else:
            return item
    return None


def _izom_propui_free_value_label_item_has_dynamic_label(item):
    if not isinstance(item, dict):
        return False
    return _izom_propui_free_rule_has_display_action(item)


def _izom_propui_free_rule_matches(rule, *, current_target_bool=None):
    if not isinstance(rule, dict):
        return False
    return _izom_propui_free_rule_has_display_action(rule)

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

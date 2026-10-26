# SPDX-License-Identifier: GPL-3.0-or-later

from .value_access import (
    _izom_propui_free_entry_value,
    izom_propui_free_entry_value_kind,
    izom_propui_free_is_exact_match_value_kind,
)
from .value_labels_common import (
    _izom_propui_free_clean_display_text,
    _izom_propui_free_display_base_state,
    _izom_propui_free_is_numeric_type,
    _izom_propui_free_rule_is_fallback,
)
from .value_labels_resolve import (
    _izom_propui_free_resolve_entry_value_label_item,
    _izom_propui_free_rule_matches,
    _izom_propui_free_value_label_item_has_dynamic_label,
)
from .value_labels_runtime import _izom_propui_free_value_labels_runtime


def _izom_propui_free_find_winning_rule(rules, match_fn):
    # Dynamic Labels are priority lists: the first matching row wins.
    for rule in rules or []:
        if not match_fn(rule):
            continue
        return rule
    return None


def _izom_propui_free_apply_rule_list_override(display_state, rules, *, current_target_bool=None, fallback_label=None):
    if not isinstance(display_state, dict):
        return display_state
    winner = _izom_propui_free_find_winning_rule(
        rules,
        lambda rule: _izom_propui_free_rule_matches(rule, current_target_bool=current_target_bool),
    )
    if winner is not None:
        if _izom_propui_free_rule_is_fallback(winner):
            if fallback_label is None:
                fallback_text = _izom_propui_free_clean_display_text(display_state.get('base_label', ''))
            else:
                fallback_text = _izom_propui_free_clean_display_text(fallback_label)
            display_state['display_label'] = fallback_text
        else:
            label = _izom_propui_free_clean_display_text(winner.get('label', ''))
            if label:
                display_state['display_label'] = label
    return display_state


def _izom_propui_free_build_dynamic_label_spec(entry, prop_id=''):
    prop_type = str(_izom_propui_free_entry_value(entry, 'prop_type', 'FLOAT') or 'FLOAT')
    value_kind = izom_propui_free_entry_value_kind(entry, prop_type)
    base_state = _izom_propui_free_display_base_state(entry, prop_id)
    spec = {
        'prop_type': prop_type,
        'value_kind': value_kind,
        'value_bucket_compare_kind': value_kind,
        'value_label_component_index': -1,
        'safe_prop_id': base_state['safe_prop_id'],
        'base_label': base_state['base_label'],
        'base_tooltip': base_state['base_tooltip'],
        'bool_states': None,
        'value_buckets': [],
        'has_dynamic_label': False,
    }

    if value_kind == 'BOOL' and bool(_izom_propui_free_entry_value(entry, 'use_bool_state_labels', False)):
        spec['bool_states'] = _izom_propui_free_resolved_bool_state_display(entry, prop_id)
        spec['has_dynamic_label'] = True

    if (
        (_izom_propui_free_is_numeric_type(value_kind) or izom_propui_free_is_exact_match_value_kind(value_kind))
        and bool(_izom_propui_free_entry_value(entry, 'use_value_labels', False))
    ):
        value_buckets = []
        for item in _izom_propui_free_value_labels_runtime(entry, 'value_labels', prop_type=value_kind):
            bucket = dict(item)
            value_buckets.append(bucket)
        spec['value_buckets'] = value_buckets
        if any(_izom_propui_free_value_label_item_has_dynamic_label(item) for item in value_buckets):
            spec['has_dynamic_label'] = True

    return spec

def _izom_propui_free_apply_display_override(display_state, override):
    if not isinstance(display_state, dict) or not isinstance(override, dict):
        return display_state
    label = _izom_propui_free_clean_display_text(override.get('label', ''))
    if label:
        display_state['display_label'] = label
    return display_state


def _izom_propui_free_resolve_entry_display_state(entry, prop_id='', current_value=None):
    spec = _izom_propui_free_build_dynamic_label_spec(entry, prop_id)
    base_state = _izom_propui_free_display_base_state(entry, prop_id)
    prop_type = spec['prop_type']
    value_kind = spec.get('value_kind', prop_type)
    use_value_labels = bool(_izom_propui_free_entry_value(entry, 'use_value_labels', False))
    use_bool_state_labels = bool(_izom_propui_free_entry_value(entry, 'use_bool_state_labels', False))

    resolved = {
        'prop_type': prop_type,
        'display_label': spec['base_label'],
        'base_label': base_state['base_label'],
        'safe_prop_id': spec['safe_prop_id'],
        'use_value_labels': use_value_labels,
        'use_bool_state_labels': use_bool_state_labels,
        'resolved_tooltip': spec['base_tooltip'],
    }

    current_bool = None
    if value_kind == 'BOOL' and spec['bool_states']:
        current_bool = current_value
        if current_bool is None:
            current_bool = _izom_propui_free_entry_value(entry, '_current_value', _izom_propui_free_entry_value(entry, 'default_bool', False))
        _izom_propui_free_apply_display_override(resolved, spec['bool_states'][bool(current_bool)])

    if (_izom_propui_free_is_numeric_type(value_kind) or izom_propui_free_is_exact_match_value_kind(value_kind)) and spec['value_buckets']:
        bucket = _izom_propui_free_resolve_entry_value_label_item(entry, value_kind, spec['value_buckets'], current_value=current_value)
        if isinstance(bucket, dict):
            if _izom_propui_free_rule_is_fallback(bucket):
                resolved['display_label'] = _izom_propui_free_clean_display_text(spec.get('base_label', ''))
            else:
                bucket_fallback_label = _izom_propui_free_clean_display_text(bucket.get('label', '')) or _izom_propui_free_clean_display_text(resolved.get('display_label', ''))
                _izom_propui_free_apply_display_override(resolved, bucket)

    return resolved


def _izom_propui_free_resolved_bool_state_display(entry, prop_id=''):
    base_state = _izom_propui_free_display_base_state(entry, prop_id)
    return {
        False: {
            'label': _izom_propui_free_clean_display_text(_izom_propui_free_entry_value(entry, 'bool_label_false', '')) or base_state['fallback_label'],
        },
        True: {
            'label': _izom_propui_free_clean_display_text(_izom_propui_free_entry_value(entry, 'bool_label_true', '')) or base_state['fallback_label'],
        },
        'fallback': base_state['fallback_label'],
        'base_label': base_state['base_label'],
        'safe_prop_id': base_state['safe_prop_id'],
        'base_tooltip': base_state['base_tooltip'],
    }

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

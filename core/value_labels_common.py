# SPDX-License-Identifier: GPL-3.0-or-later

from .value_access import (
    _izom_propui_free_entry_value,
    izom_propui_free_is_numeric_value_kind,
)


def _izom_propui_free_clean_display_text(value):
    return str(value or '').strip()


def _izom_propui_free_rule_kind_value(rule):
    if isinstance(rule, dict):
        raw_value = rule.get('rule_kind', 'LABEL')
    else:
        raw_value = getattr(rule, 'rule_kind', 'LABEL')
    kind = str(raw_value or 'LABEL').strip().upper()
    return kind or 'LABEL'


def _izom_propui_free_rule_is_fallback(rule):
    return _izom_propui_free_rule_kind_value(rule) == 'FALLBACK'


def _izom_propui_free_is_numeric_type(prop_type):
    return izom_propui_free_is_numeric_value_kind(prop_type)


_IZOM_PROPUI_FREE_VALUE_LABEL_MATCH_MODES = frozenset({'EQUAL', 'GREATER', 'LESS', 'RANGE'})


def _izom_propui_free_value_label_match_mode(raw_value, default='GREATER'):
    fallback = str(default or 'GREATER').strip().upper() or 'GREATER'
    if fallback not in _IZOM_PROPUI_FREE_VALUE_LABEL_MATCH_MODES:
        fallback = 'GREATER'
    resolved = str(raw_value or fallback).strip().upper() or fallback
    return resolved if resolved in _IZOM_PROPUI_FREE_VALUE_LABEL_MATCH_MODES else fallback

def _izom_propui_free_rule_has_display_action(rule):
    if _izom_propui_free_rule_is_fallback(rule):
        return True
    if isinstance(rule, dict):
        label = rule.get('label', '')
    else:
        label = getattr(rule, 'label', '')
    if _izom_propui_free_clean_display_text(label):
        return True
    return False

def _izom_propui_free_display_base_state(entry, prop_id=''):
    base_label = _izom_propui_free_clean_display_text(_izom_propui_free_entry_value(entry, 'label', ''))
    safe_prop_id = _izom_propui_free_clean_display_text(prop_id or _izom_propui_free_entry_value(entry, 'prop_id', ''))
    return {
        'base_label': base_label,
        'safe_prop_id': safe_prop_id,
        'fallback_label': base_label,
        'base_tooltip': _izom_propui_free_clean_display_text(_izom_propui_free_entry_value(entry, 'description', '')),
    }

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

# SPDX-License-Identifier: GPL-3.0-or-later

from .operators_value_labels_common_base import (
    izom_propui_free_log_recovered,
)
from ..core.value_access_common import izom_propui_free_is_exact_match_value_kind
from .helper_value_labels_exact import _izom_propui_free_set_low_exact_array_value
from .helper_value_labels_source import _izom_propui_free_entry_component_rule_info


_IZOM_PROPUI_FREE_VALUE_LABEL_DEFAULT_ACCESS_ERRORS = (
    AttributeError,
    TypeError,
    ValueError,
    RuntimeError,
    ReferenceError,
)


def _izom_propui_free_assign_exact_match_defaults(item, source_type, *, field_root='value', reference_entry=None, params=None):
    normalized_kind = str(source_type or 'NONE').strip().upper() or 'NONE'
    text_attr = f"{field_root}_text"

    if normalized_kind in {'COLOR', 'VECTOR', 'INT_ARRAY', 'BOOL_ARRAY'}:
        try:
            _izom_propui_free_set_low_exact_array_value(item, field_root, normalized_kind, reference_entry=reference_entry, params=params)
        except _IZOM_PROPUI_FREE_VALUE_LABEL_DEFAULT_ACCESS_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
        )
    elif izom_propui_free_is_exact_match_value_kind(normalized_kind):
        try:
            setattr(item, text_attr, '')
        except _IZOM_PROPUI_FREE_VALUE_LABEL_DEFAULT_ACCESS_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
        )


def _izom_propui_free_assign_self_component_defaults(item, entry, *, reference_entry=None):
    if item is None or entry is None:
        return
    component_info = _izom_propui_free_entry_component_rule_info(entry, reference_entry=reference_entry)
    use_component = bool(component_info.get('use_component', False))
    component_slot = int(component_info.get('component_slot', 1) or 1)
    try:
        item.use_source_component = use_component
    except _IZOM_PROPUI_FREE_VALUE_LABEL_DEFAULT_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
    try:
        item.source_component_index = component_slot
    except _IZOM_PROPUI_FREE_VALUE_LABEL_DEFAULT_ACCESS_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )



from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

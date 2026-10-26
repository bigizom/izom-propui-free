# SPDX-License-Identifier: GPL-3.0-or-later

from .diagnostics import izom_propui_free_log_recovered

from .constants import (
    IZOM_PROPUI_FREE_ENTRY_SERIALIZED_FIELDS,
    IZOM_PROPUI_FREE_TEXT_STYLE_DEFAULTS,
    IZOM_PROPUI_FREE_VALUE_LABEL_SERIALIZED_FIELDS,
)
from .entry_ids import (
    _izom_propui_free_new_uid,
)
from .float_arrays import (
    izom_propui_free_normalize_array_storage as _izom_propui_free_typed_array_snapshot_value,
)


_IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS = (AttributeError, TypeError, ValueError)
_IZOM_PROPUI_FREE_IMPORT_EXCEPTIONS = (ImportError, AttributeError)
_IZOM_PROPUI_FREE_NUMERIC_EXCEPTIONS = (TypeError, ValueError)
_IZOM_PROPUI_FREE_FLOAT_ARRAY_DEFAULT = (1.0,) * 32
_IZOM_PROPUI_FREE_INT_ARRAY_DEFAULT = (0,) * 32
_IZOM_PROPUI_FREE_BOOL_ARRAY_DEFAULT = (False,) * 32
_IZOM_PROPUI_FREE_ENTRY_DEFAULT_ARRAY_FIELDS = {
    'default_float_array': ('FLOAT', _IZOM_PROPUI_FREE_FLOAT_ARRAY_DEFAULT),
    'default_int_array': ('INT', _IZOM_PROPUI_FREE_INT_ARRAY_DEFAULT),
    'default_bool_array': ('BOOL', _IZOM_PROPUI_FREE_BOOL_ARRAY_DEFAULT),
}
_IZOM_PROPUI_FREE_ENTRY_CONDITION_ARRAY_FIELDS = {
    'visibility_match_float_array': ('FLOAT', _IZOM_PROPUI_FREE_FLOAT_ARRAY_DEFAULT),
    'visibility_match_int_array': ('INT', _IZOM_PROPUI_FREE_INT_ARRAY_DEFAULT),
    'visibility_match_bool_array': ('BOOL', _IZOM_PROPUI_FREE_BOOL_ARRAY_DEFAULT),
}
_IZOM_PROPUI_FREE_ENTRY_ARRAY_FIELD_NAMES = frozenset(
    (*_IZOM_PROPUI_FREE_ENTRY_DEFAULT_ARRAY_FIELDS, *_IZOM_PROPUI_FREE_ENTRY_CONDITION_ARRAY_FIELDS)
)
_IZOM_PROPUI_FREE_ENTRY_SERIALIZED_SCALAR_FIELDS = tuple(
    name for name in IZOM_PROPUI_FREE_ENTRY_SERIALIZED_FIELDS
    if name not in _IZOM_PROPUI_FREE_ENTRY_ARRAY_FIELD_NAMES
)
_IZOM_PROPUI_FREE_FRESH_ENTRY_DEFAULT_VALUES = None
_IZOM_PROPUI_FREE_FRESH_ENTRY_ALWAYS_SET_FIELDS = frozenset({
    'uid',
    'parent_uid',
    'prop_id',
    'label',
    'editor_label',
    'description',
    'prop_type',
    'ui_order',
    'display_order',
})
_IZOM_PROPUI_FREE_VALUE_LABEL_ARRAY_FIELDS = {
    'value_float_array': ('FLOAT', _IZOM_PROPUI_FREE_FLOAT_ARRAY_DEFAULT),
    'value_int_array': ('INT', _IZOM_PROPUI_FREE_INT_ARRAY_DEFAULT),
    'value_bool_array': ('BOOL', _IZOM_PROPUI_FREE_BOOL_ARRAY_DEFAULT),
    'target_value_float_array': ('FLOAT', _IZOM_PROPUI_FREE_FLOAT_ARRAY_DEFAULT),
    'target_value_int_array': ('INT', _IZOM_PROPUI_FREE_INT_ARRAY_DEFAULT),
    'target_value_bool_array': ('BOOL', _IZOM_PROPUI_FREE_BOOL_ARRAY_DEFAULT),
}
_IZOM_PROPUI_FREE_VALUE_LABEL_SERIALIZED_SCALAR_FIELDS = tuple(
    name for name in IZOM_PROPUI_FREE_VALUE_LABEL_SERIALIZED_FIELDS
    if name not in _IZOM_PROPUI_FREE_VALUE_LABEL_ARRAY_FIELDS
)
_IZOM_PROPUI_FREE_VALUE_LABEL_RUNTIME_SCALAR_FIELDS = tuple(
    name for name in IZOM_PROPUI_FREE_VALUE_LABEL_SERIALIZED_FIELDS
    if name not in _IZOM_PROPUI_FREE_VALUE_LABEL_ARRAY_FIELDS
)
_IZOM_PROPUI_FREE_ENTRY_RUNTIME_COMMON_FIELDS = (
    'uid',
    'parent_uid',
    'prop_id',
    'label',
    'editor_label',
    'description',
    'prop_type',
    'ui_order',
    'display_order',
    'row_slot',
    'alert_style',
    'value_label_layout',
    'multi_component_layout',
    'multi_component_draw_mode',
    'use_value_labels',
    'value_labels_use_component',
    'value_labels_component_index',
    'use_bool_state_labels',
    'bool_label_true',
    'bool_label_false',
    'library_overridable',
    'bool_child_visibility',
    'number_child_visibility',
    'visibility_inheritance_depth',
    'visibility_use_component',
    'visibility_component_index',
    'visibility_match_float',
    'visibility_match_int',
    'visibility_range_max_float',
    'visibility_range_max_int',
)
_IZOM_PROPUI_FREE_ENTRY_RUNTIME_TEXT_STYLE_FIELDS = (
    'text_alignment',
    'text_role',
    'text_alert',
    'text_icon',
    'text_icon_hug_text',
    'text_icon_after',
    'text_icon_after_hug_text',
)
_IZOM_PROPUI_FREE_ENTRY_RUNTIME_ARRAY_PRESENTATION_FIELDS = (
    'array_element_type',
    'array_size',
    'float_subtype',
    'float_array_subtype',
)
_IZOM_PROPUI_FREE_ENTRY_RUNTIME_FLOAT_FIELDS = (
    'default_float',
    'min_float',
    'max_float',
    'slider',
    'use_soft_limits',
    'soft_min_float',
    'soft_max_float',
    'step_float',
    'precision',
    'float_subtype',
)
_IZOM_PROPUI_FREE_ENTRY_RUNTIME_INT_FIELDS = (
    'default_int',
    'min_int',
    'max_int',
    'slider',
    'use_soft_limits',
    'soft_min_int',
    'soft_max_int',
    'step_int',
)
_IZOM_PROPUI_FREE_ENTRY_RUNTIME_BOOL_FIELDS = (
    'default_bool',
)
def _izom_propui_free_snapshot_typed_array_value(value, element_type, default_value):
    # Live Blender vector properties are already fixed-size typed arrays. The
    # general normalizer also accepts loose imported data, but it is much more
    # expensive and cold entry snapshots call this path many times.
    try:
        if len(value) == len(default_value):
            return tuple(value)
    except _IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS:
        pass
    return _izom_propui_free_typed_array_snapshot_value(value, element_type, default_value)


def _izom_propui_free_ensure_item_uid(item):
    try:
        uid = str(getattr(item, 'uid', '') or '').strip()
    except _IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS:
        uid = ''
    if uid:
        return uid

    uid = _izom_propui_free_new_uid()
    try:
        item.uid = uid
    except _IZOM_PROPUI_FREE_ACCESS_EXCEPTIONS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
    return uid


def _izom_propui_free_make_default_snapshot(index_hint):
    return {
        'uid': _izom_propui_free_new_uid(),
        'parent_uid': '',
        'prop_id': f'prop_{index_hint}',
        'label': f'Property {index_hint}',
        'editor_label': '',
        'description': '',
        'prop_type': 'FLOAT',
        **IZOM_PROPUI_FREE_TEXT_STYLE_DEFAULTS,
        'default_float': 0.0,
        'default_int': 0,
        'default_bool': False,
        'default_float_array': (1.0,) * 32,
        'default_int_array': (0,) * 32,
        'default_bool_array': (False,) * 32,
        'min_float': 0.0,
        'max_float': 1.0,
        'min_int': 0,
        'max_int': 5,
        'ui_order': index_hint,
        'display_order': index_hint,
        'row_slot': 1,
        'slider': True,
        'alert_style': False,
        'value_label_layout': 'INLINE',
        'multi_component_layout': 'INLINE_LABEL',
        'multi_component_draw_mode': 'WIDGET',
        'use_value_labels': False,
        'value_labels_use_component': False,
        'value_labels_component_index': 1,
        'use_bool_state_labels': False,
        'bool_label_true': '',
        'bool_label_false': '',
        'use_soft_limits': False,
        'soft_min_float': 0.0,
        'soft_max_float': 1.0,
        'soft_min_int': 0,
        'soft_max_int': 5,
        'step_float': 0.10,
        'step_int': 1,
        'precision': 3,
        'array_element_type': 'FLOAT',
        'array_size': 4,
        'float_subtype': 'NONE',
        'float_array_subtype': 'NONE',
        'library_overridable': True,
        'bool_child_visibility': 'ALWAYS',
        'number_child_visibility': 'ALWAYS',
        'visibility_inheritance_depth': 1,
        'visibility_use_component': False,
        'visibility_component_index': 1,
        'visibility_match_float': 0.0,
        'visibility_match_int': 0,
        'visibility_match_float_array': (1.0,) * 32,
        'visibility_match_int_array': (0,) * 32,
        'visibility_match_bool_array': (False,) * 32,
        'visibility_range_max_float': 1.0,
        'visibility_range_max_int': 0,
        'value_labels': [],
    }


def _izom_propui_free_fresh_entry_default_values():
    global _IZOM_PROPUI_FREE_FRESH_ENTRY_DEFAULT_VALUES
    if _IZOM_PROPUI_FREE_FRESH_ENTRY_DEFAULT_VALUES is None:
        _IZOM_PROPUI_FREE_FRESH_ENTRY_DEFAULT_VALUES = _izom_propui_free_make_default_snapshot(1)
    return _IZOM_PROPUI_FREE_FRESH_ENTRY_DEFAULT_VALUES

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

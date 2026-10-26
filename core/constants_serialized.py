# SPDX-License-Identifier: GPL-3.0-or-later

IZOM_PROPUI_FREE_TEXT_STYLE_DEFAULTS = {
    'text_alignment': 'LEFT',
    'text_role': 'TEXT',
    'text_alert': False,
    'text_icon': 'NONE',
    'text_icon_hug_text': True,
    'text_icon_after': 'NONE',
    'text_icon_after_hug_text': True,
}
IZOM_PROPUI_FREE_TEXT_STYLE_FIELDS = tuple(IZOM_PROPUI_FREE_TEXT_STYLE_DEFAULTS)

IZOM_PROPUI_FREE_ENTRY_SERIALIZED_FIELDS = (
    'uid',
    'parent_uid',
    'prop_id',
    'label',
    'editor_label',
    'description',
    'prop_type',
    *IZOM_PROPUI_FREE_TEXT_STYLE_FIELDS,
    'default_float',
    'default_int',
    'default_bool',
    'default_float_array',
    'default_int_array',
    'default_bool_array',
    'min_float',
    'max_float',
    'min_int',
    'max_int',
    'ui_order',
    'display_order',
    'row_slot',
    'slider',
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
    'use_soft_limits',
    'soft_min_float',
    'soft_max_float',
    'soft_min_int',
    'soft_max_int',
    'step_float',
    'step_int',
    'precision',
    'array_element_type',
    'array_size',
    'float_subtype',
    'float_array_subtype',
    'library_overridable',
    'bool_child_visibility',
    'number_child_visibility',
    'visibility_inheritance_depth',
    'visibility_use_component',
    'visibility_component_index',
    'visibility_match_float',
    'visibility_match_int',
    'visibility_match_float_array',
    'visibility_match_int_array',
    'visibility_match_bool_array',
    'visibility_range_max_float',
    'visibility_range_max_int',
)

IZOM_PROPUI_FREE_VALUE_LABEL_SERIALIZED_FIELDS = (
    'uid',
    'rule_kind',
    'match_mode',
    'label',
    'value_float',
    'value_int',
    'value_range_float',
    'value_range_int',
    'value_float_array',
    'value_int_array',
    'value_bool_array',
    'target_value_float',
    'target_value_int',
    'target_value_range_float',
    'target_value_range_int',
    'target_value_float_array',
    'target_value_int_array',
    'target_value_bool_array',
    'use_source_component',
    'source_component_index',
    'source_bool_state',
)

IZOM_PROPUI_FREE_MAX_FLOAT_PRECISION = 6
IZOM_PROPUI_FREE_MAX_NUMERIC_STEP = 100

IZOM_PROPUI_FREE_LIST_ENTRY_TYPE_LABELS = {
    'FLOAT': 'Float',
    'INT': 'Integer',
    'BOOL': 'Boolean',
    'ARRAY': 'Array',
    'TEXT': 'Text',
}

IZOM_PROPUI_FREE_MAX_GENERATED_UI_TEXT = 160
IZOM_PROPUI_FREE_MAX_TOOLTIP_TEXT = 255
IZOM_PROPUI_FREE_MAX_LABEL_INPUT_TEXT = 255
IZOM_PROPUI_FREE_MAX_TOOLTIP_INPUT_TEXT = 512
IZOM_PROPUI_FREE_MAX_PROP_ID_TEXT = 63

from .exports import izom_propui_free_public_names  # noqa: E402,F401


__all__ = izom_propui_free_public_names(globals(), all_public=True)

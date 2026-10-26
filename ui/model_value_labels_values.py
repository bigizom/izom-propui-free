# SPDX-License-Identifier: GPL-3.0-or-later

from .model_value_labels_common import (
    BoolProperty,
    BoolVectorProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
    IZOM_PROPUI_FREE_MAX_LABEL_INPUT_TEXT,
    IZOM_PROPUI_FREE_OTHER_LABEL_RULE_KIND_ITEMS,
    IZOM_PROPUI_FREE_RULE_SOURCE_BOOL_STATE_ITEMS,
    IZOM_PROPUI_FREE_VALUE_LABEL_MATCH_MODE_ITEMS,
    IntProperty,
    IntVectorProperty,
    PropertyGroup,
    StringProperty,
    _izom_propui_free_direct_float_array_color_property,
    _izom_propui_free_value_label_array_value_updated,
    _izom_propui_free_value_label_rule_state_updated,
    _izom_propui_free_value_label_updated,
)
from .helper_value_labels_updates import (
    _izom_propui_free_target_value_float_updated,
    _izom_propui_free_target_value_int_updated,
    _izom_propui_free_value_float_updated,
    _izom_propui_free_value_int_updated,
)
from .model_proxies_arrays import _izom_propui_free_add_float_array_proxy_properties
from .model_proxies_components import _izom_propui_free_add_array_component_proxy_properties
from .model_proxies_scalar import _izom_propui_free_add_editor_float_proxy_properties



class IZOM_PROPUI_FREE_ValueLabel(PropertyGroup):
    uid: StringProperty(
        name="UID",
        description="Internal stable identifier used for editor selection",
        default="",
        options={'HIDDEN'},
    )
    rule_kind: EnumProperty(
        name="Row Type",
        description="Choose whether this row applies a label override or resets to the current fallback label for this rule set",
        items=IZOM_PROPUI_FREE_OTHER_LABEL_RULE_KIND_ITEMS,
        default='LABEL',
        update=_izom_propui_free_value_label_rule_state_updated,
    )
    match_mode: EnumProperty(
        name="Match",
        description="How this row compares numeric values. Dynamic Labels use the first matching row from top to bottom",
        items=IZOM_PROPUI_FREE_VALUE_LABEL_MATCH_MODE_ITEMS,
        default='GREATER',
        update=_izom_propui_free_value_label_rule_state_updated,
    )
    target_value_float: FloatProperty(
        name="This Entry Value",
        description="Primary comparison value for this entry's own float value",
        default=0.0,
        update=_izom_propui_free_target_value_float_updated,
    )
    target_value_int: IntProperty(
        name="This Entry Value",
        description="Primary comparison value for this entry's own integer value",
        default=0,
        update=_izom_propui_free_target_value_int_updated,
    )
    target_value_range_float: FloatProperty(
        name="This Entry Range End",
        description="Second range value for this entry's own float value when Match is In Range",
        default=1.0,
        update=_izom_propui_free_value_label_rule_state_updated,
    )
    target_value_range_int: IntProperty(
        name="This Entry Range End",
        description="Second range value for this entry's own integer value when Match is In Range",
        default=0,
        update=_izom_propui_free_value_label_rule_state_updated,
    )
    target_value_float_array: FloatVectorProperty(
        name="This Entry Float Array",
        description="Exact float array value this entry must have for the bucket to apply",
        size=IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
        subtype='NONE',
        default=(1.0,) * IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
        update=_izom_propui_free_value_label_array_value_updated,
    )
    target_value_int_array: IntVectorProperty(
        name="This Entry Int Array",
        description="Exact integer-array value this entry must have for the bucket to apply",
        size=IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
        subtype='NONE',
        default=(0,) * IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
        update=_izom_propui_free_value_label_rule_state_updated,
    )
    target_value_bool_array: BoolVectorProperty(
        name="This Entry Bool Array",
        description="Exact boolean-array value this entry must have for the bucket to apply",
        size=IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
        subtype='NONE',
        default=(False,) * IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
        update=_izom_propui_free_value_label_rule_state_updated,
    )
    target_value_float_array_color: _izom_propui_free_direct_float_array_color_property(
        'target_value_float_array',
        name="This Entry Color",
        description="Exact RGBA value this entry must have for the bucket to apply when it resolves to a color",
        defer_storage_write=True,
    )
    use_source_component: BoolProperty(
        name="Use One Component",
        description="For vector, color, integer-array, or boolean-array values, evaluate this rule from one chosen component or channel instead of matching the whole value",
        default=False,
        update=_izom_propui_free_value_label_rule_state_updated,
    )
    source_component_index: IntProperty(
        name="Component",
        description="1-based component or channel used by this rule while Use One Component is enabled",
        default=1,
        min=1,
        max=IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
        update=_izom_propui_free_value_label_rule_state_updated,
    )
    source_bool_state: EnumProperty(
        name="When Component Is",
        description="Boolean state to match when the selected component is a boolean",
        items=IZOM_PROPUI_FREE_RULE_SOURCE_BOOL_STATE_ITEMS,
        default='WHEN_TRUE',
        update=_izom_propui_free_value_label_rule_state_updated,
    )
    label: StringProperty(
        name="Label",
        description="Label to use when this row matches",
        default="",
        maxlen=IZOM_PROPUI_FREE_MAX_LABEL_INPUT_TEXT,
        update=_izom_propui_free_value_label_updated,
    )
    value_float: FloatProperty(
        name="Value",
        description="Primary comparison value for this row",
        default=0.0,
        update=_izom_propui_free_value_float_updated,
    )
    value_int: IntProperty(
        name="Value",
        description="Primary comparison value for this row",
        default=0,
        update=_izom_propui_free_value_int_updated,
    )
    value_range_float: FloatProperty(
        name="Range End",
        description="Second range value when Match is In Range",
        default=1.0,
        update=_izom_propui_free_value_label_rule_state_updated,
    )
    value_range_int: IntProperty(
        name="Range End",
        description="Second range value when Match is In Range",
        default=0,
        update=_izom_propui_free_value_label_rule_state_updated,
    )
    value_float_array: FloatVectorProperty(
        name="From Float Array",
        description="Exact float array value to match when this entry resolves to a float array",
        size=IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
        subtype='NONE',
        default=(1.0,) * IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
        update=_izom_propui_free_value_label_array_value_updated,
    )
    value_int_array: IntVectorProperty(
        name="From Int Array",
        description="Exact integer-array value to match when this entry resolves to an integer array",
        size=IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
        subtype='NONE',
        default=(0,) * IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
        update=_izom_propui_free_value_label_rule_state_updated,
    )
    value_bool_array: BoolVectorProperty(
        name="From Bool Array",
        description="Exact boolean-array value to match when this entry resolves to a boolean array",
        size=IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
        subtype='NONE',
        default=(False,) * IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
        update=_izom_propui_free_value_label_rule_state_updated,
    )
    value_float_array_color: _izom_propui_free_direct_float_array_color_property(
        'value_float_array',
        name="From Color",
        description="Exact RGBA value to match when this entry resolves to a color",
        defer_storage_write=True,
    )
_izom_propui_free_add_editor_float_proxy_properties(
    IZOM_PROPUI_FREE_ValueLabel,
    {
        'target_value_float': {
            'name': "This Entry Value",
            'description': "Primary comparison value for this entry's own float value",
        },
        'target_value_range_float': {
            'name': "This Entry Range End",
            'description': "Second range value for this entry's own float value",
        },
        'value_float': {
            'name': "Value",
            'description': "Primary comparison value for this row",
        },
        'value_range_float': {
            'name': "Range End",
            'description': "Second range value when Match is In Range",
        },
    },
)

_izom_propui_free_add_float_array_proxy_properties(
    IZOM_PROPUI_FREE_ValueLabel,
    {
        'target_value_float_array': {
            'name': "This Entry Value",
            'description': "Exact float array value this entry must have for the bucket to apply",
        },
        'value_float_array': {
            'name': "From Value",
            'description': "Exact float array value to match when this entry resolves to a float array",
        },
    },
)

_izom_propui_free_add_array_component_proxy_properties(
    IZOM_PROPUI_FREE_ValueLabel,
    {
        'target_value_float_array': {
            'name': "This Entry Value",
            'description': "Exact float-array value this entry must have for the bucket to apply",
        },
        'target_value_int_array': {
            'name': "This Entry Value",
            'description': "Exact integer-array value this entry must have for the bucket to apply",
        },
        'target_value_bool_array': {
            'name': "This Entry Value",
            'description': "Exact boolean-array value this entry must have for the bucket to apply",
        },
        'value_float_array': {
            'name': "From Value",
            'description': "Exact float-array value to match when this entry resolves to a float array",
        },
        'value_int_array': {
            'name': "From Value",
            'description': "Exact integer-array value to match when this entry resolves to an integer array",
        },
        'value_bool_array': {
            'name': "From Value",
            'description': "Exact boolean-array value to match when this entry resolves to a boolean array",
        },
    },
)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

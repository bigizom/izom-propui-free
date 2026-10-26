# SPDX-License-Identifier: GPL-3.0-or-later

from .model_entries_updates import (
    IZOM_PROPUI_FREE_ENTRY_LIST_COLLAPSE_STATE_ITEMS,
    _izom_propui_free_entry_list_collapse_state_get,
    _izom_propui_free_entry_list_collapse_state_set,
    _izom_propui_free_entry_list_collapsed_get,
    _izom_propui_free_entry_list_collapsed_set,
    _izom_propui_free_entry_runtime_state_updated,
    _izom_propui_free_slider_updated,
    _izom_propui_free_use_soft_limits_updated,
)
from bpy.props import (
    BoolProperty,
    BoolVectorProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    IntVectorProperty,
    StringProperty,
)
from bpy.types import PropertyGroup
from .editor_session import izom_propui_free_session_int_property, izom_propui_free_session_string_property
from ..core.constants_display import (
    IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
    IZOM_PROPUI_FREE_ARRAY_SIZE_MIN,
    IZOM_PROPUI_FREE_BOOL_VISIBILITY_ITEMS,
    IZOM_PROPUI_FREE_ENTRY_TREE_MAX_DEPTH,
    IZOM_PROPUI_FREE_FLOAT_ARRAY_SUBTYPE_ITEMS,
    IZOM_PROPUI_FREE_FLOAT_SUBTYPE_ITEMS,
    IZOM_PROPUI_FREE_MULTI_COMPONENT_DRAW_MODE_ITEMS,
    IZOM_PROPUI_FREE_MULTI_COMPONENT_LAYOUT_ITEMS,
    IZOM_PROPUI_FREE_NUMBER_VISIBILITY_ITEMS,
    IZOM_PROPUI_FREE_TEXT_ALIGNMENT_ITEMS,
    IZOM_PROPUI_FREE_TEXT_ROLE_ITEMS,
    IZOM_PROPUI_FREE_VALUE_LABEL_LAYOUT_ITEMS,
)
from ..core.constants_serialized import (
    IZOM_PROPUI_FREE_MAX_LABEL_INPUT_TEXT,
    IZOM_PROPUI_FREE_MAX_PROP_ID_TEXT,
    IZOM_PROPUI_FREE_MAX_TOOLTIP_INPUT_TEXT,
)
from ..core.constants_types import (
    IZOM_PROPUI_FREE_ARRAY_ELEMENT_TYPE_ITEMS,
    IZOM_PROPUI_FREE_PROP_TYPE_ITEMS,
)
from .helper_cache_updates_arrays import (
    _izom_propui_free_entry_array_shape_updated,
    _izom_propui_free_entry_array_value_updated,
)
from .helper_cache_updates_custom import (
    _izom_propui_free_bool_label_false_updated,
    _izom_propui_free_bool_label_true_updated,
    _izom_propui_free_description_updated,
    _izom_propui_free_editor_label_updated,
    _izom_propui_free_label_updated,
)
from .helper_cache_updates_entry_runtime import _izom_propui_free_entry_runtime_display_updated
from .helper_cache_updates_entry_type import _izom_propui_free_prop_type_updated
from .helper_field_clamp_arrays import _izom_propui_free_float_array_subtype_updated
from .helper_field_clamp_numeric import (
    _izom_propui_free_float_range_updated,
    _izom_propui_free_int_range_updated,
)
from .helper_field_clamp_prop_id import _izom_propui_free_prop_id_updated
from .helper_layout_updates import _izom_propui_free_row_slot_updated
from .helper_selection_active import (
    _izom_propui_free_entry_value_labels_active_index_updated,
)
from .helper_value_labels_updates import (
    _izom_propui_free_default_float_updated,
    _izom_propui_free_default_int_updated,
    _izom_propui_free_number_child_visibility_updated,
    _izom_propui_free_step_float_updated,
    _izom_propui_free_visibility_inheritance_depth_updated,
    _izom_propui_free_visibility_match_float_updated,
    _izom_propui_free_visibility_match_int_updated,
    _izom_propui_free_visibility_range_max_float_updated,
    _izom_propui_free_visibility_range_max_int_updated,
)
from .model_proxies_arrays import _izom_propui_free_add_float_array_proxy_properties
from .model_proxies_color import _izom_propui_free_direct_float_array_color_property
from .model_proxies_scalar import _izom_propui_free_add_editor_float_proxy_properties
from .model_proxies_components import _izom_propui_free_add_array_component_proxy_properties
from .model_value_labels_values import IZOM_PROPUI_FREE_ValueLabel



class IZOM_PROPUI_FREE_PropertyEntry(PropertyGroup):
    uid: StringProperty(name="UID", description="Internal stable identifier used for tree parenting", default="", options={'HIDDEN'})
    parent_uid: StringProperty(name="Parent UID", description="Internal parent link for Entry List hierarchy", default="", options={'HIDDEN'})
    entry_list_collapsed: BoolProperty(
        name="Collapsed",
        description="Collapse or expand this parent entry in the Entry List",
        default=False,
        get=_izom_propui_free_entry_list_collapsed_get,
        set=_izom_propui_free_entry_list_collapsed_set,
    )
    entry_list_collapse_state: EnumProperty(
        name="Collapse State",
        description="Expand or collapse this parent entry in the Entry List",
        items=IZOM_PROPUI_FREE_ENTRY_LIST_COLLAPSE_STATE_ITEMS,
        default='EXPANDED',
        get=_izom_propui_free_entry_list_collapse_state_get,
        set=_izom_propui_free_entry_list_collapse_state_set,
        options={'HIDDEN'},
    )

    prop_id: StringProperty(
        name="Property ID",
        description="Custom-property key stored on the resolved target owner. Property IDs must be unique per target; duplicate names are auto-suffixed",
        default="prop",
        maxlen=IZOM_PROPUI_FREE_MAX_PROP_ID_TEXT,
        update=_izom_propui_free_prop_id_updated,
    )
    label: StringProperty(
        name="Label",
        description="User-facing label shown in the generated UI. You can also edit it directly in the Entry List",
        default="Property",
        maxlen=IZOM_PROPUI_FREE_MAX_LABEL_INPUT_TEXT,
        update=_izom_propui_free_label_updated,
    )
    editor_label: StringProperty(
        name="Editor Label",
        description="Optional editor-only name used in izom PropUI lists without changing generated labels or custom properties",
        default="",
        maxlen=IZOM_PROPUI_FREE_MAX_LABEL_INPUT_TEXT,
        update=_izom_propui_free_editor_label_updated,
    )
    description: StringProperty(
        name="Tooltip",
        description="Static tooltip shown for this property in the generated UI",
        default="",
        maxlen=IZOM_PROPUI_FREE_MAX_TOOLTIP_INPUT_TEXT,
        update=_izom_propui_free_description_updated,
    )
    prop_type: EnumProperty(
        name="Type",
        description="Entry type used by the generated UI and property builder",
        items=IZOM_PROPUI_FREE_PROP_TYPE_ITEMS,
        default='FLOAT',
        update=_izom_propui_free_prop_type_updated,
    )
    text_alignment: EnumProperty(name="Alignment", description="How this text block is aligned in the generated UI", items=IZOM_PROPUI_FREE_TEXT_ALIGNMENT_ITEMS, default='LEFT', update=_izom_propui_free_entry_runtime_display_updated)
    text_role: EnumProperty(name="Role", description="Choose whether this text entry draws text, a divider, or generated-row space", items=IZOM_PROPUI_FREE_TEXT_ROLE_ITEMS, default='TEXT', update=_izom_propui_free_entry_runtime_display_updated)
    text_alert: BoolProperty(name="Alert Style", description="Draw this text block with Blender's alert styling", default=False, update=_izom_propui_free_entry_runtime_display_updated)
    text_icon: StringProperty(name="Icon", description="Optional Blender icon drawn before this text block", default="NONE", update=_izom_propui_free_entry_runtime_display_updated)
    text_icon_hug_text: BoolProperty(name="Hug Text", description="For centered text only, keep the before icon attached to the text instead of pinning it to the row edge; left and right aligned text always hugs icons", default=True, update=_izom_propui_free_entry_runtime_display_updated)
    text_icon_after: StringProperty(name="After Icon", description="Optional Blender icon drawn after this text block", default="NONE", update=_izom_propui_free_entry_runtime_display_updated)
    text_icon_after_hug_text: BoolProperty(name="Hug Text", description="For centered text only, keep the after icon attached to the text instead of pinning it to the row edge; left and right aligned text always hugs icons", default=True, update=_izom_propui_free_entry_runtime_display_updated)
    default_float: FloatProperty(name="Default", description="Default float value for this generated custom property", default=0.0, update=_izom_propui_free_default_float_updated)
    default_int: IntProperty(name="Default", description="Default integer value for this generated custom property", default=0, update=_izom_propui_free_default_int_updated)
    default_bool: BoolProperty(name="Default", description="Default boolean value for this generated custom property", default=False, update=_izom_propui_free_entry_runtime_state_updated)
    default_float_array: FloatVectorProperty(
        name="Default",
        description="Default float values for this generated array custom property",
        size=IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
        subtype='NONE',
        default=(1.0,) * IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
        update=_izom_propui_free_entry_array_value_updated,
    )
    default_int_array: IntVectorProperty(
        name="Default",
        description="Default integer values for this generated array custom property",
        size=IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
        subtype='NONE',
        default=(0,) * IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
        update=_izom_propui_free_entry_runtime_state_updated,
    )
    default_bool_array: BoolVectorProperty(
        name="Default",
        description="Default boolean values for this generated array custom property",
        size=IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
        subtype='NONE',
        default=(False,) * IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
        update=_izom_propui_free_entry_runtime_state_updated,
    )
    default_float_array_color: _izom_propui_free_direct_float_array_color_property(
        'default_float_array',
        name="Default",
        description="Default RGBA color value for this generated custom property",
        defer_storage_write=True,
    )
    min_float: FloatProperty(name="Min", description="Minimum float value for this generated custom property", default=0.0, update=_izom_propui_free_float_range_updated)
    max_float: FloatProperty(name="Max", description="Maximum float value for this generated custom property", default=1.0, update=_izom_propui_free_float_range_updated)
    use_soft_limits: BoolProperty(name="Soft Limits", description="Use separate soft min/max limits in the UI. Enabling this turns off Use Slider", default=False, update=_izom_propui_free_use_soft_limits_updated)
    soft_min_float: FloatProperty(name="Soft Min", description="Soft minimum float value used by the generated custom-property UI", default=0.0, update=_izom_propui_free_float_range_updated)
    soft_max_float: FloatProperty(name="Soft Max", description="Soft maximum float value used by the generated custom-property UI", default=1.0, update=_izom_propui_free_float_range_updated)
    step_float: FloatProperty(name="Step", description="Native Blender float custom-property step metadata. This affects Blender's property metadata, not the generated row layout", default=0.10, min=0.01, max=100.0, update=_izom_propui_free_step_float_updated)
    precision: IntProperty(name="Precision", description="Native Blender float custom-property precision metadata. This affects Blender's property metadata, not the generated row layout", default=3, min=0, max=6, update=_izom_propui_free_entry_runtime_state_updated)
    float_subtype: EnumProperty(name="Subtype", description="Native Blender float custom-property subtype", items=IZOM_PROPUI_FREE_FLOAT_SUBTYPE_ITEMS, default='NONE', update=_izom_propui_free_entry_runtime_state_updated)
    float_array_subtype: EnumProperty(name="Subtype", description="Native Blender float array subtype applied to the generated custom property", items=IZOM_PROPUI_FREE_FLOAT_ARRAY_SUBTYPE_ITEMS, default='NONE', update=_izom_propui_free_float_array_subtype_updated)
    float_array_subtype_cached: StringProperty(name="Cached Float Array Subtype", description="Editor-only previous float-array subtype used for remapping component meaning", default='NONE', options={'HIDDEN'})
    min_int: IntProperty(name="Min", description="Minimum integer value for this generated custom property", default=0, update=_izom_propui_free_int_range_updated)
    max_int: IntProperty(name="Max", description="Maximum integer value for this generated custom property", default=5, update=_izom_propui_free_int_range_updated)
    soft_min_int: IntProperty(name="Soft Min", description="Soft minimum integer value used by the generated custom-property UI", default=0, update=_izom_propui_free_int_range_updated)
    soft_max_int: IntProperty(name="Soft Max", description="Soft maximum integer value used by the generated custom-property UI", default=5, update=_izom_propui_free_int_range_updated)
    step_int: IntProperty(name="Step", description="Native Blender integer custom-property step metadata. This affects Blender's property metadata, not the generated row layout", default=1, min=1, max=100, update=_izom_propui_free_entry_runtime_state_updated)
    array_element_type: EnumProperty(name="Element Type", description="Element type stored by this generated array property", items=IZOM_PROPUI_FREE_ARRAY_ELEMENT_TYPE_ITEMS, default='FLOAT', update=_izom_propui_free_entry_array_shape_updated)
    array_size: IntProperty(name="Size", description="Number of visible elements in this array property", default=4, min=IZOM_PROPUI_FREE_ARRAY_SIZE_MIN, max=IZOM_PROPUI_FREE_ARRAY_SIZE_MAX, update=_izom_propui_free_entry_array_shape_updated)
    library_overridable: BoolProperty(name="Library Overridable", description="Mark this generated custom property as library-overridable", default=True, update=_izom_propui_free_entry_runtime_state_updated)
    ui_order: IntProperty(name="UI Order", description="Internal stored order used by the izom PropUI editor", default=1, options={'HIDDEN'})
    display_order: IntProperty(name="Display Order", description="Internal generated row order used by the generated UI", default=1, min=1, options={'HIDDEN'})
    row_slot: IntProperty(name="Column", description="1-based left-to-right column inside a shared generated row", default=1, min=1, update=_izom_propui_free_row_slot_updated)
    slider: BoolProperty(name="Use Slider", description="Show numeric generated properties and custom IDProperty paths as sliders. Enabling this turns off Soft Limits. Hidden for native RNA paths whose widget style Blender controls internally", default=True, update=_izom_propui_free_slider_updated)
    alert_style: BoolProperty(name="Alert Style", description="Draw this generated property control with Blender's alert styling", default=False, update=_izom_propui_free_entry_runtime_state_updated)
    value_label_layout: EnumProperty(name="Label Layout", description="How scalar labels should be placed in the generated UI", items=IZOM_PROPUI_FREE_VALUE_LABEL_LAYOUT_ITEMS, default='INLINE', update=_izom_propui_free_entry_runtime_state_updated)
    multi_component_layout: EnumProperty(name="Multi-Component Layout", description="How vector-like values should be drawn: inline, with split labels, with label above, or on separate lines inside the same cell", items=IZOM_PROPUI_FREE_MULTI_COMPONENT_LAYOUT_ITEMS, default='INLINE_LABEL', update=_izom_propui_free_entry_runtime_state_updated)
    multi_component_draw_mode: EnumProperty(name="Draw Mode", description="For color and direction subtypes, choose Blender's native whole-value control or individual component fields", items=IZOM_PROPUI_FREE_MULTI_COMPONENT_DRAW_MODE_ITEMS, default='WIDGET', update=_izom_propui_free_entry_runtime_state_updated)
    use_value_labels: BoolProperty(name="Dynamic Labels", description="Change the visible label based on this entry's current value", default=False, update=_izom_propui_free_entry_runtime_state_updated)
    value_labels_use_component: BoolProperty(name="Use One Component", description="For vector, color, integer-array, or boolean-array values, evaluate Dynamic Labels from one chosen component or channel instead of matching the whole value", default=False, update=_izom_propui_free_entry_runtime_state_updated)
    value_labels_component_index: IntProperty(name="Component", description="1-based component or channel used by this entry's Dynamic Labels while Use One Component is enabled", default=1, min=1, max=IZOM_PROPUI_FREE_ARRAY_SIZE_MAX, update=_izom_propui_free_entry_runtime_state_updated)
    use_bool_state_labels: BoolProperty(name="Per State Labels", description="Change the visible label based on whether this boolean is on or off", default=False, update=_izom_propui_free_entry_runtime_state_updated)
    bool_label_true: StringProperty(name="When On", description="Label to show when this boolean is on", default="", maxlen=IZOM_PROPUI_FREE_MAX_LABEL_INPUT_TEXT, update=_izom_propui_free_bool_label_true_updated)
    bool_label_false: StringProperty(name="When Off", description="Label to show when this boolean is off", default="", maxlen=IZOM_PROPUI_FREE_MAX_LABEL_INPUT_TEXT, update=_izom_propui_free_bool_label_false_updated)
    value_labels: CollectionProperty(type=IZOM_PROPUI_FREE_ValueLabel)
    value_labels_active_index: izom_propui_free_session_int_property('value_labels_active_index', default=0, update=_izom_propui_free_entry_value_labels_active_index_updated)
    value_labels_active_uid: izom_propui_free_session_string_property('value_labels_active_uid', default="", options={'HIDDEN'})
    value_labels_selected_uids_json: izom_propui_free_session_string_property('value_labels_selected_uids_json', default="[]", options={'HIDDEN'})
    value_labels_selection_anchor_uid: izom_propui_free_session_string_property('value_labels_selection_anchor_uid', default="", options={'HIDDEN'})
    bool_child_visibility: EnumProperty(name="Show Child", description="When this child entry should be shown, based on its parent boolean value", items=IZOM_PROPUI_FREE_BOOL_VISIBILITY_ITEMS, default='ALWAYS', update=_izom_propui_free_entry_runtime_state_updated)
    number_child_visibility: EnumProperty(name="Show Child", description="When this child entry should be shown, based on its parent numeric value", items=IZOM_PROPUI_FREE_NUMBER_VISIBILITY_ITEMS, default='ALWAYS', update=_izom_propui_free_number_child_visibility_updated)
    visibility_inheritance_depth: IntProperty(name="Chain", description="How many visibility rules this entry uses in the generated UI chain. 1 = parent only, 2 = parent + parent's rule, higher numbers add upstream rules. The editor shows the full parent chain; the generated UI can only use ancestors that are actually present there", default=1, min=1, max=IZOM_PROPUI_FREE_ENTRY_TREE_MAX_DEPTH, update=_izom_propui_free_visibility_inheritance_depth_updated)
    visibility_use_component: BoolProperty(name="Use One Component", description="For vector, color, or integer-array parents, evaluate Child Visibility from one chosen component or channel instead of matching the whole parent value", default=False, update=_izom_propui_free_entry_runtime_state_updated)
    visibility_component_index: IntProperty(name="Component", description="1-based component or channel used by Child Visibility while Use One Component is enabled", default=1, min=1, max=IZOM_PROPUI_FREE_ARRAY_SIZE_MAX, update=_izom_propui_free_entry_runtime_state_updated)
    visibility_match_float: FloatProperty(name="Compare Value", description="Comparison value used against the parent float property", default=0.0, update=_izom_propui_free_visibility_match_float_updated)
    visibility_match_int: IntProperty(name="Compare Value", description="Comparison value used against the parent integer property", default=0, update=_izom_propui_free_visibility_match_int_updated)
    visibility_match_float_array: FloatVectorProperty(name="Compare Float Array", description="Exact float-array value used against a parent array property", size=IZOM_PROPUI_FREE_ARRAY_SIZE_MAX, subtype='NONE', default=(1.0,) * IZOM_PROPUI_FREE_ARRAY_SIZE_MAX, update=_izom_propui_free_entry_array_value_updated)
    visibility_match_int_array: IntVectorProperty(name="Compare Int Array", description="Exact integer-array value used against a parent array property", size=IZOM_PROPUI_FREE_ARRAY_SIZE_MAX, subtype='NONE', default=(0,) * IZOM_PROPUI_FREE_ARRAY_SIZE_MAX, update=_izom_propui_free_entry_runtime_state_updated)
    visibility_match_bool_array: BoolVectorProperty(name="Compare Bool Array", description="Exact boolean-array value used against a parent array property", size=IZOM_PROPUI_FREE_ARRAY_SIZE_MAX, subtype='NONE', default=(False,) * IZOM_PROPUI_FREE_ARRAY_SIZE_MAX, update=_izom_propui_free_entry_runtime_state_updated)
    visibility_match_float_array_color: _izom_propui_free_direct_float_array_color_property('visibility_match_float_array', name="Compare Color", description="Exact RGBA value used against a parent color property", defer_storage_write=True)
    visibility_range_max_float: FloatProperty(name="Range Max", description="Upper bound of the visibility range for the parent float property", default=1.0, update=_izom_propui_free_visibility_range_max_float_updated)
    visibility_range_max_int: IntProperty(name="Range Max", description="Upper bound of the visibility range for the parent integer property", default=0, update=_izom_propui_free_visibility_range_max_int_updated)

_izom_propui_free_add_editor_float_proxy_properties(
    IZOM_PROPUI_FREE_PropertyEntry,
    {
        'default_float': {'name': "Default", 'description': "Default float value for this generated custom property"},
        'min_float': {'name': "Min", 'description': "Minimum float value for this generated custom property"},
        'max_float': {'name': "Max", 'description': "Maximum float value for this generated custom property", 'default': 1.0},
        'soft_min_float': {'name': "Soft Min", 'description': "Soft minimum float value used by the generated custom-property UI"},
        'soft_max_float': {'name': "Soft Max", 'description': "Soft maximum float value used by the generated custom-property UI", 'default': 1.0},
        'step_float': {'name': "Step", 'description': "Native Blender float custom-property step metadata. This does not change the generated UI layout", 'default': 0.1},
        'visibility_match_float': {'name': "Compare Value", 'description': "Comparison value used against the parent float property"},
        'visibility_range_max_float': {'name': "Range Max", 'description': "Upper bound of the visibility range for the parent float property", 'default': 1.0},
    },
)

_izom_propui_free_add_float_array_proxy_properties(
    IZOM_PROPUI_FREE_PropertyEntry,
    {
        'default_float_array': {
            'name': "Default",
            'description': "Default value for this generated float array custom property",
        },
        'visibility_match_float_array': {
            'name': "Compare Value",
            'description': "Exact value used against a parent float array property",
        },
    },
)

_izom_propui_free_add_array_component_proxy_properties(
    IZOM_PROPUI_FREE_PropertyEntry,
    {
        'default_float_array': {
            'name': "Default",
            'description': "Default values for this generated array custom property",
        },
        'default_int_array': {
            'name': "Default",
            'description': "Default values for this generated array custom property",
        },
        'default_bool_array': {
            'name': "Default",
            'description': "Default values for this generated array custom property",
        },
        'visibility_match_float_array': {
            'name': "Compare Value",
            'description': "Exact float-array value used against a parent array property",
        },
        'visibility_match_int_array': {
            'name': "Compare Value",
            'description': "Exact integer-array value used against a parent array property",
        },
        'visibility_match_bool_array': {
            'name': "Compare Value",
            'description': "Exact boolean-array value used against a parent array property",
        },
    },
)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

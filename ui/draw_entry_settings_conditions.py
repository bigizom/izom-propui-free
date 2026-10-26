# SPDX-License-Identifier: GPL-3.0-or-later

from .draw_common import (
    _izom_propui_free_draw_array_prop,
    _izom_propui_free_draw_child_compare_bounds_hint,
    _izom_propui_free_draw_child_compare_component_controls,
    _izom_propui_free_draw_editor_float_prop,
    _izom_propui_free_exact_match_array_meta,
    izom_propui_free_entry_array_field_name,
    izom_propui_free_is_exact_match_value_kind,
    izom_propui_free_is_numeric_value_kind,
)
from .helper_field_clamp_compare import (
    _izom_propui_free_visibility_compare_info,
)
from .helper_validation import (
    _izom_propui_free_entry_visibility_inheritance_info,
)



def _izom_propui_free_draw_exact_match_child_mode(layout, entry, number_attr):
    mode = str(getattr(entry, number_attr, 'ALWAYS') or 'ALWAYS').strip().upper()
    if mode not in {'ALWAYS', 'EQUAL'}:
        mode = 'EQUAL'
    row = layout.row(align=True)
    row.use_property_split = False
    row.use_property_decorate = False
    row.prop_enum(entry, number_attr, 'ALWAYS', text="Always")
    row.prop_enum(entry, number_attr, 'EQUAL', text="Equals")


def _izom_propui_free_draw_child_condition_rule_box(
    column,
    params,
    entry,
    parent,
    *,
    entry_uid,
    label,
    mode,
    compare_info,
    parent_value_kind,
    parent_prop_type,
    inheritance_info,
):
    box = column.box().column(align=True)
    box.label(text=label)

    bool_attr = f"bool_child_{mode}"
    number_attr = f"number_child_{mode}"
    match_float_attr = f"{mode}_match_float"
    range_float_attr = f"{mode}_range_max_float"
    match_int_attr = f"{mode}_match_int"
    range_int_attr = f"{mode}_range_max_int"
    match_text_attr = f"{mode}_match_text"
    use_component_attr = f"{mode}_use_component"
    component_attr = f"{mode}_component_index"
    inheritance_attr = f"{mode}_inheritance_depth"

    if parent_value_kind == 'BOOL':
        box.prop(entry, bool_attr)
    elif parent_value_kind == 'FLOAT':
        box.prop(entry, number_attr)
        if getattr(entry, number_attr) == 'RANGE':
            _izom_propui_free_draw_editor_float_prop(box, entry, match_float_attr, params, text="Range 1")
            _izom_propui_free_draw_editor_float_prop(box, entry, range_float_attr, params, text="Range 2")
        elif getattr(entry, number_attr) != 'ALWAYS':
            _izom_propui_free_draw_editor_float_prop(box, entry, match_float_attr, params)
        if getattr(entry, number_attr) != 'ALWAYS':
            _izom_propui_free_draw_child_compare_bounds_hint(box, compare_info)
    elif parent_value_kind == 'INT':
        box.prop(entry, number_attr)
        if getattr(entry, number_attr) == 'RANGE':
            box.prop(entry, match_int_attr, text="Range 1")
            box.prop(entry, range_int_attr, text="Range 2")
        elif getattr(entry, number_attr) != 'ALWAYS':
            box.prop(entry, match_int_attr)
        if getattr(entry, number_attr) != 'ALWAYS':
            _izom_propui_free_draw_child_compare_bounds_hint(box, compare_info)
    elif parent_value_kind in {'COLOR', 'VECTOR', 'INT_ARRAY', 'BOOL_ARRAY'}:
        component_enabled = _izom_propui_free_draw_child_compare_component_controls(
            box,
            entry,
            compare_info,
            use_component_attr=use_component_attr,
            component_attr=component_attr,
        )
        if component_enabled and parent_prop_type == 'BOOL':
            box.prop(entry, bool_attr)
        elif component_enabled and parent_prop_type in {'FLOAT', 'INT'}:
            box.prop(entry, number_attr)
            if getattr(entry, number_attr) != 'ALWAYS':
                if parent_prop_type == 'FLOAT':
                    if getattr(entry, number_attr) == 'RANGE':
                        _izom_propui_free_draw_editor_float_prop(box, entry, match_float_attr, params, text="Range 1")
                        _izom_propui_free_draw_editor_float_prop(box, entry, range_float_attr, params, text="Range 2")
                    else:
                        _izom_propui_free_draw_editor_float_prop(box, entry, match_float_attr, params)
                else:
                    if getattr(entry, number_attr) == 'RANGE':
                        box.prop(entry, match_int_attr, text="Range 1")
                        box.prop(entry, range_int_attr, text="Range 2")
                    else:
                        box.prop(entry, match_int_attr)
                _izom_propui_free_draw_child_compare_bounds_hint(box, compare_info)
        else:
            _izom_propui_free_draw_exact_match_child_mode(box, entry, number_attr)
            if getattr(entry, number_attr) != 'ALWAYS':
                parent_array_meta = _izom_propui_free_exact_match_array_meta(
                    compare_info.get('parent') if compare_info else parent,
                    parent_value_kind,
                )
                _izom_propui_free_draw_array_prop(
                    box,
                    entry,
                    izom_propui_free_entry_array_field_name(f'{mode}_match', parent_array_meta['element_type']),
                    element_type=parent_array_meta['element_type'],
                    subtype=parent_array_meta['subtype'],
                    size=parent_array_meta['size'],
                    text_label="When Parent Color Is" if parent_array_meta['value_kind'] == 'COLOR' else "When Parent Value Is",
                    color_picker_scope='ENTRY',
                    entry_uid=entry_uid,
                    params=params,
                )
    elif izom_propui_free_is_exact_match_value_kind(parent_value_kind):
        _izom_propui_free_draw_exact_match_child_mode(box, entry, number_attr)
        if getattr(entry, number_attr) != 'ALWAYS':
            box.prop(entry, match_text_attr, text="When Parent Value Is")
    else:
        box.label(text=f"Parent kind is not supported for child {mode}.")

    inheritance_split = box.row(align=True).split(factor=0.44, align=True)
    inheritance_control = inheritance_split.row(align=True)
    inheritance_control.enabled = bool(inheritance_info.get('enabled', False))
    inheritance_control.prop(entry, inheritance_attr, text="Chain", slider=True)
    inheritance_summary = inheritance_split.row(align=True)
    inheritance_summary.alignment = 'LEFT'
    inheritance_summary.label(text=inheritance_info.get('summary_text', 'none'))
    return box


def draw_izom_propui_free_entry_conditions_section(
    column,
    params,
    entry,
    *,
    parent,
    parent_uid,
    entry_uid,
    state,
):
    visibility_compare_info = _izom_propui_free_visibility_compare_info(params, entry, parent=parent)
    visibility_parent_value_kind = (
        str(visibility_compare_info.get('parent_value_kind', '') or '').strip().upper()
        if visibility_compare_info
        else str(parent.get('prop_type', '') or '').strip().upper()
    )
    visibility_parent_prop_type = (
        str(visibility_compare_info.get('parent_prop_type', '') or '').strip().upper()
        if visibility_compare_info
        else str(parent.get('prop_type', '') or '').strip().upper()
    )

    inheritance_info = _izom_propui_free_entry_visibility_inheritance_info(params, entry, state=state)
    vis_box = _izom_propui_free_draw_child_condition_rule_box(
        column,
        params,
        entry,
        parent,
        entry_uid=entry_uid,
        label="Child Visibility",
        mode='visibility',
        compare_info=visibility_compare_info,
        parent_value_kind=visibility_parent_value_kind,
        parent_prop_type=visibility_parent_prop_type,
        inheritance_info=inheritance_info,
    )


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

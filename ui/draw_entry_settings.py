# SPDX-License-Identifier: GPL-3.0-or-later

from types import SimpleNamespace

from .draw_common import (  # noqa: F401
    IZOM_PROPUI_FREE_MAX_LABEL_INPUT_TEXT,
    _izom_propui_free_draw_array_prop,
    _izom_propui_free_draw_editor_float_prop,
    _izom_propui_free_draw_limit_notice_for_prop,
    _izom_propui_free_draw_sub_section,
    _izom_propui_free_entry_display_value_kind,
    _izom_propui_free_resolved_parent_entry,
    izom_propui_free_entry_array_element_type,
    izom_propui_free_entry_array_field_name,
    izom_propui_free_entry_array_size,
    izom_propui_free_entry_array_subtype,
    izom_propui_free_is_exact_match_value_kind,
    izom_propui_free_is_numeric_value_kind,
)
from .draw_entry_settings_sections import (
    _izom_propui_free_entry_settings_hidden_flags,
    _izom_propui_free_entry_settings_section_spec,
)
from .draw_entry_settings_conditions import (
    draw_izom_propui_free_entry_conditions_section,
)
from .draw_entry_settings_dynamic_labels import draw_izom_propui_free_entry_dynamic_labels_section
from .draw_entry_settings_display import draw_izom_propui_free_entry_display_section
from .editor_sections import izom_propui_free_ordered_editor_subsection_specs
from ..core.cache_entries import izom_propui_free_cached_same_type_peer_counts
from ..core.cache_state import (
    izom_propui_free_cached_entry_navigation_bundle,
    izom_propui_free_cached_runtime_parent_lookup,
)
from ..core.constants_serialized import (
    IZOM_PROPUI_FREE_MAX_PROP_ID_TEXT,
    IZOM_PROPUI_FREE_MAX_TOOLTIP_INPUT_TEXT,
)
from ..core.entry_ids import _izom_propui_free_entry_label
from ..core.value_access_entries import izom_propui_free_is_managed_entry



def draw_izom_propui_free_entry_settings(layout, params, entry, *, state=None, lookup=None):
    _draw_izom_propui_free_entry_settings_inner(layout, params, entry, state=state, lookup=lookup)


def _izom_propui_free_entry_settings_context(layout, params, entry, *, state=None, lookup=None):
    layout.use_property_split = True
    layout.use_property_decorate = False

    if state is None:
        state = izom_propui_free_cached_entry_navigation_bundle(params).get('tree_state', {})
    if lookup is None:
        lookup = {}

    parent, parent_uid = _izom_propui_free_resolved_parent_entry(params, entry)
    hidden_sections = _izom_propui_free_entry_settings_hidden_flags(params)
    entry_uid = str(getattr(entry, 'uid', '') or '').strip()
    entry_prop_type = str(getattr(entry, 'prop_type', 'FLOAT') or 'FLOAT').strip().upper()
    runtime_entry = lookup.get(entry_uid) if isinstance(lookup, dict) and entry_uid else None
    entry_value_kind = _izom_propui_free_entry_display_value_kind(entry, runtime_entry=runtime_entry)
    text_role = str(getattr(entry, 'text_role', 'TEXT') or 'TEXT').strip().upper()
    is_text_entry = entry_prop_type == 'TEXT'
    display_prop_type = entry_prop_type
    is_managed_entry = bool(izom_propui_free_is_managed_entry(entry))
    is_numeric_entry = bool(izom_propui_free_is_numeric_value_kind(entry_value_kind))
    is_exact_match_entry = bool(izom_propui_free_is_exact_match_value_kind(entry_value_kind))

    return SimpleNamespace(
        layout=layout,
        params=params,
        entry=entry,
        state=state,
        lookup=lookup,
        parent=parent,
        parent_uid=parent_uid,
        hide_basics=hidden_sections['basics'],
        hide_value=hidden_sections['value'],
        hide_display=hidden_sections['display'],
        hide_dynamic_labels=hidden_sections['dynamic_labels'],
        hide_conditions=hidden_sections['conditions'],
        hide_storage=hidden_sections['storage'],
        hide_tools=True,
        hide_copy_settings=True,
        hide_import_export=True,
        entry_uid=entry_uid,
        entry_prop_type=entry_prop_type,
        runtime_entry=runtime_entry,
        entry_value_kind=entry_value_kind,
        text_role=text_role,
        is_text_entry=is_text_entry,
        display_prop_type=display_prop_type,
        is_managed_entry=is_managed_entry,
        is_numeric_entry=is_numeric_entry,
        is_exact_match_entry=is_exact_match_entry,
        is_bool_entry=entry_value_kind == 'BOOL',
        supports_bool_style=entry_value_kind in {'BOOL', 'BOOL_ARRAY'},
        is_multi_component_entry=display_prop_type == 'ARRAY',
    )


def _izom_propui_free_entry_settings_runtime_lookup(ctx):
    if isinstance(ctx.lookup, dict) and ctx.lookup:
        return ctx.lookup
    return izom_propui_free_cached_runtime_parent_lookup(ctx.params)


def _draw_izom_propui_free_entry_settings_inner(layout, params, entry, *, state=None, lookup=None):
    ctx = _izom_propui_free_entry_settings_context(layout, params, entry, state=state, lookup=lookup)
    for selected_spec in izom_propui_free_ordered_editor_subsection_specs(params, 'SELECTED_ENTRY'):
        _izom_propui_free_draw_selected_entry_section(
            ctx,
            str(selected_spec.get('key', '') or '').strip().upper(),
        )


def _izom_propui_free_draw_selected_entry_section(ctx, section_key):
    if section_key == 'SELECTED_BASICS':
        if not ctx.hide_basics:
            _izom_propui_free_draw_entry_basics_section(ctx)
        return
    if section_key == 'SELECTED_VALUE':
        if _izom_propui_free_entry_settings_show_value_section(ctx):
            _izom_propui_free_draw_entry_collapsible_section(
                ctx,
                'value',
                _izom_propui_free_draw_entry_value_section,
                title="Value",
                icon='PROPERTIES',
            )
        return
    if section_key == 'SELECTED_DISPLAY':
        if not ctx.hide_display:
            _izom_propui_free_draw_entry_collapsible_section(ctx, 'display', _izom_propui_free_draw_display_section)
        return
    if section_key == 'SELECTED_DYNAMIC_LABELS':
        if not ctx.hide_dynamic_labels:
            _izom_propui_free_draw_entry_collapsible_section(
                ctx,
                'dynamic_labels',
                _izom_propui_free_draw_dynamic_labels_section,
            )
        return
    if section_key == 'SELECTED_CONDITIONS':
        if not ctx.hide_conditions and ctx.parent:
            _izom_propui_free_draw_entry_collapsible_section(ctx, 'conditions', _izom_propui_free_draw_conditions_section)
        return
    if section_key == 'SELECTED_STORAGE':
        if not ctx.hide_storage and ctx.is_managed_entry:
            _izom_propui_free_draw_entry_collapsible_section(ctx, 'storage', _izom_propui_free_draw_storage_section)
        return


def _izom_propui_free_entry_settings_show_value_section(ctx):
    return bool(
        not ctx.hide_value
        and ctx.is_managed_entry
    )


def _izom_propui_free_draw_entry_collapsible_section(ctx, key, callback, *, title=None, icon=None):
    spec = _izom_propui_free_entry_settings_section_spec(key)
    box = _izom_propui_free_draw_sub_section(
        ctx.layout,
        ctx.params,
        spec['expanded_attr'],
        title or spec['title'],
        icon or spec['icon'],
    )
    if box is not None:
        callback(ctx, box)


def _izom_propui_free_draw_entry_basics_section(ctx):
    basics = ctx.layout.box().column(align=True)
    basics.label(text="Basics", icon='DOT')
    _izom_propui_free_draw_entry_parent_control(ctx, basics)
    basics.prop(ctx.entry, "prop_type")
    basics.prop(ctx.entry, "editor_label", text="Editor Label")
    _izom_propui_free_draw_limit_notice_for_prop(
        basics,
        ctx.entry,
        "editor_label",
        IZOM_PROPUI_FREE_MAX_LABEL_INPUT_TEXT,
    )
    if ctx.is_text_entry:
        _izom_propui_free_draw_text_entry_basics(ctx, basics)
    else:
        _izom_propui_free_draw_regular_entry_basics(ctx, basics)


def _izom_propui_free_draw_entry_parent_control(ctx, basics):
    parent_name = _izom_propui_free_entry_label(ctx.parent) if ctx.parent else 'None'
    row = basics.row(align=True)
    split = row.split(factor=0.4, align=True)
    label_col = split.row(align=True)
    label_col.alignment = 'RIGHT'
    label_col.label(text="Parent")
    control_row = split.row(align=True)
    control_row.menu("IZOM_PROPUI_FREE_MT_set_parent", text=parent_name)
    if ctx.parent:
        control_row.operator("wm.izom_propui_free_clear_parent", text="", icon='UNLINKED')


def _izom_propui_free_draw_text_entry_basics(ctx, basics):
    if ctx.text_role == 'TEXT':
        basics.prop(ctx.entry, "label", text="Text")
        _izom_propui_free_draw_limit_notice_for_prop(basics, ctx.entry, "label", IZOM_PROPUI_FREE_MAX_LABEL_INPUT_TEXT)


def _izom_propui_free_draw_regular_entry_basics(ctx, basics):
    basics.prop(ctx.entry, "label")
    _izom_propui_free_draw_limit_notice_for_prop(basics, ctx.entry, "label", IZOM_PROPUI_FREE_MAX_LABEL_INPUT_TEXT)
    basics.prop(ctx.entry, "description")
    _izom_propui_free_draw_limit_notice_for_prop(basics, ctx.entry, "description", IZOM_PROPUI_FREE_MAX_TOOLTIP_INPUT_TEXT)
    if ctx.is_managed_entry:
        basics.prop(ctx.entry, "prop_id", text="Property ID")
        _izom_propui_free_draw_limit_notice_for_prop(basics, ctx.entry, "prop_id", IZOM_PROPUI_FREE_MAX_PROP_ID_TEXT)


def _izom_propui_free_draw_entry_value_section(ctx, column):
    if ctx.is_managed_entry:
        _izom_propui_free_draw_managed_entry_value_section(ctx, column)


def _izom_propui_free_draw_managed_entry_value_section(ctx, column):
    if ctx.entry_prop_type == 'FLOAT':
        _izom_propui_free_draw_float_value_controls(column, ctx.entry, ctx.params)
    elif ctx.entry_prop_type == 'INT':
        _izom_propui_free_draw_int_value_controls(column, ctx.entry)
    elif ctx.entry_prop_type == 'ARRAY':
        _izom_propui_free_draw_array_value_controls(ctx, column)
    else:
        column.prop(ctx.entry, "default_bool", text="Default Value")


def _izom_propui_free_draw_float_value_controls(column, entry, params):
    _izom_propui_free_draw_editor_float_prop(column, entry, "default_float", params, text="Default Value")
    row = column.row(align=True)
    _izom_propui_free_draw_editor_float_prop(row, entry, "min_float", params, text="Min")
    _izom_propui_free_draw_editor_float_prop(row, entry, "max_float", params, text="Max")
    column.prop(entry, "use_soft_limits")
    if entry.use_soft_limits:
        row = column.row(align=True)
        _izom_propui_free_draw_editor_float_prop(row, entry, "soft_min_float", params, text="Soft Min")
        _izom_propui_free_draw_editor_float_prop(row, entry, "soft_max_float", params, text="Soft Max")
    _izom_propui_free_draw_editor_float_prop(column, entry, "step_float", params, text="Step")
    column.prop(entry, "precision")
    column.prop(entry, "float_subtype", text="Subtype")


def _izom_propui_free_draw_int_value_controls(column, entry):
    column.prop(entry, "default_int", text="Default Value")
    row = column.row(align=True)
    row.prop(entry, "min_int", text="Min")
    row.prop(entry, "max_int", text="Max")
    column.prop(entry, "use_soft_limits")
    if entry.use_soft_limits:
        row = column.row(align=True)
        row.prop(entry, "soft_min_int", text="Soft Min")
        row.prop(entry, "soft_max_int", text="Soft Max")
    column.prop(entry, "step_int", text="Step")


def _izom_propui_free_draw_array_value_controls(ctx, column):
    array_element_type = (
        izom_propui_free_entry_array_element_type(ctx.entry, 'FLOAT')
        if ctx.entry_prop_type == 'ARRAY'
        else 'FLOAT'
    )
    array_subtype = izom_propui_free_entry_array_subtype(ctx.entry, 'NONE')
    array_size = izom_propui_free_entry_array_size(ctx.entry, 4)
    if ctx.entry_prop_type == 'ARRAY':
        column.prop(ctx.entry, "array_element_type")
        column.prop(ctx.entry, "array_size")
    if array_element_type == 'FLOAT':
        column.prop(ctx.entry, "float_array_subtype", text="Subtype")
    _izom_propui_free_draw_array_prop(
        column,
        ctx.entry,
        izom_propui_free_entry_array_field_name('default', array_element_type),
        element_type=array_element_type,
        subtype=array_subtype,
        size=array_size,
        text_label="Default Value",
        color_picker_scope='ENTRY',
        entry_uid=ctx.entry_uid,
        params=ctx.params,
    )
    is_color_array = (
        array_element_type == 'FLOAT'
        and str(array_subtype or 'NONE').strip().upper().startswith('COLOR')
    )
    if array_element_type == 'FLOAT' and not is_color_array:
        _izom_propui_free_draw_float_array_limit_controls(column, ctx.entry, ctx.params)
    elif array_element_type == 'INT':
        _izom_propui_free_draw_int_array_limit_controls(column, ctx.entry)


def _izom_propui_free_draw_float_array_limit_controls(column, entry, params):
    row = column.row(align=True)
    _izom_propui_free_draw_editor_float_prop(row, entry, "min_float", params, text="Min")
    _izom_propui_free_draw_editor_float_prop(row, entry, "max_float", params, text="Max")
    column.prop(entry, "use_soft_limits")
    if entry.use_soft_limits:
        row = column.row(align=True)
        _izom_propui_free_draw_editor_float_prop(row, entry, "soft_min_float", params, text="Soft Min")
        _izom_propui_free_draw_editor_float_prop(row, entry, "soft_max_float", params, text="Soft Max")
    _izom_propui_free_draw_editor_float_prop(column, entry, "step_float", params, text="Step")
    column.prop(entry, "precision")


def _izom_propui_free_draw_int_array_limit_controls(column, entry):
    row = column.row(align=True)
    row.prop(entry, "min_int", text="Min")
    row.prop(entry, "max_int", text="Max")
    column.prop(entry, "use_soft_limits")
    if entry.use_soft_limits:
        row = column.row(align=True)
        row.prop(entry, "soft_min_int", text="Soft Min")
        row.prop(entry, "soft_max_int", text="Soft Max")
    column.prop(entry, "step_int", text="Step")


def _izom_propui_free_draw_display_section(ctx, column):
    draw_izom_propui_free_entry_display_section(
        column,
        ctx.params,
        ctx.entry,
        entry_uid=ctx.entry_uid,
        entry_value_kind=ctx.entry_value_kind,
        is_text_entry=ctx.is_text_entry,
        is_multi_component_entry=ctx.is_multi_component_entry,
        supports_bool_style=ctx.supports_bool_style,
        is_bool_entry=ctx.is_bool_entry,
    )


def _izom_propui_free_draw_dynamic_labels_section(ctx, column):
    if ctx.is_text_entry:
        column.label(text="No dynamic label controls for text entries.")
        return
    draw_izom_propui_free_entry_dynamic_labels_section(
        column,
        ctx.params,
        ctx.entry,
        entry_value_kind=ctx.entry_value_kind,
        is_text_entry=ctx.is_text_entry,
        is_bool_entry=ctx.is_bool_entry,
        is_numeric_entry=ctx.is_numeric_entry,
        is_exact_match_entry=ctx.is_exact_match_entry,
        runtime_lookup=lambda: _izom_propui_free_entry_settings_runtime_lookup(ctx),
    )


def _izom_propui_free_draw_storage_section(ctx, column):
    if not ctx.is_managed_entry:
        column.label(text="No generated custom-property storage for this entry.")
        return
    column.label(text="Uses the Object property storage from Output Setup.", icon='LINKED')
    column.prop(ctx.entry, "library_overridable")


def _izom_propui_free_draw_conditions_section(ctx, column):
    draw_izom_propui_free_entry_conditions_section(
        column,
        ctx.params,
        ctx.entry,
        parent=ctx.parent,
        parent_uid=ctx.parent_uid,
        entry_uid=ctx.entry_uid,
        state=ctx.state,
    )

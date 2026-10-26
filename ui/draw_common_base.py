# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from ..core.diagnostics import izom_propui_free_log_recovered

from ..core.constants import (
    IZOM_PROPUI_FREE_STANDALONE_MULTI_COMPONENT_LABEL_ABOVE_LAYOUT_IDS,
    izom_propui_free_subtype_supports_native_control,
)
from ..core.value_access import (
    izom_propui_free_entry_array_element_type,
    izom_propui_free_entry_array_subtype,
    izom_propui_free_entry_value_kind,
    izom_propui_free_uses_scalar_label_layout,
)
from .helpers import (
    _izom_propui_free_data_value,
    _izom_propui_free_draw_char_limit_notice,
)




def _izom_propui_free_entry_native_control_subtype(entry, value_kind):
    normalized_kind = str(value_kind or 'NONE').strip().upper() or 'NONE'
    if normalized_kind not in {'VECTOR', 'COLOR'}:
        return 'NONE'

    prop_type = str(getattr(entry, 'prop_type', 'FLOAT') or 'FLOAT').strip().upper()
    if prop_type == 'ARRAY':
        element_type = izom_propui_free_entry_array_element_type(entry, 'FLOAT') if prop_type == 'ARRAY' else 'FLOAT'
        if element_type != 'FLOAT':
            return 'NONE'
        fallback_subtype = 'COLOR' if normalized_kind == 'COLOR' else 'NONE'
        return izom_propui_free_entry_array_subtype(entry, fallback_subtype)

    return 'NONE'


def _izom_propui_free_entry_supports_native_control_draw_mode(entry, value_kind):
    return izom_propui_free_subtype_supports_native_control(
        _izom_propui_free_entry_native_control_subtype(entry, value_kind)
    )


def _izom_propui_free_draw_limit_notice_for_prop(layout, owner, attr_name, limit):
    try:
        value = getattr(owner, attr_name, '')
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        value = ''
    _izom_propui_free_draw_char_limit_notice(layout, value, limit)


def _izom_propui_free_draw_sub_section(layout, params, prop_name, title, icon='NONE'):
    """Draw a collapsible sub-section. Returns column to draw into, or None if collapsed."""
    box = layout.box()
    header = box.row()
    header.use_property_split = False
    header.use_property_decorate = False
    header.alignment = 'EXPAND'
    try:
        expanded = bool(getattr(params, prop_name, True))
        toggle_icon = 'TRIA_DOWN' if expanded else 'TRIA_RIGHT'
        toggle = header.operator(
            "wm.izom_propui_free_toggle_editor_expanded",
            text=title,
            icon=toggle_icon,
            emboss=False,
        )
        toggle.property_name = prop_name
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        expanded = True
        header.label(text=title, icon=icon)
    if not expanded:
        return None
    return box.column(align=True)


def _izom_propui_free_template_list_rows(item_count, *, preferred_rows=4, max_rows=8, min_rows=1):
    try:
        count = max(0, int(item_count or 0))
    except (TypeError, ValueError):
        count = 0

    min_rows = max(1, int(min_rows))
    preferred_rows = max(min_rows, int(preferred_rows))
    max_rows = max(preferred_rows, int(max_rows))

    if count <= 0:
        return min_rows, min_rows

    # Blender treats `rows` as the minimum visible height and `maxrows` as the
    # expandable upper bound. To let lists genuinely shrink to one row while
    # still growing when there is room, keep `rows` pinned to the minimum and
    # only clamp the expansion target by collection size.
    rows = min(min_rows, count)
    maxrows = max(rows, min(max_rows, count))
    return rows, maxrows


def _izom_propui_free_runtime_entry_value(runtime_entry, entry, field_name, default=None):
    if isinstance(runtime_entry, dict) and field_name in runtime_entry:
        return runtime_entry.get(field_name, default)
    return getattr(entry, field_name, default)


def _izom_propui_free_entry_display_value_kind(entry, *, runtime_entry=None):
    cached_kind = ''
    if isinstance(runtime_entry, dict):
        cached_kind = str(runtime_entry.get('value_kind', '') or '').strip().upper()
    if cached_kind:
        return cached_kind
    return str(
        izom_propui_free_entry_value_kind(entry, str(_izom_propui_free_data_value(entry, 'prop_type', 'FLOAT') or 'FLOAT'))
        or 'NONE'
    ).strip().upper() or 'NONE'


def _izom_propui_free_component_mapping_text(component_meta):
    labels = tuple(component_meta.get('labels', ()) or ())
    if not labels:
        return ""
    preview = [f"{index + 1}={label}" for index, label in enumerate(labels[:8])]
    if len(labels) > 8:
        preview.append('...')
    return "Components: " + ", ".join(preview)


def _izom_propui_free_draw_child_compare_bounds_hint(layout, compare_info):
    if not compare_info:
        return
    compare_prop_type = str(compare_info.get('parent_prop_type', '') or '').strip().upper()
    low = compare_info.get('min_value')
    high = compare_info.get('max_value')
    if compare_prop_type not in {'FLOAT', 'INT'} or low is None or high is None:
        return
    if compare_prop_type == 'INT':
        bounds_text = f"Parent range: {int(low)} to {int(high)}"
    else:
        bounds_text = f"Parent range: {float(low):g} to {float(high):g}"
    hint_row = layout.row(align=True)
    hint_row.label(text=bounds_text, icon='INFO')


def _izom_propui_free_draw_child_compare_component_controls(layout, entry, compare_info, *, use_component_attr, component_attr):
    component_meta = compare_info.get('component_meta', {}) if compare_info else {}
    if not bool(component_meta.get('supported', False)):
        return False

    layout.prop(entry, use_component_attr, text="Use One Component")
    if not bool(getattr(entry, use_component_attr, False)):
        return False

    component_box = layout.box().column(align=True)
    component_box.prop(entry, component_attr, text="Component")
    component_text = _izom_propui_free_component_mapping_text(component_meta)
    if component_text:
        component_box.label(text=component_text)
    return True

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

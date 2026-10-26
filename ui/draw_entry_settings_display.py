# SPDX-License-Identifier: GPL-3.0-or-later

from .draw_common import (
    _izom_propui_free_draw_text_block_controls,
    _izom_propui_free_entry_supports_native_control_draw_mode,
    izom_propui_free_entry_component_meta,
    izom_propui_free_uses_scalar_label_layout,
)
from ..core.constants_display import (
    IZOM_PROPUI_FREE_NATIVE_MULTI_COMPONENT_LAYOUT_IDS,
    IZOM_PROPUI_FREE_STANDALONE_MULTI_COMPONENT_LABEL_ABOVE_LAYOUT_IDS,
    izom_propui_free_normalize_multi_component_draw_mode,
)
from ..core.value_access_entries import izom_propui_free_entry_slider_control_available



def draw_izom_propui_free_entry_display_section(
    column,
    params,
    entry,
    *,
    entry_uid,
    entry_value_kind,
    is_text_entry,
    is_multi_component_entry,
    supports_bool_style,
    is_bool_entry,
):
    if is_text_entry:
        _izom_propui_free_draw_text_block_controls(
            column,
            params,
            entry,
            text_label="Text",
            target_scope='ENTRY',
            entry_uid=entry_uid,
            show_text_field=False,
        )
    else:
        alert_row = column.row(align=True)
        alert_row.alert = bool(getattr(entry, 'alert_style', False))
        alert_row.prop(entry, "alert_style")
        supports_native_control_draw_mode = _izom_propui_free_entry_supports_native_control_draw_mode(
            entry,
            entry_value_kind,
        )
        display_layout_mode = str(getattr(entry, 'multi_component_layout', 'INLINE') or 'INLINE').strip().upper()
        component_meta = (
            izom_propui_free_entry_component_meta(entry, entry_value_kind)
            if is_multi_component_entry
            else {}
        )
        uses_component_draw_mode = (
            True
            if (
                not supports_native_control_draw_mode
                or display_layout_mode not in IZOM_PROPUI_FREE_NATIVE_MULTI_COMPONENT_LAYOUT_IDS
            )
            else izom_propui_free_normalize_multi_component_draw_mode(
                getattr(entry, 'multi_component_draw_mode', 'WIDGET')
            ) == 'COMPONENTS'
        )
        slider_supported = izom_propui_free_entry_slider_control_available(
            entry,
            entry_value_kind,
            uses_component_draw_mode=uses_component_draw_mode,
        )
        if slider_supported:
            slider_row = column.row(align=True)
            slider_row.prop(entry, "slider")
        scalar_label_layout_entry = izom_propui_free_uses_scalar_label_layout(entry_value_kind)
        if scalar_label_layout_entry:
            column.prop(entry, "value_label_layout", text="Label Layout")
        scalar_label_above = bool(
            scalar_label_layout_entry
            and str(getattr(entry, 'value_label_layout', 'INLINE') or 'INLINE').strip().upper() == 'LABEL_ABOVE'
        )
        multi_component_label_above = False
        if is_multi_component_entry:
            column.prop(entry, "multi_component_layout", text="Multi-Component Layout")
            multi_component_layout = str(getattr(entry, 'multi_component_layout', 'INLINE') or 'INLINE').strip().upper()
            if (
                supports_native_control_draw_mode
                and multi_component_layout in IZOM_PROPUI_FREE_NATIVE_MULTI_COMPONENT_LAYOUT_IDS
            ):
                column.prop(entry, "multi_component_draw_mode", text="Draw Mode")
                uses_component_draw_mode = (
                    izom_propui_free_normalize_multi_component_draw_mode(
                        getattr(entry, 'multi_component_draw_mode', 'WIDGET')
                    ) == 'COMPONENTS'
                )
            multi_component_label_above = (
                multi_component_layout in IZOM_PROPUI_FREE_STANDALONE_MULTI_COMPONENT_LABEL_ABOVE_LAYOUT_IDS
            )


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

# SPDX-License-Identifier: GPL-3.0-or-later

from .draw_common import (
    IZOM_PROPUI_FREE_MAX_LABEL_INPUT_TEXT,
    _izom_propui_free_draw_limit_notice_for_prop,
    _izom_propui_free_draw_value_label_box,
    izom_propui_free_entry_component_meta,
)
from .helper_value_labels import _izom_propui_free_value_label_reference_entry


def draw_izom_propui_free_entry_dynamic_labels_section(
    column,
    params,
    entry,
    *,
    entry_value_kind,
    is_text_entry,
    is_bool_entry,
    is_numeric_entry,
    is_exact_match_entry,
    runtime_lookup,
):
    dynamic_reference_entry = _izom_propui_free_value_label_reference_entry(params, entry) or entry
    if is_text_entry:
        column.label(text="No dynamic label controls for text entries.")
    elif is_bool_entry:
        column.prop(entry, "use_bool_state_labels")
        if entry.use_bool_state_labels:
            box = column.box().column(align=True)
            box.prop(entry, "bool_label_false")
            _izom_propui_free_draw_limit_notice_for_prop(box, entry, "bool_label_false", IZOM_PROPUI_FREE_MAX_LABEL_INPUT_TEXT)
            box.prop(entry, "bool_label_true")
            _izom_propui_free_draw_limit_notice_for_prop(box, entry, "bool_label_true", IZOM_PROPUI_FREE_MAX_LABEL_INPUT_TEXT)
    elif is_numeric_entry or is_exact_match_entry:
        column.prop(entry, "use_value_labels")
        if entry.use_value_labels:
            value_label_component_meta = izom_propui_free_entry_component_meta(dynamic_reference_entry, entry_value_kind)
            footer_text = "Rows are checked top to bottom. The first matching row wins."
            if is_numeric_entry:
                footer_text = "Rows are checked top to bottom. The first matching row wins. Numeric rows can match Equals, At Least, At Most, or In Range."
            elif bool(value_label_component_meta.get('supported', False)):
                footer_text = "Rows are checked top to bottom. The first matching row wins. Each row can match the full value or choose one component."
            _izom_propui_free_draw_value_label_box(
                column,
                params,
                runtime_lookup(),
                "Dynamic Labels",
                entry,
                'value_labels',
                entry_value_kind,
                target_mode='SELF',
                footer_text=footer_text,
                bounds_entry=dynamic_reference_entry,
            )
    else:
        column.label(text="No dynamic label controls for this entry type.")


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

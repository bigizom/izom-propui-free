# SPDX-License-Identifier: GPL-3.0-or-later



def draw_izom_propui_free_icon_picker(layout, owner, prop_name, *, label, target_scope, entry_uid='', value_label_uid='', target_mode='SELF'):
    row = layout.row(align=True)
    current_icon = izom_propui_free_display_icon(getattr(owner, prop_name, 'NONE'), 'NONE')
    row.prop(owner, prop_name, text=label, icon=current_icon)
    op = row.operator(
        "wm.izom_propui_free_pick_icon",
        text="",
        icon='VIEWZOOM',
    )
    op.target_scope = str(target_scope or 'ENTRY').strip().upper() or 'ENTRY'
    op.entry_uid = str(entry_uid or '').strip()
    op.value_label_uid = str(value_label_uid or '').strip()
    op.target_mode = str(target_mode or 'SELF').strip().upper() or 'SELF'
    op.prop_name = str(prop_name or '').strip()
    op.initial_icon_value = current_icon
    return row


def _izom_propui_free_draw_text_block_controls(
    layout,
    params,
    item,
    *,
    text_label='Text',
    target_scope='ENTRY',
    entry_uid='',
    value_label_uid='',
    target_mode='SELF',
    show_text_field=True,
):
    text_role = str(getattr(item, 'text_role', 'TEXT') or 'TEXT').strip().upper()

    layout.prop(item, "text_role", text="Role")
    if text_role == 'TEXT' and show_text_field:
        layout.prop(item, "label", text=text_label)
        _izom_propui_free_draw_limit_notice_for_prop(layout, item, "label", IZOM_PROPUI_FREE_MAX_LABEL_INPUT_TEXT)

    if text_role != 'TEXT':
        return None

    style_box = layout.box().column(align=True)
    style_box.label(text="Display Style")
    style_box.prop(item, "text_alignment", text="Alignment")
    style_box.prop(item, "text_alert", text="Alert Style")
    icon_hug_enabled = str(getattr(item, 'text_alignment', 'LEFT') or 'LEFT').strip().upper() == 'CENTER'
    before_icon_row = draw_izom_propui_free_icon_picker(
        style_box,
        item,
        "text_icon",
        label="Before Icon",
        target_scope=target_scope,
        entry_uid=entry_uid,
        value_label_uid=value_label_uid,
        target_mode=target_mode,
    )
    before_hug_row = before_icon_row.row(align=True)
    before_hug_row.enabled = icon_hug_enabled
    before_hug_row.prop(item, "text_icon_hug_text", text="Hug Text")
    after_icon_row = draw_izom_propui_free_icon_picker(
        style_box,
        item,
        "text_icon_after",
        label="After Icon",
        target_scope=target_scope,
        entry_uid=entry_uid,
        value_label_uid=value_label_uid,
        target_mode=target_mode,
    )
    after_hug_row = after_icon_row.row(align=True)
    after_hug_row.enabled = icon_hug_enabled
    after_hug_row.prop(item, "text_icon_after_hug_text", text="Hug Text")
    return style_box


def _izom_propui_free_resolved_parent_entry(params, entry):
    parent_uid = str(getattr(entry, 'parent_uid', '') or '').strip()
    if not parent_uid:
        return None, ''

    resolved_parent = _izom_propui_free_entry_by_uid(params, parent_uid) if params is not None else None
    return resolved_parent, parent_uid


def _izom_propui_free_draw_compact_footer_text(layout, footer_text):
    text = str(footer_text or '').strip()
    if not text:
        return
    footer_col = layout.column(align=True)
    footer_col.separator()
    lines = textwrap.wrap(text, width=96) or [text]
    for index, line in enumerate(lines):
        footer_col.label(text=line, icon='INFO' if index == 0 else 'BLANK1')

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401
import textwrap
from ..core.constants_serialized import IZOM_PROPUI_FREE_MAX_LABEL_INPUT_TEXT
from ..core.text import izom_propui_free_display_icon
from .draw_common_base import _izom_propui_free_draw_limit_notice_for_prop
from .helper_selection_common import _izom_propui_free_entry_by_uid


__all__ = izom_propui_free_public_names(globals(), all_public=True)

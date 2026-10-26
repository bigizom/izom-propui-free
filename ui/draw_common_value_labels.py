# SPDX-License-Identifier: GPL-3.0-or-later

from .draw_common_controls import (
    IZOM_PROPUI_FREE_MAX_LABEL_INPUT_TEXT,
    _izom_propui_free_draw_compact_footer_text,
    _izom_propui_free_draw_limit_notice_for_prop,
)
from ..core.value_access_common import (
    izom_propui_free_is_exact_match_value_kind,
    izom_propui_free_is_numeric_value_kind,
)
from ..core.value_access_entries import (
    izom_propui_free_entry_component_meta,
)
from .draw_common_arrays import _izom_propui_free_draw_value_match_prop
from .draw_common_base import (
    _izom_propui_free_component_mapping_text,
    _izom_propui_free_template_list_rows,
)
from .helper_selection_collections import _izom_propui_free_active_collection_item
from .helper_value_labels_source import (
    _izom_propui_free_component_slot_value,
    _izom_propui_free_entry_component_rule_info,
)



def _izom_propui_free_draw_value_label_box(parent_col, params, lookup, box_title, owner, collection_attr, source_type, *, target_mode='SELF', value_label_text='Label', footer_text='', bounds_entry=None):
    _izom_propui_free_draw_value_label_box_inner(parent_col, params, lookup, box_title, owner, collection_attr, source_type, target_mode=target_mode, value_label_text=value_label_text, footer_text=footer_text, bounds_entry=bounds_entry)


def _izom_propui_free_draw_value_label_box_inner(parent_col, params, lookup, box_title, owner, collection_attr, source_type, *, target_mode='SELF', value_label_text='Label', footer_text='', bounds_entry=None):
    box = parent_col.box()
    if box_title:
        box.label(text=box_title)
    collection = getattr(owner, collection_attr, None) or []
    current = _izom_propui_free_active_collection_item(owner, collection_attr)

    list_row = box.row()
    list_col = list_row.column(align=True)
    value_label_rows, value_label_maxrows = _izom_propui_free_template_list_rows(
        len(collection),
        preferred_rows=2,
        max_rows=6,
    )
    active_field = f"{collection_attr}_active_index"
    list_col.template_list(
        "IZOM_PROPUI_FREE_UL_value_labels",
        f"{collection_attr}_{target_mode}",
        owner,
        collection_attr,
        owner,
        active_field,
        rows=value_label_rows,
        maxrows=value_label_maxrows,
    )

    buttons = list_row.column(align=True)
    owner_uid = str(getattr(owner, 'uid', '') or '').strip()
    op = buttons.operator("wm.izom_propui_free_add_value_label", icon='ADD', text="")
    op.target_mode = target_mode
    op.entry_uid = owner_uid
    op = buttons.operator("wm.izom_propui_free_remove_value_label", icon='REMOVE', text="")
    op.target_mode = target_mode
    op.entry_uid = owner_uid
    op = buttons.operator("wm.izom_propui_free_duplicate_value_label", icon='DUPLICATE', text="")
    op.target_mode = target_mode
    op.entry_uid = owner_uid
    buttons.separator()
    op = buttons.operator("wm.izom_propui_free_move_value_label", icon='TRIA_UP', text="")
    op.direction = 'UP'
    op.target_mode = target_mode
    op.entry_uid = owner_uid
    op = buttons.operator("wm.izom_propui_free_move_value_label", icon='TRIA_DOWN', text="")
    op.direction = 'DOWN'
    op.target_mode = target_mode
    op.entry_uid = owner_uid
    buttons.separator()
    value_label_tools_menu = {
        'SELF': "IZOM_PROPUI_FREE_MT_value_label_tools_self",
    }.get(str(target_mode or 'SELF').strip().upper(), "IZOM_PROPUI_FREE_MT_value_label_tools_self")
    buttons.menu(value_label_tools_menu, icon='DOWNARROW_HLT', text="")

    if current is not None:
        detail = box.column(align=True)
        source_value_kind = str(source_type or '').strip().upper()
        effective_source_type = source_value_kind
        if target_mode == 'SELF':
            self_reference_entry = bounds_entry if bounds_entry is not None else owner
            self_component_info = _izom_propui_free_entry_component_rule_info(owner, current, reference_entry=self_reference_entry)
            self_component_meta = self_component_info.get('component_meta', {}) if isinstance(self_component_info, dict) else {}
            entry_use_component = bool(getattr(owner, 'value_labels_use_component', False))
            if entry_use_component != bool(getattr(self_reference_entry, 'value_labels_use_component', False)):
                self_component_info = dict(self_component_info)
                row_use_component = bool(getattr(current, 'use_source_component', False))
                component_slot = (
                    _izom_propui_free_component_slot_value(
                        current,
                        'source_component_index',
                        self_component_meta.get('size', 1),
                    )
                    if row_use_component
                    else _izom_propui_free_component_slot_value(
                        owner,
                        'value_labels_component_index',
                        self_component_meta.get('size', 1),
                    )
                )
                self_component_info['use_component'] = bool(self_component_meta.get('supported', False)) and (row_use_component or entry_use_component)
                self_component_info['component_slot'] = component_slot
            if bool(self_component_meta.get('supported', False)):
                detail.prop(current, "use_source_component", text="Use One Component")
                if bool(getattr(current, 'use_source_component', False)):
                    component_box = detail.box().column(align=True)
                    component_box.prop(current, "source_component_index", text="Component")
                    component_text = _izom_propui_free_component_mapping_text(self_component_meta)
                    if component_text:
                        component_box.label(text=component_text)
            if bool(self_component_info.get('use_component', False)):
                effective_source_type = str(self_component_meta.get('component_kind', source_value_kind) or source_value_kind).strip().upper() or source_value_kind
        supports_self_value_rules = (
            izom_propui_free_is_numeric_value_kind(effective_source_type)
            or effective_source_type == 'BOOL'
            or izom_propui_free_is_exact_match_value_kind(effective_source_type)
        )
        supports_fallback_rule = target_mode == 'SELF' and supports_self_value_rules
        if target_mode == 'SELF':
            self_reference_entry = bounds_entry if bounds_entry is not None else owner
            _izom_propui_free_draw_value_match_prop(
                detail,
                current,
                effective_source_type,
                params,
                text_label="From Value",
                field_root='target_value',
                reference_entry=self_reference_entry,
                color_picker_scope='VALUE_LABEL',
                entry_uid=str(getattr(owner, 'uid', '') or '').strip(),
                value_label_uid=str(getattr(current, 'uid', '') or '').strip(),
                target_mode=target_mode,
            )
        if supports_fallback_rule:
            detail.prop(current, "rule_kind", text="Row Type")
        current_rule_kind = str(getattr(current, 'rule_kind', 'LABEL') or 'LABEL').strip().upper()
        if not (supports_fallback_rule and current_rule_kind == 'FALLBACK'):
            detail.prop(current, "label", text=value_label_text)
            _izom_propui_free_draw_limit_notice_for_prop(detail, current, "label", IZOM_PROPUI_FREE_MAX_LABEL_INPUT_TEXT)

    _izom_propui_free_draw_compact_footer_text(box, footer_text)
    return box

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

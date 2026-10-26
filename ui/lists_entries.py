# SPDX-License-Identifier: GPL-3.0-or-later

from .lists_common import (
    IZOM_PROPUI_FREE_ENTRY_LIST_EXPANDED_ICON,
    _IZOM_PROPUI_FREE_ENTRY_LIST_FILTER_CACHE,
    _izom_propui_free_cached_lookup,
    _izom_propui_free_draw_tree_arrow_spacer,
    _izom_propui_free_draw_tree_indent,
    _izom_propui_free_entry_list_primary_column,
    _izom_propui_free_entry_list_state,
    _izom_propui_free_fixed_row,
    _izom_propui_free_layout_entry_display_name,
    _izom_propui_free_pointer,
    _izom_propui_free_tree_arrow_slot,
    izom_propui_free_cached_entry_navigation_bundle,
)
from bpy.types import UIList


class IZOM_PROPUI_FREE_UL_entries(UIList):
    bl_idname = "IZOM_PROPUI_FREE_UL_entries"

    def _resolve_list_state(self, data):
        collection = getattr(data, 'izom_propui_free_entries', None)
        collection_ptr = _izom_propui_free_pointer(collection)
        collection_len = len(collection) if collection is not None else 0
        state_bundle = izom_propui_free_cached_entry_navigation_bundle(data)
        show_tree_hints = bool(getattr(data, 'izom_propui_free_show_entry_tree_hints', True))
        primary_column = _izom_propui_free_entry_list_primary_column(data)
        fingerprint = (
            _izom_propui_free_pointer(data),
            collection_ptr,
            collection_len,
            id(state_bundle.get('entry_snapshots')),
            id(state_bundle.get('entry_draw_state')),
            show_tree_hints,
            primary_column,
        )
        last = getattr(self, '_last_list_state', None)
        if last is not None and last[0] == fingerprint:
            return last[1]
        list_state = _izom_propui_free_entry_list_state(
            data,
            state_bundle=state_bundle,
            show_tree_hints=show_tree_hints,
            primary_column=primary_column,
        )
        self._last_list_state = (fingerprint, list_state)
        return list_state

    def draw_item(self, context, layout, data, item, _icon, _active_data, _active_propname, _index=0, _flt_flag=0):
        cache = getattr(self, '_draw_list_state', None) or self._resolve_list_state(data)
        self._draw_list_state = cache
        entry = item if hasattr(item, 'label') else None
        entry_uid = str(getattr(entry, 'uid', '') or getattr(item, 'entry_uid', '') or getattr(item, 'uid', '') or '').strip()
        if entry is None:
            fallback_index = cache.get('by_uid', {}).get(entry_uid, {}).get('fallback_index')
            items = cache.get('items', [])
            if isinstance(fallback_index, int) and 0 <= fallback_index < len(items):
                entry = items[fallback_index]
        if entry is None:
            layout.label(text='[Missing Entry]', icon='ERROR')
            return
        entry_uid = str(getattr(entry, 'uid', '') or entry_uid).strip()
        if not entry_uid:
            layout.label(text='[Missing Entry UID]', icon='ERROR')
            return
        item_state = cache.get('by_uid', {}).get(entry_uid, {})
        entry_icon = str(item_state.get('entry_icon', 'DOT') or 'DOT')
        layout.use_property_split = False
        layout.use_property_decorate = False
        row = layout.row(align=True)
        row.use_property_split = False
        row.use_property_decorate = False
        row.ui_units_y = 1.0
        name_cell = _izom_propui_free_fixed_row(row)
        name_cell.use_property_split = False
        name_cell.use_property_decorate = False
        name_cell.alignment = 'EXPAND'
        if cache.get('show_tree_hints', True):
            depth = max(0, int(item_state.get('depth', 0) or 0))
            collapsed = bool(item_state.get('collapsed', False))
            if depth > 0:
                _izom_propui_free_draw_tree_indent(name_cell, depth)
            toggle_cell = _izom_propui_free_tree_arrow_slot(name_cell)
            if bool(item_state.get('has_children', False)) and entry_uid:
                toggle_cell.emboss = 'NONE_OR_STATUS'
                toggle = toggle_cell.operator(
                    "wm.izom_propui_free_toggle_active_entry_collapse",
                    text="",
                    icon=str(item_state.get('row_icon', IZOM_PROPUI_FREE_ENTRY_LIST_EXPANDED_ICON) or IZOM_PROPUI_FREE_ENTRY_LIST_EXPANDED_ICON),
                )
                toggle.target_uid = entry_uid
            else:
                _izom_propui_free_draw_tree_arrow_spacer(toggle_cell)
        name_prop = name_cell.row(align=True)
        name_prop.use_property_split = False
        name_prop.use_property_decorate = False
        name_prop.alignment = 'EXPAND'
        editor_label = str(getattr(entry, 'editor_label', '') or '').strip()
        prop_type = str(getattr(entry, 'prop_type', 'FLOAT') or 'FLOAT').strip().upper()
        text_role = str(getattr(entry, 'text_role', 'TEXT') or 'TEXT').strip().upper()
        if editor_label:
            name_prop.prop(entry, "editor_label", text="", emboss=False, icon=entry_icon)
        elif prop_type == 'TEXT' and text_role != 'TEXT':
            name_prop.label(
                text=_izom_propui_free_layout_entry_display_name(entry, fallback_index=item_state.get('fallback_index', 1)),
                icon=entry_icon,
            )
        else:
            primary_attr = "label"
            if cache.get('primary_column', 'NAME') == 'PROP_ID' and prop_type != 'TEXT':
                primary_attr = "prop_id"
            name_prop.prop(entry, primary_attr, text="", emboss=False, icon=entry_icon)

    def filter_items(self, _context, data, _propname):
        cache = self._resolve_list_state(data)
        self._draw_list_state = cache
        ordered_uids = cache.get('ordered_uids', [])
        if not ordered_uids:
            return [], []

        filter_text = (self.filter_name or '').strip().casefold()
        cache_key = (
            _izom_propui_free_pointer(data),
            id(cache.get('items')),
            id(cache.get('visible_uid_set')),
            str(filter_text or ''),
        )

        def _build_flags():
            visible_uid_set = cache.get('visible_uid_set', set())
            by_uid = cache.get('by_uid', {})
            bitflag = self.bitflag_filter_item
            flags = []
            for entry_uid in ordered_uids:
                visible = str(entry_uid or '').strip() in visible_uid_set
                if visible and filter_text:
                    visible = filter_text in str(by_uid.get(entry_uid, {}).get('haystack', '') or '')
                flags.append(bitflag if visible else 0)
            return tuple(flags)

        flags = _izom_propui_free_cached_lookup(_IZOM_PROPUI_FREE_ENTRY_LIST_FILTER_CACHE, cache_key, _build_flags)
        return list(flags), list(range(len(ordered_uids)))

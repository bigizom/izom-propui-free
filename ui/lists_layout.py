# SPDX-License-Identifier: GPL-3.0-or-later

from .lists_common import (
    IZOM_PROPUI_FREE_ENTRY_LIST_COLLAPSED_ICON,
    IZOM_PROPUI_FREE_ENTRY_LIST_EXPANDED_ICON,
    _IZOM_PROPUI_FREE_LAYOUT_ENTRY_FILTER_CACHE,
    _izom_propui_free_cached_lookup,
    _izom_propui_free_draw_tree_arrow_spacer,
    _izom_propui_free_draw_tree_indent,
    _izom_propui_free_fixed_row,
    _izom_propui_free_layout_list_state,
    _izom_propui_free_pointer,
    _izom_propui_free_tree_arrow_slot,
    izom_propui_free_cached_layout_bundle,
)
from bpy.types import UIList


class IZOM_PROPUI_FREE_UL_layout_entries(UIList):
    bl_idname = "IZOM_PROPUI_FREE_UL_layout_entries"

    def _resolve_list_state(self, data, context):
        # Cheap per-instance fingerprint so repeated draw_item calls within a
        # single redraw don't even enter the cached state lookup.
        collection = getattr(data, 'izom_propui_free_layout_view_items', None)
        collection_ptr = _izom_propui_free_pointer(collection)
        collection_len = len(collection) if collection is not None else 0
        state_bundle = izom_propui_free_cached_layout_bundle(data)
        generated_layout_state = state_bundle.get('generated_layout_state', {})
        entry_snapshots_token = id(state_bundle.get('entry_snapshots'))
        fingerprint = (
            _izom_propui_free_pointer(data),
            collection_ptr,
            collection_len,
            id(generated_layout_state),
            id(state_bundle.get('layout_collapsed_row_uid_set')),
            entry_snapshots_token,
        )
        last = getattr(self, '_last_list_state', None)
        if last is not None and last[0] == fingerprint:
            return last[1]
        list_state = _izom_propui_free_layout_list_state(data)
        self._last_list_state = (fingerprint, list_state)
        return list_state

    def filter_items(self, context, data, propname):
        # We only need len(collection) here — `kinds` and `filter_haystacks`
        # from list_state already encode per-index info, so the whole
        # `list(collection)` conversion was a wasted O(N) RNA iteration.
        collection = getattr(data, propname, None)
        try:
            items_len = len(collection) if collection is not None else 0
        except TypeError:
            items_len = 0
        if items_len == 0:
            self._draw_list_state = None
            return [], []

        list_state = self._resolve_list_state(data, context)
        # Prime per-row fast path; see IZOM_PROPUI_FREE_UL_entries.filter_items.
        self._draw_list_state = list_state
        filter_text = (self.filter_name or '').strip().casefold()
        bitflag = self.bitflag_filter_item
        cache_key = (
            _izom_propui_free_pointer(data),
            id(list_state.get('items')),
            str(filter_text or ''),
        )

        def _build_flags():
            if not filter_text:
                return tuple([bitflag] * items_len)
            haystacks = list_state['filter_haystacks']
            haystacks_len = len(haystacks)
            flags = []
            for index in range(items_len):
                haystack = haystacks[index] if index < haystacks_len else ''
                flags.append(bitflag if filter_text in haystack else 0)
            return tuple(flags)

        flags = _izom_propui_free_cached_lookup(_IZOM_PROPUI_FREE_LAYOUT_ENTRY_FILTER_CACHE, cache_key, _build_flags)

        return list(flags), list_state['order']

    def draw_item(self, context, layout, data, item, _icon, _active_data, _active_propname, _index=0, _flt_flag=0):
        list_state = getattr(self, '_draw_list_state', None)
        if list_state is None:
            list_state = self._resolve_list_state(data, context)
        display_text = list_state['display_texts'][_index]
        row_icon = list_state['row_icons'][_index]
        row_depths = list_state.get('row_depths', [])
        row_depth = row_depths[_index] if _index < len(row_depths) else 0
        row_toggle_uids = list_state.get('row_toggle_uids', [])
        row_toggle_uid = row_toggle_uids[_index] if _index < len(row_toggle_uids) else ''
        row_collapsed = list_state.get('row_collapsed', [])
        is_collapsed = bool(row_collapsed[_index]) if _index < len(row_collapsed) else False
        row_entry_items = list_state.get('row_entry_items', [])
        entry = row_entry_items[_index] if _index < len(row_entry_items) else None
        row_meta_texts = list_state.get('row_meta_texts', [])
        row_meta_text = row_meta_texts[_index] if _index < len(row_meta_texts) else ''
        kind = str(getattr(item, 'kind', '') or '').strip()

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

        if kind == 'DIVIDER':
            row.enabled = False
        if row_depth > 0:
            _izom_propui_free_draw_tree_indent(name_cell, row_depth)
        toggle_cell = _izom_propui_free_tree_arrow_slot(name_cell)
        if kind == 'ROW_HEADER' and row_toggle_uid:
            toggle_cell.emboss = 'NONE_OR_STATUS'
            toggle = toggle_cell.operator(
                "wm.izom_propui_free_toggle_layout_row_group_collapse",
                text="",
                icon=IZOM_PROPUI_FREE_ENTRY_LIST_COLLAPSED_ICON if is_collapsed else IZOM_PROPUI_FREE_ENTRY_LIST_EXPANDED_ICON,
                emboss=False,
            )
            toggle.target_view_uid = row_toggle_uid
        else:
            _izom_propui_free_draw_tree_arrow_spacer(toggle_cell)

        name_prop = name_cell.row(align=True)
        name_prop.use_property_split = False
        name_prop.use_property_decorate = False
        name_prop.alignment = 'EXPAND'
        if kind == 'ENTRY_ITEM' and entry is not None:
            if row_meta_text:
                name_prop.label(text=row_meta_text)
            name_prop.label(text=display_text, icon=row_icon)
        else:
            if row_meta_text:
                name_prop.label(text=row_meta_text)
            name_prop.label(text=display_text, icon=row_icon)

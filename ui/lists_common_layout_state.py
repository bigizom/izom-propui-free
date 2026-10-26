# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.cache import izom_propui_free_cached_layout_bundle

from .lists_common_base import (
    _IZOM_PROPUI_FREE_LAYOUT_LIST_STATE_CACHE,
    _izom_propui_free_cached_lookup,
    _izom_propui_free_entry_type_icon,
    _izom_propui_free_pointer,
    _izom_propui_free_safe_collection_items,
    _izom_propui_free_safe_int_value,
)
from .lists_common_entry_state import (
    _izom_propui_free_entry_lookup_from_state,
    _izom_propui_free_layout_entry_display_name,
)


def _izom_propui_free_layout_list_state(data):
    collection = getattr(data, 'izom_propui_free_layout_view_items', None)
    collection_len = len(collection) if collection is not None else 0
    state_bundle = izom_propui_free_cached_layout_bundle(data)
    generated_layout_state = state_bundle.get('generated_layout_state', {})
    layout_collapsed_row_uid_set = state_bundle.get('layout_collapsed_row_uid_set', set())
    entry_snapshots_token = id(state_bundle.get('entry_snapshots'))
    cache_key = (
        _izom_propui_free_pointer(data),
        _izom_propui_free_pointer(collection),
        collection_len,
        id(generated_layout_state),
        id(layout_collapsed_row_uid_set),
        entry_snapshots_token,
    )

    def _build_state():
        items = _izom_propui_free_safe_collection_items(collection)
        entry_lookup = _izom_propui_free_entry_lookup_from_state(data, state_bundle)
        group_by_row_index = generated_layout_state.get('group_by_row_index', {})
        row_width_percent_label_by_layout_uid = generated_layout_state.get('row_width_percent_label_by_layout_uid', {})
        row_height_label_by_layout_uid = generated_layout_state.get('row_height_label_by_layout_uid', {})
        row_height_label_by_row_index = generated_layout_state.get('row_height_label_by_row_index', {})
        row_inset_label_by_layout_uid = generated_layout_state.get('row_inset_label_by_layout_uid', {})
        row_inset_label_by_row_index = generated_layout_state.get('row_inset_label_by_row_index', {})
        display_texts = []
        row_meta_texts = []
        row_icons = []
        row_depths = []
        row_toggle_uids = []
        row_collapsed = []
        row_entry_items = []
        filter_haystacks = []
        ordered = []

        for index, item in enumerate(items):
            kind = str(getattr(item, 'kind', '') or '').strip()
            ordered.append((
                _izom_propui_free_safe_int_value(getattr(item, 'ui_order', index + 1), index + 1),
                index,
            ))

            if kind == 'ROW_HEADER':
                row_uid = str(getattr(item, 'uid', '') or '').strip()
                row_index = max(1, _izom_propui_free_safe_int_value(getattr(item, 'row_index', 1), 1))
                group = group_by_row_index.get(row_index, {})
                member_count = len(group.get('member_uids', ()))
                item_label = "item" if member_count == 1 else "items"
                preview_text = str(group.get('preview_text', '') or '').strip()
                display_text = f"{member_count} {item_label}"
                row_height_label = (
                    str(row_height_label_by_row_index.get(row_index, '') or '').strip()
                )
                row_inset_label = (
                    str(row_inset_label_by_row_index.get(row_index, '') or '').strip()
                )
                meta_parts = [f"Row {row_index}"]
                meta_parts.append("100%")
                if row_height_label:
                    meta_parts.append(row_height_label)
                if row_inset_label:
                    meta_parts.append(row_inset_label)
                row_meta_label = " - ".join(part for part in meta_parts if part)
                display_texts.append(display_text)
                row_meta_texts.append(row_meta_label)
                row_icons.append('NONE')
                row_depths.append(0)
                row_toggle_uids.append(row_uid)
                row_collapsed.append(bool(row_uid and row_uid in layout_collapsed_row_uid_set))
                row_entry_items.append(None)
                filter_haystacks.append("\n".join(part for part in (display_text, row_meta_label, preview_text) if part).casefold())
                continue

            if kind == 'ENTRY_ITEM':
                entry_uid = str(getattr(item, 'entry_uid', '') or '').strip()
                entry = entry_lookup.get(entry_uid)
                is_gl_child = bool(str(getattr(item, 'parent_uid', '') or '').strip())
                base_name = _izom_propui_free_layout_entry_display_name(
                    entry,
                    fallback_index=index + 1,
                    entry_lookup=entry_lookup,
                )
                row_index = max(1, _izom_propui_free_safe_int_value(getattr(item, 'row_index', 1), 1))
                column_index = max(1, _izom_propui_free_safe_int_value(getattr(item, 'column_index', 1), 1))
                layout_uid = str(getattr(item, 'layout_uid', '') or '').strip()
                row_member_uids = generated_layout_state.get('row_by_layout_uid', {}).get(layout_uid, ()) or ()
                location_text = (
                    f"R{row_index} Column {column_index}"
                    if len(row_member_uids) > 1 else
                    f"Row {row_index}"
                )
                percent_label = (
                    str(row_width_percent_label_by_layout_uid.get(layout_uid, '') or '').strip()
                )
                row_height_label = (
                    str(row_height_label_by_layout_uid.get(layout_uid, '') or '').strip()
                    if len(row_member_uids) <= 1 else ''
                )
                row_inset_label = (
                    str(row_inset_label_by_layout_uid.get(layout_uid, '') or '').strip()
                    if len(row_member_uids) <= 1 else ''
                )
                meta_parts = [location_text]
                if percent_label:
                    meta_parts.append(percent_label)
                if row_height_label:
                    meta_parts.append(row_height_label)
                if row_inset_label:
                    meta_parts.append(row_inset_label)
                meta_text = " - ".join(meta_parts)
                display_texts.append(base_name)
                row_meta_texts.append(meta_text)
                prop_id = str(getattr(entry, 'prop_id', '') or '').strip() if entry is not None else ''
                row_icons.append(_izom_propui_free_entry_type_icon(str(getattr(entry, 'prop_type', '') or 'FLOAT')))
                row_depths.append(1 if is_gl_child else 0)
                row_toggle_uids.append('')
                row_collapsed.append(False)
                row_entry_items.append(entry)
                filter_haystacks.append("\n".join((base_name, prop_id, f"Row {row_index}", f"Column {column_index}", location_text, meta_text)).casefold())
                continue

            if kind == 'DIVIDER':
                display_texts.append('')
                row_meta_texts.append('')
                row_icons.append('BLANK1')
                row_depths.append(0)
                row_toggle_uids.append('')
                row_collapsed.append(False)
                row_entry_items.append(None)
                filter_haystacks.append('')
                continue

            display_texts.append('')
            row_meta_texts.append('')
            row_icons.append('BLANK1')
            row_depths.append(0)
            row_toggle_uids.append('')
            row_collapsed.append(False)
            row_entry_items.append(None)
            filter_haystacks.append('')

        return {
            'items': items,
            'display_texts': display_texts,
            'row_meta_texts': row_meta_texts,
            'row_icons': row_icons,
            'row_depths': row_depths,
            'row_toggle_uids': row_toggle_uids,
            'row_collapsed': row_collapsed,
            'row_entry_items': row_entry_items,
            'filter_haystacks': filter_haystacks,
            'order': [index for _ui_order, index in sorted(ordered, key=lambda pair: (pair[0], pair[1]))],
        }

    return _izom_propui_free_cached_lookup(_IZOM_PROPUI_FREE_LAYOUT_LIST_STATE_CACHE, cache_key, _build_state)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.constants import IZOM_PROPUI_FREE_LIST_ENTRY_TYPE_LABELS
from ..core.cache import izom_propui_free_cached_entry_navigation_bundle
from ..core.text import izom_propui_free_entry_display_name

from .helper_cache_updates import _izom_propui_free_cache_params_entries
from .lists_common_base import (
    _IZOM_PROPUI_FREE_ENTRY_LIST_DRAW_CACHE,
    IZOM_PROPUI_FREE_ENTRY_LIST_NAME_BASE_WIDTH,
    IZOM_PROPUI_FREE_ENTRY_LIST_NAME_CHAR_WIDTH,
    IZOM_PROPUI_FREE_ENTRY_LIST_NAME_DEPTH_WIDTH,
    IZOM_PROPUI_FREE_ENTRY_LIST_NAME_MIN_WIDTH,
    IZOM_PROPUI_FREE_ENTRY_LIST_NAME_TREE_SLOT_WIDTH,
    IZOM_PROPUI_FREE_ENTRY_LIST_PROP_ID_MIN_WIDTH,
    IZOM_PROPUI_FREE_ENTRY_LIST_PROP_ID_WIDTH,
    IZOM_PROPUI_FREE_ENTRY_LIST_TYPE_DROPDOWN_PAD,
    IZOM_PROPUI_FREE_ENTRY_LIST_TYPE_MIN_WIDTH,
    IZOM_PROPUI_FREE_ENTRY_LIST_TYPE_WIDTH,
    IZOM_PROPUI_FREE_ENTRY_LIST_COLLAPSED_ICON,
    IZOM_PROPUI_FREE_ENTRY_LIST_EXPANDED_ICON,
    _izom_propui_free_cached_lookup,
    _izom_propui_free_entry_type_icon,
    _izom_propui_free_pointer,
    _izom_propui_free_safe_collection_items,
)
from .lists_common_tree_draw import _izom_propui_free_fixed_row


def _izom_propui_free_entry_name_ui_units(display_name, *, depth=0, include_tree_prefix=False):
    name_length = len(str(display_name or ''))
    units = IZOM_PROPUI_FREE_ENTRY_LIST_NAME_BASE_WIDTH + (float(name_length) * IZOM_PROPUI_FREE_ENTRY_LIST_NAME_CHAR_WIDTH)
    if include_tree_prefix:
        units += IZOM_PROPUI_FREE_ENTRY_LIST_NAME_TREE_SLOT_WIDTH
        units += max(0, int(depth or 0)) * IZOM_PROPUI_FREE_ENTRY_LIST_NAME_DEPTH_WIDTH
    return max(IZOM_PROPUI_FREE_ENTRY_LIST_NAME_MIN_WIDTH, units)


def _izom_propui_free_entry_list_text_ui_units(display_text, *, min_width, max_width, extra_width=0.0):
    text_length = len(str(display_text or ''))
    units = IZOM_PROPUI_FREE_ENTRY_LIST_NAME_BASE_WIDTH + (float(text_length) * IZOM_PROPUI_FREE_ENTRY_LIST_NAME_CHAR_WIDTH)
    units += max(0.0, float(extra_width or 0.0))
    return max(float(min_width), min(float(max_width), units))


def _izom_propui_free_entry_list_primary_column(data):
    return str(getattr(data, 'izom_propui_free_entry_list_primary_column', 'NAME') or 'NAME').strip().upper() or 'NAME'


def _izom_propui_free_entry_item_value(item, name, default=None):
    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)


def _izom_propui_free_layout_entry_display_name(entry, *, fallback_index=1, entry_lookup=None):
    if entry is None:
        return izom_propui_free_entry_display_name(entry, fallback_index=fallback_index)
    editor_label = str(_izom_propui_free_entry_item_value(entry, 'editor_label', '') or '').strip()
    if editor_label:
        return editor_label
    return izom_propui_free_entry_display_name(entry, fallback_index=fallback_index)


def _izom_propui_free_entry_list_primary_text(
    data,
    entry,
    *,
    primary_column=None,
    fallback_index=1,
    entry_lookup=None,
):
    editor_label = str(getattr(entry, 'editor_label', '') or '').strip()
    if editor_label:
        return editor_label
    resolved_primary_column = (
        _izom_propui_free_entry_list_primary_column(data)
        if primary_column is None
        else primary_column
    )
    if resolved_primary_column == 'PROP_ID':
        prop_id = str(getattr(entry, 'prop_id', '') or '').strip()
        if prop_id:
            return prop_id
    return _izom_propui_free_layout_entry_display_name(
        entry,
        fallback_index=fallback_index,
        entry_lookup=entry_lookup,
    )


def izom_propui_free_draw_entry_list_header(layout, *, data=None, context=None, list_state=None):
    layout.use_property_split = False
    layout.use_property_decorate = False
    row = layout.row(align=True)
    row.use_property_split = False
    row.use_property_decorate = False
    row.ui_units_y = 1.0
    row.alignment = 'LEFT'
    name_cell = _izom_propui_free_fixed_row(row)
    name_cell.alignment = 'LEFT'
    primary_column = (
        str(list_state.get('primary_column', 'NAME') or 'NAME')
        if list_state is not None
        else _izom_propui_free_entry_list_primary_column(data)
    )
    name_cell.label(text="Property ID" if primary_column == 'PROP_ID' else "Name/Label/Text")


def _izom_propui_free_entry_lookup_from_state(data, state_bundle):
    entries = getattr(data, 'izom_propui_free_entries', None) or []
    lookup = {}
    for uid, index in (state_bundle.get('entry_index_by_uid', {}) or {}).items():
        try:
            resolved_index = int(index)
        except (TypeError, ValueError):
            continue
        if 0 <= resolved_index < len(entries):
            target_uid = str(uid or '').strip()
            candidate = entries[resolved_index]
            if str(getattr(candidate, 'uid', '') or '').strip() == target_uid:
                lookup[target_uid] = candidate
    for entry in entries:
        entry_uid = str(getattr(entry, 'uid', '') or '').strip()
        if entry_uid and entry_uid not in lookup:
            lookup[entry_uid] = entry
    return lookup


def _izom_propui_free_entry_list_state(
    data,
    *,
    state_bundle=None,
    show_tree_hints=None,
    primary_column=None,
):
    collection = getattr(data, 'izom_propui_free_entries', None)
    collection_len = len(collection) if collection is not None else 0
    if state_bundle is None:
        state_bundle = izom_propui_free_cached_entry_navigation_bundle(data)
    tree_state = state_bundle.get('tree_state', {}) or {}
    entry_draw_state = state_bundle.get('entry_draw_state', {}) or {}
    if show_tree_hints is None:
        show_tree_hints = bool(getattr(data, 'izom_propui_free_show_entry_tree_hints', True))
    if primary_column is None:
        primary_column = _izom_propui_free_entry_list_primary_column(data)
    cache_key = (
        _izom_propui_free_pointer(data),
        _izom_propui_free_pointer(collection),
        collection_len,
        id(state_bundle.get('entry_snapshots')),
        id(entry_draw_state),
        bool(show_tree_hints),
        primary_column,
    )

    def _build_state():
        items = _izom_propui_free_safe_collection_items(collection)
        _izom_propui_free_cache_params_entries(data)
        entry_lookup = {
            str(getattr(item, 'uid', '') or '').strip(): item
            for item in items
            if str(getattr(item, 'uid', '') or '').strip()
        }
        children_by_uid = tree_state.get('children_by_uid', {}) or {}
        depth_by_uid = tree_state.get('depth_by_uid', {}) or {}
        entry_draw_by_uid = entry_draw_state.get('by_uid', {}) or {}
        if show_tree_hints:
            visible_uid_set = entry_draw_state.get('visible_entry_list_uid_set')
            if visible_uid_set is None:
                visible_uid_set = set(entry_draw_state.get('visible_entry_list_uids', []) or ())
        else:
            visible_uid_set = entry_draw_state.get('visible_hierarchy_uid_set')
            if visible_uid_set is None:
                visible_uid_set = set(entry_draw_state.get('visible_hierarchy_uids', []) or ())
        ordered_uids = []
        by_uid = {}
        visible_count = 0
        max_visible_name_units = IZOM_PROPUI_FREE_ENTRY_LIST_NAME_MIN_WIDTH
        max_visible_prop_id_units = _izom_propui_free_entry_list_text_ui_units(
            "Property ID",
            min_width=IZOM_PROPUI_FREE_ENTRY_LIST_PROP_ID_MIN_WIDTH,
            max_width=IZOM_PROPUI_FREE_ENTRY_LIST_PROP_ID_WIDTH,
        )
        max_visible_type_units = _izom_propui_free_entry_list_text_ui_units(
            "Entry Type",
            min_width=IZOM_PROPUI_FREE_ENTRY_LIST_TYPE_MIN_WIDTH,
            max_width=IZOM_PROPUI_FREE_ENTRY_LIST_TYPE_WIDTH,
            extra_width=IZOM_PROPUI_FREE_ENTRY_LIST_TYPE_DROPDOWN_PAD,
        )
        for index, entry in enumerate(items):
            entry_uid = str(getattr(entry, 'uid', '') or getattr(entry, 'entry_uid', '') or '').strip()
            ordered_uids.append(entry_uid)
            label = str(getattr(entry, 'label', '') or '').strip()
            prop_id = str(getattr(entry, 'prop_id', '') or '').strip()
            prop_type = str(getattr(entry, 'prop_type', 'FLOAT') or 'FLOAT').strip().upper() or 'FLOAT'
            prop_type_label = str(IZOM_PROPUI_FREE_LIST_ENTRY_TYPE_LABELS.get(prop_type, prop_type.title()) or prop_type).strip()
            display_name = _izom_propui_free_entry_list_primary_text(
                data,
                entry,
                primary_column=primary_column,
                fallback_index=index + 1,
                entry_lookup=entry_lookup,
            )
            editor_label = str(getattr(entry, 'editor_label', '') or '').strip()
            item_state = {
                'haystack': "\n".join((editor_label, display_name, label, prop_id, prop_type, prop_type_label)).casefold(),
                'depth': 0,
                'has_children': False,
                'collapsed': False,
                'row_icon': 'BLANK1',
                'entry_icon': _izom_propui_free_entry_type_icon(prop_type),
                'display_name': display_name,
                'fallback_index': index,
            }
            if show_tree_hints:
                row_state = entry_draw_by_uid.get(entry_uid, {}) or {}
                depth = max(0, int(row_state.get('depth', depth_by_uid.get(entry_uid, 0)) or 0))
                has_children = bool(row_state.get('has_children', False)) or bool(entry_uid and entry_uid in children_by_uid)
                collapsed = bool(row_state.get('collapsed', False))
                row_icon = str(
                    row_state.get(
                        'row_icon',
                        IZOM_PROPUI_FREE_ENTRY_LIST_COLLAPSED_ICON if collapsed else IZOM_PROPUI_FREE_ENTRY_LIST_EXPANDED_ICON,
                    )
                    or (IZOM_PROPUI_FREE_ENTRY_LIST_COLLAPSED_ICON if collapsed else IZOM_PROPUI_FREE_ENTRY_LIST_EXPANDED_ICON)
                )
                if not has_children:
                    row_icon = 'BLANK1'
                item_state['depth'] = depth
                item_state['has_children'] = has_children
                item_state['collapsed'] = collapsed
                item_state['row_icon'] = row_icon
            by_uid[entry_uid] = item_state
            if entry_uid in visible_uid_set:
                visible_count += 1
                max_visible_prop_id_units = max(
                    max_visible_prop_id_units,
                    _izom_propui_free_entry_list_text_ui_units(
                        prop_id or "Property ID",
                        min_width=IZOM_PROPUI_FREE_ENTRY_LIST_PROP_ID_MIN_WIDTH,
                        max_width=IZOM_PROPUI_FREE_ENTRY_LIST_PROP_ID_WIDTH,
                    ),
                )
                max_visible_type_units = max(
                    max_visible_type_units,
                    _izom_propui_free_entry_list_text_ui_units(
                        prop_type_label,
                        min_width=IZOM_PROPUI_FREE_ENTRY_LIST_TYPE_MIN_WIDTH,
                        max_width=IZOM_PROPUI_FREE_ENTRY_LIST_TYPE_WIDTH,
                        extra_width=IZOM_PROPUI_FREE_ENTRY_LIST_TYPE_DROPDOWN_PAD,
                    ),
                )
                max_visible_name_units = max(
                    max_visible_name_units,
                    _izom_propui_free_entry_name_ui_units(
                        display_name,
                        depth=item_state.get('depth', 0),
                        include_tree_prefix=show_tree_hints,
                    ),
                )
        return {
            'items': items,
            'ordered_uids': ordered_uids,
            'by_uid': by_uid,
            'visible_uid_set': visible_uid_set,
            'visible_count': visible_count,
            'max_visible_name_units': max_visible_name_units,
            'max_visible_prop_id_units': max_visible_prop_id_units,
            'max_visible_type_units': max_visible_type_units,
            'show_tree_hints': show_tree_hints,
            'primary_column': primary_column,
        }

    return _izom_propui_free_cached_lookup(_IZOM_PROPUI_FREE_ENTRY_LIST_DRAW_CACHE, cache_key, _build_state)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

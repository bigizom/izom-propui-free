# SPDX-License-Identifier: GPL-3.0-or-later

from .lists_common import (
    _IZOM_PROPUI_FREE_VALUE_LABEL_FILTER_CACHE,
    _IZOM_PROPUI_FREE_VALUE_LABEL_LIST_CACHE,
    _izom_propui_free_cached_lookup,
    _izom_propui_free_pointer,
    _izom_propui_free_resolved_value_label_source_info,
    _izom_propui_free_rule_kind_value,
    _izom_propui_free_safe_collection_items,
    _izom_propui_free_value_label_cache_key,
    _izom_propui_free_value_label_fallback_name,
    _izom_propui_free_value_label_row_summary,
)
from bpy.types import UIList
from ..core.cache_state import izom_propui_free_cached_entry_tree_bundle
from .helper_cache_updates_entry_params import _izom_propui_free_find_params_for_entry



class IZOM_PROPUI_FREE_UL_value_labels(UIList):
    bl_idname = "IZOM_PROPUI_FREE_UL_value_labels"

    def _row_cache(self, owner, active_propname, context):
        collection_name = active_propname.replace('_active_index', '')
        collection = getattr(owner, collection_name, None)
        collection_ptr = _izom_propui_free_pointer(collection)
        collection_len = len(collection) if collection is not None else 0
        collection_revision = 0
        params_ptr = 0
        snapshot_cache_token = 0
        runtime_cache_token = 0
        params = owner if hasattr(owner, 'izom_propui_free_entries') else _izom_propui_free_find_params_for_entry(owner, context)
        if params is not None:
            params_ptr = _izom_propui_free_pointer(params)
            state_bundle = izom_propui_free_cached_entry_tree_bundle(params)
            snapshot_cache_token = id(state_bundle.get('entry_snapshots'))
            runtime_cache_token = id(state_bundle.get('runtime_entries'))
        cheap_fingerprint = (
            _izom_propui_free_pointer(owner),
            str(active_propname or ''),
            collection_ptr,
            collection_len,
            collection_revision,
            params_ptr,
            snapshot_cache_token,
            runtime_cache_token,
        )
        last = getattr(self, '_last_row_cache', None)
        if last is not None and last[0] == cheap_fingerprint:
            return last[1]

        source_info = _izom_propui_free_resolved_value_label_source_info(owner, active_propname, context)
        cache_key = _izom_propui_free_value_label_cache_key(
            owner,
            active_propname,
            source_info,
            collection_ptr=collection_ptr,
            collection_len=collection_len,
            collection_revision=collection_revision,
            snapshot_cache_token=snapshot_cache_token,
            runtime_cache_token=runtime_cache_token,
        )

        def _build_cache():
            items = _izom_propui_free_safe_collection_items(collection)
            target_mode = str(source_info.get('target_mode', 'SELF') or 'SELF')
            display_texts = []
            row_icons = []
            haystacks = []
            for index, item in enumerate(items):
                summary = _izom_propui_free_value_label_row_summary(source_info, item)
                if _izom_propui_free_rule_kind_value(item) == 'FALLBACK':
                    label = _izom_propui_free_value_label_fallback_name(source_info)
                    row_icons.append('INFO')
                else:
                    label = str(getattr(item, 'label', '') or '')
                    row_icons.append('DOT')
                display_text = f"{index + 1}. {summary}"
                if label and label != summary:
                    display_text = f"{display_text} - {label}"
                display_texts.append(display_text)
                haystacks.append("\n".join((summary, label, display_text)).casefold())
            return {
                'items': items,
                'source_info': source_info,
                'display_texts': display_texts,
                'row_icons': row_icons,
                'haystacks': haystacks,
            }

        result = _izom_propui_free_cached_lookup(_IZOM_PROPUI_FREE_VALUE_LABEL_LIST_CACHE, cache_key, _build_cache)
        self._last_row_cache = (cheap_fingerprint, result)
        return result

    def filter_items(self, context, data, propname):
        active_propname = f"{propname}_active_index"
        cache = self._row_cache(data, active_propname, context)
        items = cache['items']
        if not items:
            return [], []
        filter_text = (self.filter_name or '').strip().casefold()
        bitflag = self.bitflag_filter_item
        cache_key = (
            _izom_propui_free_pointer(data),
            str(active_propname or ''),
            id(cache.get('items')),
            id(cache.get('haystacks')),
            str(filter_text or ''),
        )

        def _build_flags():
            if not filter_text:
                return tuple([bitflag] * len(items))
            return tuple(
                bitflag if filter_text in haystack else 0
                for haystack in cache['haystacks']
            )

        flags = _izom_propui_free_cached_lookup(_IZOM_PROPUI_FREE_VALUE_LABEL_FILTER_CACHE, cache_key, _build_flags)
        return list(flags), list(range(len(items)))

    def draw_item(self, context, layout, _data, item, _icon, active_data, active_propname, _index=0, _flt_flag=0):
        owner = active_data
        cache = self._row_cache(owner, active_propname, context)
        layout.label(
            text=cache['display_texts'][_index],
            icon=cache['row_icons'][_index],
        )

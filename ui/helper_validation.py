# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.cache import (
    _izom_propui_free_inheritance_summary,
    izom_propui_free_cached_visibility_inheritance_info_map,
)
from ..core.entry_ids import _izom_propui_free_entry_label
from ..core.runtime import (
    _izom_propui_free_visibility_inheritance_scope,
)

def _izom_propui_free_default_inheritance_info():
    return {
        'requested_depth': 1,
        'available_depth': 0,
        'selected_depth': 1,
        'applied_depth': 0,
        'applied_ancestors': [],
        'selected_ancestor': None,
        'selected_relation': "none",
        'selected_ancestor_name': 'Entry',
        'summary_text': "none",
        'enabled': False,
    }

def _izom_propui_free_copy_inheritance_info(info):
    copied = dict(info or _izom_propui_free_default_inheritance_info())
    copied['applied_ancestors'] = list(copied.get('applied_ancestors', []) or [])
    return copied

def _izom_propui_free_build_inheritance_info(scope):
    available_depth = int(scope.get('available_depth', 0) or 0)
    selected_depth = int(scope.get('selected_depth', 1) or 1)
    applied_depth = int(scope.get('applied_depth', 0) or 0)
    applied_ancestors = list(scope.get('applied_ancestors', []) or [])
    selected_ancestor = applied_ancestors[applied_depth - 1] if applied_depth > 0 and applied_depth <= len(applied_ancestors) else None
    summary_text = _izom_propui_free_inheritance_summary(applied_depth)
    selected_relation = summary_text
    selected_ancestor_name = _izom_propui_free_entry_label(selected_ancestor) if selected_ancestor is not None else 'Entry'
    return {
        'requested_depth': int(scope.get('requested_depth', selected_depth) or selected_depth),
        'available_depth': available_depth,
        'selected_depth': selected_depth,
        'applied_depth': applied_depth,
        'applied_ancestors': applied_ancestors,
        'selected_ancestor': selected_ancestor,
        'selected_relation': selected_relation,
        'selected_ancestor_name': selected_ancestor_name,
        'summary_text': summary_text,
        'enabled': available_depth > 1,
    }

def _izom_propui_free_entry_visibility_inheritance_info(params, entry, *, state=None):
    if entry is None:
        return _izom_propui_free_default_inheritance_info()

    if params is not None and state is None:
        entry_uid = str(getattr(entry, 'uid', '') if not isinstance(entry, dict) else entry.get('uid', '') or '').strip()
        cached = izom_propui_free_cached_visibility_inheritance_info_map(params).get(entry_uid)
        if cached is not None:
            return _izom_propui_free_copy_inheritance_info(cached)

    scope = _izom_propui_free_visibility_inheritance_scope(params, entry, state=state)
    return _izom_propui_free_build_inheritance_info(scope)

def _izom_propui_free_draw_char_limit_notice(layout, value, limit):
    try:
        current_len = len(str(value or ''))
    except (TypeError, ValueError):
        current_len = 0
    if limit is None or current_len < int(limit):
        return
    row = layout.row()
    row.alert = True
    row.label(text=f"{int(limit)} character limit reached", icon='INFO')

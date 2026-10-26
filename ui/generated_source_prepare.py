# SPDX-License-Identifier: GPL-3.0-or-later

def _izom_propui_free_prepare_generated_entries(params, *, runtime_layout_entries=None):
    default_owner_path = str(getattr(params, 'izom_propui_free_default_target_owner_path', '') or '').strip()
    entries = []
    owner_paths = []
    source_entries = runtime_layout_entries if runtime_layout_entries is not None else izom_propui_free_runtime_layout_entries(params)
    for entry in source_entries:
        item = dict(entry)
        if _izom_propui_free_syncable_prop_type(item.get('prop_type')) and default_owner_path and not owner_paths:
            owner_paths.append(default_owner_path)
        entries.append(item)
    return entries, owner_paths


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401
from ..core.runtime_layout import izom_propui_free_runtime_layout_entries
from .operators_sync_common import _izom_propui_free_syncable_prop_type


__all__ = izom_propui_free_public_names(globals(), all_public=True)

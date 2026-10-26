# SPDX-License-Identifier: GPL-3.0-or-later

from .generated_slots_common import (
    _izom_propui_free_new_generated_slot_uid,
)
from ..core.constants_display import (
    IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TAB,
    IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TITLE,
)
from .generated_naming import _izom_propui_free_generated_script_name_for_slot
from .generated_branding import izom_propui_free_normalize_generated_branding


def _izom_propui_free_normalize_generated_slot(item):
    slot_uid = str(item.get('uid', '') or '').strip() or _izom_propui_free_new_generated_slot_uid()
    branding = izom_propui_free_normalize_generated_branding(item.get('branding'))
    script_name = _izom_propui_free_generated_script_name_for_slot({**item, 'uid': slot_uid, 'branding': branding})
    return {
        'uid': slot_uid,
        'scene_name': str(item.get('scene_name', '') or '').strip(),
        'script_name': script_name,
        'tab': str(item.get('tab', '') or '').strip() or IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TAB,
        'title': str(item.get('title', '') or '').strip() or IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TITLE,
        'target_path': str(item.get('target_path', '') or '').strip(),
        'source': str(item.get('source', '') or ''),
        'branding': branding,
        'owner_paths': list(item.get('owner_paths', []) or []),
    }


def _izom_propui_free_generated_slot_container_specs(slot):
    return [{
        'title': str((slot or {}).get('title', '') or '').strip() or IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TITLE,
        'draw_name': '_izom_propui_free_generated_draw',
    }]


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

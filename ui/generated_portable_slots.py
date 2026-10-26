# SPDX-License-Identifier: GPL-3.0-or-later

from .generated_naming import (
    _izom_propui_free_generated_script_name_for_slot,
    _izom_propui_free_with_unique_per_ui_script_names,
)
from .generated_slots import _izom_propui_free_generated_slots_from_params
from .generated_state import _izom_propui_free_data_collection


def _izom_propui_free_portable_script_slots():
    slots = []
    scenes = _izom_propui_free_data_collection('scenes')
    if scenes is None:
        return slots
    for scene in scenes:
        params = getattr(scene, 'izom_propui_free', None)
        if params is None:
            continue
        scene_name = str(getattr(scene, 'name', '') or '').strip()
        for slot in _izom_propui_free_generated_slots_from_params(params):
            source = str(slot.get('source', '') or '')
            if not source:
                continue
            item = dict(slot)
            item['scene_name'] = scene_name
            item['script_name'] = _izom_propui_free_generated_script_name_for_slot(item)
            slots.append(item)
    return _izom_propui_free_with_unique_per_ui_script_names(slots)

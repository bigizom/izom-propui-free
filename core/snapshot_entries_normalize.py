# SPDX-License-Identifier: GPL-3.0-or-later

from .snapshot_entries_labels import (
    _izom_propui_free_limit_label_input_text,
)
from .constants_display import (
    izom_propui_free_normalize_multi_component_layout,
    izom_propui_free_normalize_multi_component_draw_mode,
    izom_propui_free_normalize_value_label_layout,
)
from .constants_serialized import IZOM_PROPUI_FREE_LIST_ENTRY_TYPE_LABELS
from .entry_ids import (
    _izom_propui_free_limit_entry_snapshot_strings,
)
from .entry_normalization import _izom_propui_free_disable_slider_for_soft_limits
from .float_arrays import (
    izom_propui_free_normalize_array_element_type,
    izom_propui_free_normalize_array_size,
)
from .snapshot_entries_common import _izom_propui_free_typed_array_snapshot_value
from .snapshot_tree import (
    _izom_propui_free_clamp_snapshot_compare_value,
    _izom_propui_free_clamp_snapshot_default_value,
    _izom_propui_free_coerce_float,
    _izom_propui_free_coerce_int,
    _izom_propui_free_visibility_inheritance_depth_from_state,
)
from .text import (
    izom_propui_free_display_alignment,
    izom_propui_free_display_icon,
    izom_propui_free_display_icon_pair,
    izom_propui_free_text_role,
)



def _izom_propui_free_normalize_entry_snapshot(index, snap, state):
    prop_type = str(snap.get('prop_type', 'FLOAT') or 'FLOAT').strip().upper() or 'FLOAT'
    if prop_type == 'FLOAT_ARRAY':
        prop_type = 'ARRAY'
    snap['prop_type'] = prop_type if prop_type in IZOM_PROPUI_FREE_LIST_ENTRY_TYPE_LABELS else 'FLOAT'
    snap['ui_order'] = index
    snap['display_order'] = max(1, _izom_propui_free_coerce_int(snap['display_order'], snap['ui_order']))
    snap['row_slot'] = max(1, _izom_propui_free_coerce_int(snap['row_slot'], 1))
    snap['slider'] = bool(snap.get('slider', True))
    snap['use_soft_limits'] = bool(snap.get('use_soft_limits', False))
    _izom_propui_free_disable_slider_for_soft_limits(snap)
    snap['alert_style'] = bool(snap.get('alert_style', False))
    snap['text_alignment'] = izom_propui_free_display_alignment(snap['text_alignment'])
    snap['text_role'] = izom_propui_free_text_role(snap.get('text_role', 'TEXT'))
    snap['text_alert'] = bool(snap['text_alert'])
    snap['text_icon_hug_text'] = bool(snap.get('text_icon_hug_text', True))
    snap['text_icon_after_hug_text'] = bool(snap.get('text_icon_after_hug_text', True))
    snap['text_icon'], snap['text_icon_after'] = izom_propui_free_display_icon_pair(
        snap['text_icon'],
        snap['text_icon_after'],
    )
    snap['array_element_type'] = izom_propui_free_normalize_array_element_type(snap.get('array_element_type', 'FLOAT'), 'FLOAT')
    snap['array_size'] = izom_propui_free_normalize_array_size(
        snap.get('array_size', 4),
        snap.get('float_array_subtype', 'NONE'),
        snap['array_element_type'],
        default=4,
    )
    snap['default_float_array'] = _izom_propui_free_typed_array_snapshot_value(snap.get('default_float_array', (1.0,) * 32), 'FLOAT', (1.0,) * 32)
    snap['default_int_array'] = _izom_propui_free_typed_array_snapshot_value(snap.get('default_int_array', (0,) * 32), 'INT', (0,) * 32)
    snap['default_bool_array'] = _izom_propui_free_typed_array_snapshot_value(snap.get('default_bool_array', (False,) * 32), 'BOOL', (False,) * 32)
    snap['visibility_match_float_array'] = _izom_propui_free_typed_array_snapshot_value(snap.get('visibility_match_float_array', (1.0,) * 32), 'FLOAT', (1.0,) * 32)
    snap['visibility_match_int_array'] = _izom_propui_free_typed_array_snapshot_value(snap.get('visibility_match_int_array', (0,) * 32), 'INT', (0,) * 32)
    snap['visibility_match_bool_array'] = _izom_propui_free_typed_array_snapshot_value(snap.get('visibility_match_bool_array', (False,) * 32), 'BOOL', (False,) * 32)
    snap['value_label_layout'] = izom_propui_free_normalize_value_label_layout(snap.get('value_label_layout'))
    snap['multi_component_layout'] = izom_propui_free_normalize_multi_component_layout(snap.get('multi_component_layout'))
    snap['multi_component_draw_mode'] = izom_propui_free_normalize_multi_component_draw_mode(
        snap.get('multi_component_draw_mode', 'WIDGET')
    )
    snap['value_labels'] = list(snap.get('value_labels') or [])
    snap['visibility_inheritance_depth'] = _izom_propui_free_visibility_inheritance_depth_from_state(
        state,
        snap['uid'],
        snap['visibility_inheritance_depth'],
    )
    _izom_propui_free_clamp_snapshot_default_value(snap)
    _izom_propui_free_clamp_snapshot_compare_value(state, snap, prefix='visibility')
    _izom_propui_free_limit_entry_snapshot_strings(snap)

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

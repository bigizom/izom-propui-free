# SPDX-License-Identifier: GPL-3.0-or-later

def _izom_propui_free_normalize_editor_float_decimals(raw_decimals):
    try:
        decimals = int(raw_decimals)
    except (TypeError, ValueError):
        decimals = 3
    return max(0, min(6, decimals))


def _izom_propui_free_editor_float_min_step(decimals):
    decimals = _izom_propui_free_normalize_editor_float_decimals(decimals)
    if decimals <= 0:
        return 1.0
    return round(10 ** (-decimals), decimals)


def _izom_propui_free_normalize_editor_float_step(raw_step, decimals):
    decimals = _izom_propui_free_normalize_editor_float_decimals(decimals)
    scale = 10 ** decimals
    min_step_ticks = max(1, int(round(_izom_propui_free_editor_float_min_step(decimals) * scale)))
    try:
        step_value = abs(float(raw_step))
    except (TypeError, ValueError):
        step_value = _izom_propui_free_editor_float_min_step(decimals)
    step_ticks = int(round(step_value * scale))
    if step_ticks < min_step_ticks:
        step_ticks = min_step_ticks
    return step_ticks / scale


def _izom_propui_free_snap_editor_float_value(raw_value, decimals, step, base=0.0):
    decimals = _izom_propui_free_normalize_editor_float_decimals(decimals)
    scale = 10 ** decimals
    step_value = _izom_propui_free_normalize_editor_float_step(step, decimals)
    step_ticks = max(1, int(round(step_value * scale)))
    try:
        value_ticks = int(round(float(raw_value) * scale))
    except (TypeError, ValueError):
        value_ticks = 0
    try:
        base_ticks = int(round(float(base) * scale))
    except (TypeError, ValueError):
        base_ticks = 0

    delta_ticks = value_ticks - base_ticks
    half_step = step_ticks // 2
    if delta_ticks >= 0:
        snapped_steps = (delta_ticks + half_step) // step_ticks
    else:
        snapped_steps = -(((-delta_ticks) + half_step) // step_ticks)
    snapped_ticks = base_ticks + snapped_steps * step_ticks
    return snapped_ticks / scale


def _izom_propui_free_normalize_threshold_value(raw_value, prop_type):
    try:
        if prop_type == 'INT':
            return int(raw_value)
        return round(float(raw_value), 6)
    except (TypeError, ValueError):
        return 0 if prop_type == 'INT' else 0.0


def _izom_propui_free_collection_item_matches(candidate, item):
    if candidate is item:
        return True
    try:
        return int(candidate.as_pointer()) == int(item.as_pointer())
    except (AttributeError, TypeError, ValueError):
        return False


def _izom_propui_free_clamp_threshold_value(raw_value, prop_type, min_value=None, max_value=None):
    value = _izom_propui_free_normalize_threshold_value(raw_value, prop_type)
    if min_value is not None:
        min_value = _izom_propui_free_normalize_threshold_value(min_value, prop_type)
        if value < min_value:
            value = min_value
    if max_value is not None:
        max_value = _izom_propui_free_normalize_threshold_value(max_value, prop_type)
        if value > max_value:
            value = max_value
    if min_value is not None and max_value is not None and value < min_value:
        value = min_value
    return value


from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

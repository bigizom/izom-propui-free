# SPDX-License-Identifier: GPL-3.0-or-later

from .helper_cache_updates import (
    _izom_propui_free_context_bulk_entry_updates_suspended,
    _izom_propui_free_entry_runtime_update_callbacks_suspended,
)
from ..core.value_labels_thresholds import (
    _izom_propui_free_editor_float_min_step,
    _izom_propui_free_normalize_editor_float_decimals,
    _izom_propui_free_snap_editor_float_value,
)



def _izom_propui_free_entry_field_update_suspended(context=None):
    return (
        _izom_propui_free_entry_runtime_update_callbacks_suspended()
        or _izom_propui_free_context_bulk_entry_updates_suspended(context)
    )


def _izom_propui_free_editor_float_settings(params):
    decimals = _izom_propui_free_normalize_editor_float_decimals(getattr(params, 'izom_propui_free_editor_float_decimals', 3))
    step = _izom_propui_free_editor_float_min_step(decimals)
    return decimals, step


def _izom_propui_free_snap_editor_float_value_for_params(params, raw_value, *, base=0.0):
    if params is None:
        decimals = _izom_propui_free_normalize_editor_float_decimals(3)
        step = _izom_propui_free_editor_float_min_step(decimals)
    else:
        decimals, step = _izom_propui_free_editor_float_settings(params)
    return _izom_propui_free_snap_editor_float_value(raw_value, decimals, step, base=base)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

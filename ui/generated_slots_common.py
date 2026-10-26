# SPDX-License-Identifier: GPL-3.0-or-later

def _izom_propui_free_copy_generated_slot(slot):
    copied = dict(slot or {})
    copied['owner_paths'] = list(copied.get('owner_paths', []) or [])
    copied['branding'] = dict(copied.get('branding', {}) or {}) if isinstance(copied.get('branding', {}), dict) else {}
    return copied


def _izom_propui_free_copy_generated_slots(slots):
    return [_izom_propui_free_copy_generated_slot(slot) for slot in (slots or []) if isinstance(slot, dict)]

def _izom_propui_free_params_key_safe(params):
    try:
        return int(params.as_pointer())
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        from ..core.diagnostics import izom_propui_free_log_recovered

        izom_propui_free_log_recovered(category='UI', exception=exc)
        return id(params)

def _izom_propui_free_new_generated_slot_uid():
    import uuid

    return "generated_" + uuid.uuid4().hex

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

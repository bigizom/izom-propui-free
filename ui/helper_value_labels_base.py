# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from ..core.diagnostics import izom_propui_free_log_recovered

from ..core.cache import (
    izom_propui_free_cached_entry_tree_bundle,
)

_IZOM_PROPUI_FREE_DEPENDENT_THRESHOLD_OWNER_CACHE = {}
_IZOM_PROPUI_FREE_DEPENDENT_THRESHOLD_OWNER_CACHE_LIMIT = 32


def _izom_propui_free_clear_value_label_session_caches():
    _IZOM_PROPUI_FREE_DEPENDENT_THRESHOLD_OWNER_CACHE.clear()


def _izom_propui_free_inheritance_tree_state(params):
    if params is None:
        return None
    try:
        return izom_propui_free_cached_entry_tree_bundle(params).get('tree_state')
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        return None

def _izom_propui_free_numeric_threshold_matches(a, b, prop_type):
    try:
        if prop_type == 'INT':
            return int(a) == int(b)
        return abs(float(a) - float(b)) <= 1e-6
    except (TypeError, ValueError):
        return False

def _izom_propui_free_value_label_guard_key(item, field_name):
    try:
        return (str(field_name), int(item.as_pointer()))
    except (AttributeError, TypeError, ValueError):
        return (str(field_name), id(item))

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

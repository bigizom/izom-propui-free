# SPDX-License-Identifier: GPL-3.0-or-later

from .helper_cache_updates_entry_runtime import (
    _izom_propui_free_entry_runtime_display_updated,
)
from ..core.entry_ids import _izom_propui_free_string_limit_updated
from ..core.text import (
    _izom_propui_free_limit_label_input_text,
    _izom_propui_free_limit_tooltip_input_text,
)


def _izom_propui_free_string_limit_updated_with_cache(field_name, limit_func):
    base_update = _izom_propui_free_string_limit_updated(field_name, limit_func)

    def _update(entry, context):
        base_update(entry, context)
        _izom_propui_free_entry_runtime_display_updated(entry, context)

    return _update


_izom_propui_free_label_updated = _izom_propui_free_string_limit_updated_with_cache('label', _izom_propui_free_limit_label_input_text)
_izom_propui_free_editor_label_updated = _izom_propui_free_string_limit_updated_with_cache('editor_label', _izom_propui_free_limit_label_input_text)
_izom_propui_free_description_updated = _izom_propui_free_string_limit_updated_with_cache('description', _izom_propui_free_limit_tooltip_input_text)
_izom_propui_free_bool_label_true_updated = _izom_propui_free_string_limit_updated_with_cache('bool_label_true', _izom_propui_free_limit_label_input_text)
_izom_propui_free_bool_label_false_updated = _izom_propui_free_string_limit_updated_with_cache('bool_label_false', _izom_propui_free_limit_label_input_text)


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

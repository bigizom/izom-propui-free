# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from ..core.diagnostics import izom_propui_free_log_recovered

from ..core.context import izom_propui_free_context_params

from ..core.value_access import (
    izom_propui_free_entry_value_kind,
)
from .helpers import (
    _izom_propui_free_active_entry,
    _izom_propui_free_active_collection_item,
    _izom_propui_free_report_operator,
    _izom_propui_free_entry_by_uid,
    _izom_propui_free_self_value_label_companion_key,
    _izom_propui_free_value_label_target_info,
)

IZOM_PROPUI_FREE_VALUE_LABEL_TARGET_MODE_ITEMS = (
    ('SELF', 'This Entry', ''),
)

IZOM_PROPUI_FREE_VALUE_LABEL_TARGET_MODE_ITEMS_WITH_DESCRIPTIONS = (
    ('SELF', 'This Entry', "Edit this entry's own dynamic labels"),
)


def _izom_propui_free_report_value_label_warning(operator, message):
    _izom_propui_free_report_operator(operator, 'WARNING', message)
    return {'FINISHED'}


def _izom_propui_free_value_label_target_mode_label(target_mode):
    return 'Dynamic Labels'


def _izom_propui_free_value_label_operator_entry(context, entry_uid=''):
    params = izom_propui_free_context_params(context)
    target_uid = str(entry_uid or '').strip()
    if params is not None and target_uid:
        entry = _izom_propui_free_entry_by_uid(params, target_uid)
        if entry is not None:
            return entry
    return _izom_propui_free_active_entry(context)


def _izom_propui_free_value_label_companion_key_for_collection(collection_name, entry, collection_owner, field_name, *, reference_entry=None):
    if collection_name == 'value_labels' and str(field_name or '').startswith('target_value_'):
        return lambda candidate, _entry=entry, _reference_entry=reference_entry: _izom_propui_free_self_value_label_companion_key(
            _entry,
            candidate,
            reference_entry=_reference_entry,
        )
    return None


def _izom_propui_free_value_label_editor_context(target_mode):
    return 'VALUE_LABEL_SELF'


def _izom_propui_free_value_label_collection_name(target_mode):
    return 'value_labels'


def _izom_propui_free_resolved_source_target_mode(entry, context, target_mode):
    return 'SELF', _izom_propui_free_value_label_target_info(entry, context, 'SELF')


def _izom_propui_free_active_target_collection_item(info, entry, target_mode):
    if not info:
        return None
    active_owner = info.get('active_owner', entry)
    collection_name = _izom_propui_free_value_label_collection_name(target_mode)
    current = _izom_propui_free_active_collection_item(active_owner, collection_name)
    if current is not None:
        return current

    collection = info.get('collection') or []
    try:
        active_index = int(getattr(active_owner, f"{collection_name}_active_index", 0) or 0)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        active_index = 0
    if 0 <= active_index < len(collection):
        return collection[active_index]
    return None


def _izom_propui_free_threshold_field_name(prop_type, *, field_root='value'):
    root = str(field_root or 'value').strip() or 'value'
    return f"{root}_int" if prop_type == 'INT' else f"{root}_float"


def _izom_propui_free_source_entry_value_kind(source_entry):
    if source_entry is None:
        return ''
    if isinstance(source_entry, dict):
        prop_type = str(source_entry.get('prop_type', '') or '')
    else:
        prop_type = str(getattr(source_entry, 'prop_type', '') or '')
    return str(izom_propui_free_entry_value_kind(source_entry, prop_type) or '').strip().upper()



from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

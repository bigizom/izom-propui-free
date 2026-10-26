# SPDX-License-Identifier: GPL-3.0-or-later

from copy import deepcopy

from rna_prop_ui import (
    rna_idprop_quote_path as _izom_propui_free_rna_idprop_quote_path,
    rna_idprop_ui_create as _izom_propui_free_rna_idprop_ui_create,
)

from ..core.diagnostics import izom_propui_free_log_recovered
from ..core.runtime import (
    _izom_propui_free_build_copy_ui_data_kwargs,
    _izom_propui_free_idprop_runtime_type,
    _izom_propui_free_sequence_value,
    _izom_propui_free_should_skip_import_key,
    _izom_propui_free_value_matches_generic,
    izom_propui_free_runtime_entries,
)


_IZOM_PROPUI_FREE_IDPROP_ACCESS_EXCEPTIONS = (AttributeError, KeyError, LookupError, TypeError)
_IZOM_PROPUI_FREE_IDPROP_UI_EXCEPTIONS = (AttributeError, KeyError, LookupError, TypeError, ValueError)
_IZOM_PROPUI_FREE_DEEPCOPY_EXCEPTIONS = (AttributeError, TypeError, ValueError)
_IZOM_PROPUI_FREE_ARRAY_RUNTIME_TYPES = {'VECTOR', 'INT_ARRAY', 'BOOL_ARRAY'}


def _izom_propui_free_idprop_path(prop_id):
    return _izom_propui_free_rna_idprop_quote_path(str(prop_id or ''))


def _izom_propui_free_has_custom_prop(owner, prop_id):
    if not owner or not prop_id:
        return False

    try:
        return prop_id in owner
    except _IZOM_PROPUI_FREE_IDPROP_ACCESS_EXCEPTIONS:
        return False


def _izom_propui_free_get_idprop_ui(owner, key):
    return owner.id_properties_ui(key)


def _izom_propui_free_get_idprop_ui_data(owner, key):
    try:
        ui = _izom_propui_free_get_idprop_ui(owner, key)
    except _IZOM_PROPUI_FREE_IDPROP_UI_EXCEPTIONS:
        return {}

    as_dict = getattr(ui, "as_dict", None)
    if callable(as_dict):
        try:
            data = as_dict()
        except _IZOM_PROPUI_FREE_IDPROP_UI_EXCEPTIONS:
            return {}
        return data if isinstance(data, dict) else {}

    return {}


def _izom_propui_free_is_library_overridable(owner, prop_id):
    try:
        return bool(owner.is_property_overridable_library(_izom_propui_free_idprop_path(prop_id)))
    except _IZOM_PROPUI_FREE_IDPROP_UI_EXCEPTIONS:
        return False


def _izom_propui_free_set_library_overridable(owner, prop_id, enabled):
    try:
        owner.property_overridable_library_set(_izom_propui_free_idprop_path(prop_id), bool(enabled))
        return True
    except _IZOM_PROPUI_FREE_IDPROP_UI_EXCEPTIONS:
        return False


def _izom_propui_free_clear_custom_prop_ui_data(owner, prop_id):
    if not owner or not prop_id:
        return

    try:
        ui = _izom_propui_free_get_idprop_ui(owner, prop_id)
    except _IZOM_PROPUI_FREE_IDPROP_UI_EXCEPTIONS:
        return

    clear = getattr(ui, "clear", None)
    if callable(clear):
        try:
            clear()
        except _IZOM_PROPUI_FREE_IDPROP_UI_EXCEPTIONS as exc:
            izom_propui_free_log_recovered(
                category='ID Properties',
                exception=exc,
                hint=f'clearing UI data for {prop_id}',
            )


def _izom_propui_free_delete_custom_prop(owner, prop_id):
    try:
        del owner[prop_id]
        return True
    except _IZOM_PROPUI_FREE_IDPROP_ACCESS_EXCEPTIONS:
        return False


def _izom_propui_free_validate_custom_prop_assignment(owner, value):
    if not owner:
        return

    temp_name = "_izom_propui_free_assignment_probe"
    try:
        keys = set(owner.keys())
    except _IZOM_PROPUI_FREE_IDPROP_ACCESS_EXCEPTIONS:
        keys = set()
    index = 1
    while temp_name in keys:
        index += 1
        temp_name = f"_izom_propui_free_assignment_probe_{index}"
    try:
        owner[temp_name] = value
    finally:
        _izom_propui_free_delete_custom_prop(owner, temp_name)


def _izom_propui_free_custom_prop_needs_update(
    owner,
    prop_id,
    desired_value,
    desired_ui_kwargs=None,
    desired_overridable=True,
):
    if not owner or not prop_id:
        return True

    if not _izom_propui_free_has_custom_prop(owner, prop_id):
        return True

    try:
        current_value = owner[prop_id]
    except _IZOM_PROPUI_FREE_IDPROP_ACCESS_EXCEPTIONS:
        return True

    current_ui_kwargs = _izom_propui_free_build_copy_ui_data_kwargs(
        _izom_propui_free_get_idprop_ui_data(owner, prop_id),
        current_value,
    )
    current_overridable = _izom_propui_free_is_library_overridable(owner, prop_id)
    desired_ui_kwargs = dict(desired_ui_kwargs or {})
    desired_ui_kwargs.pop('_skip_ui_default', None)
    desired_description = str(desired_ui_kwargs.get('description', '') or '').strip()
    if desired_description:
        desired_ui_kwargs['description'] = desired_description
    else:
        desired_ui_kwargs.pop('description', None)

    return not (
        _izom_propui_free_value_matches_generic(current_value, desired_value)
        and current_ui_kwargs == desired_ui_kwargs
        and current_overridable == bool(desired_overridable)
    )


def _izom_propui_free_prepare_existing_custom_prop_for_update(owner, prop_id, value):
    if not owner or not prop_id or not _izom_propui_free_has_custom_prop(owner, prop_id):
        return

    try:
        current_value = owner[prop_id]
    except _IZOM_PROPUI_FREE_IDPROP_ACCESS_EXCEPTIONS:
        current_value = None

    current_type = _izom_propui_free_idprop_runtime_type(current_value)
    desired_type = _izom_propui_free_idprop_runtime_type(value)
    if current_type == desired_type:
        if current_type not in _IZOM_PROPUI_FREE_ARRAY_RUNTIME_TYPES:
            return
        current_sequence = _izom_propui_free_sequence_value(current_value)
        desired_sequence = _izom_propui_free_sequence_value(value)
        if current_sequence is not None and desired_sequence is not None and len(current_sequence) == len(desired_sequence):
            return

    _izom_propui_free_clear_custom_prop_ui_data(owner, prop_id)
    _izom_propui_free_delete_custom_prop(owner, prop_id)


def _izom_propui_free_update_existing_custom_prop_value(owner, prop_id, current_value, value):
    current_type = _izom_propui_free_idprop_runtime_type(current_value)
    value_type = _izom_propui_free_idprop_runtime_type(value)
    if current_type == value_type and current_type in _IZOM_PROPUI_FREE_ARRAY_RUNTIME_TYPES:
        sequence = _izom_propui_free_sequence_value(value)
        if sequence is not None:
            for index, component in enumerate(sequence):
                current_value[index] = component
            return
    owner[prop_id] = value


def _izom_propui_free_update_existing_custom_prop_ui_data(owner, prop_id, ui_default_value, description, ui_kwargs, *, skip_default=False):
    ui = _izom_propui_free_get_idprop_ui(owner, prop_id)
    if skip_default:
        ui.update(
            description=description,
            **ui_kwargs,
        )
    else:
        ui.update(
            default=ui_default_value,
            description=description,
            **ui_kwargs,
        )


def _izom_propui_free_create_or_update_custom_prop(owner, prop_id, value, ui_kwargs=None, library_overridable=True, *, assume_missing=False):
    if not owner or not prop_id:
        return False

    kwargs = dict(ui_kwargs or {})
    kwargs.pop('size', None)
    skip_ui_default = bool(kwargs.pop('_skip_ui_default', False))
    ui_default_value = kwargs.pop('default', value)
    description = str(kwargs.pop('description', '') or '').strip() or None
    overridable = bool(library_overridable)
    desired_ui_kwargs = dict(kwargs)
    if not skip_ui_default:
        desired_ui_kwargs['default'] = ui_default_value
    if description:
        desired_ui_kwargs['description'] = description

    if not assume_missing and not _izom_propui_free_custom_prop_needs_update(
        owner,
        prop_id,
        value,
        desired_ui_kwargs=desired_ui_kwargs,
        desired_overridable=overridable,
    ):
        return False

    if not assume_missing:
        _izom_propui_free_prepare_existing_custom_prop_for_update(owner, prop_id, value)
    if _izom_propui_free_idprop_runtime_type(value) == 'PYTHON':
        if not assume_missing and _izom_propui_free_has_custom_prop(owner, prop_id):
            current_value = owner[prop_id]
            if not _izom_propui_free_value_matches_generic(current_value, value):
                _izom_propui_free_validate_custom_prop_assignment(owner, value)
                _izom_propui_free_clear_custom_prop_ui_data(owner, prop_id)
                _izom_propui_free_delete_custom_prop(owner, prop_id)
                owner[prop_id] = value
        else:
            owner[prop_id] = value
        _izom_propui_free_set_library_overridable(owner, prop_id, overridable)
        return True

    if not assume_missing and _izom_propui_free_has_custom_prop(owner, prop_id):
        current_value = owner[prop_id]
        if not _izom_propui_free_value_matches_generic(current_value, value):
            _izom_propui_free_update_existing_custom_prop_value(owner, prop_id, current_value, value)
        _izom_propui_free_update_existing_custom_prop_ui_data(
            owner,
            prop_id,
            ui_default_value,
            description,
            kwargs,
            skip_default=skip_ui_default,
        )
    else:
        create_default = None if skip_ui_default else ui_default_value
        _izom_propui_free_rna_idprop_ui_create(
            owner,
            prop_id,
            default=create_default,
            description=description,
            overridable=overridable,
            **kwargs,
        )
        if not _izom_propui_free_value_matches_generic(value, create_default):
            owner[prop_id] = value
    _izom_propui_free_set_library_overridable(owner, prop_id, overridable)
    return True


def _izom_propui_free_clone_idprop_value(value):
    try:
        return deepcopy(value)
    except _IZOM_PROPUI_FREE_DEEPCOPY_EXCEPTIONS:
        return value


def izom_propui_free_managed_prop_ids(params):
    ids = []
    for entry in izom_propui_free_runtime_entries(params):
        if not bool(entry.get('is_managed_entry', entry.get('prop_type') != 'TEXT')):
            continue
        prop_id = str(entry.get('prop_id', '')).strip()
        if prop_id:
            ids.append(prop_id)
    return ids


def izom_propui_free_list_source_custom_props(owner, exclude_ids=None):
    exclude_ids = set(exclude_ids or [])
    props = []

    for key in owner.keys():
        if _izom_propui_free_should_skip_import_key(key):
            continue
        if key in exclude_ids:
            continue
        props.append({
            'key': key,
            'value': _izom_propui_free_clone_idprop_value(owner[key]),
            'ui_data': _izom_propui_free_get_idprop_ui_data(owner, key),
        })

    return props


def izom_propui_free_remove_custom_props(owner, exclude_ids=None):
    removed = []
    for item in izom_propui_free_list_source_custom_props(owner, exclude_ids=exclude_ids):
        key = item['key']
        _izom_propui_free_clear_custom_prop_ui_data(owner, key)
        if _izom_propui_free_delete_custom_prop(owner, key):
            removed.append(key)
    return removed

# SPDX-License-Identifier: GPL-3.0-or-later

"""Rollback property application when generation fails before output is saved."""

import array
from ..bpy_support.idprops import (
    _izom_propui_free_get_idprop_ui_data,
    _izom_propui_free_is_library_overridable,
    _izom_propui_free_set_library_overridable,
)
from ..core.runtime_idprops import _izom_propui_free_should_skip_import_key
from ..core.cache import izom_propui_free_invalidate_params_cache
from .operators_sync_common import (
    _izom_propui_free_resolved_target_owners,
    _izom_propui_free_resolved_cleanup_target_owners,
    _izom_propui_free_notify_idprop_owners_changed,
)


def _izom_propui_free_detached_property_value(value):
    if hasattr(value, 'to_dict'):
        return {key: _izom_propui_free_detached_property_value(item) for key, item in value.items()}
    if hasattr(value, 'to_list'):
        return array.array(value.typecode, value.to_list())
    # Blender ID references must retain their identity, not be deep-copied.
    return value


class IzomPropUIFreeGenerationTransaction:
    def __init__(self, params):
        self.params = params
        self.committed = False
        self.attrs = {
            name: getattr(params, name)
            for name in ('izom_propui_free_last_synced_prop_ids_json', 'izom_propui_free_generated_panels_json')
            if hasattr(params, name)
        }
        self.entry_ids = [(entry, entry.prop_id) for entry in params.izom_propui_free_entries]
        current = _izom_propui_free_resolved_target_owners(params, entries=params.izom_propui_free_entries, owner_by_path={})
        owners, _missing = _izom_propui_free_resolved_cleanup_target_owners(params, current, owner_by_path={})
        self.owners = []
        for _path, owner in owners:
            properties = {}
            for key in owner.keys():
                if _izom_propui_free_should_skip_import_key(key):
                    continue
                properties[key] = (
                    _izom_propui_free_detached_property_value(owner[key]),
                    _izom_propui_free_get_idprop_ui_data(owner, key),
                    _izom_propui_free_is_library_overridable(owner, key),
                )
            self.owners.append((owner, properties))

    def __enter__(self):
        return self

    def rollback(self):
        for owner, properties in self.owners:
            for key in list(owner.keys()):
                if not _izom_propui_free_should_skip_import_key(key) and key not in properties:
                    del owner[key]
            for key, (value, metadata, overridable) in properties.items():
                if key in owner:
                    current = _izom_propui_free_detached_property_value(owner[key])
                    if (type(current) is type(value) and current == value
                            and getattr(current, 'typecode', None) == getattr(value, 'typecode', None)
                            and _izom_propui_free_get_idprop_ui_data(owner, key) == metadata
                            and _izom_propui_free_is_library_overridable(owner, key) == overridable):
                        continue
                if key in owner:
                    del owner[key]
                owner[key] = value
                if metadata:
                    owner.id_properties_ui(key).update(**metadata)
                _izom_propui_free_set_library_overridable(owner, key, overridable)
        for entry, prop_id in self.entry_ids:
            if entry.prop_id != prop_id:
                entry.prop_id = prop_id
        for name, value in self.attrs.items():
            if getattr(self.params, name) != value:
                setattr(self.params, name, value)
        izom_propui_free_invalidate_params_cache(self.params)
        _izom_propui_free_notify_idprop_owners_changed([owner for owner, _properties in self.owners])

    def __exit__(self, exc_type, exc, traceback):
        if exc_type is not None or not self.committed:
            self.rollback()
        return False

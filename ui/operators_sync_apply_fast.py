# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .operators_sync_values import (
    _izom_propui_free_entry_value_for_owner,
    izom_propui_free_log_recovered,
)
from ..bpy_support.idprops import (
    _izom_propui_free_create_or_update_custom_prop,
    _izom_propui_free_is_library_overridable,
    izom_propui_free_remove_custom_props,
)
from ..core.entry_ids import _izom_propui_free_unique_prop_id
from ..core.runtime_idprops import (
    _izom_propui_free_should_skip_import_key,
    _izom_propui_free_value_matches_generic,
)
from ..core.runtime_ui_kwargs import (
    _izom_propui_free_build_copy_ui_data_kwargs,
    _izom_propui_free_build_entry_custom_prop_ui_kwargs,
)
from ..core.sync_state import (
    _izom_propui_free_load_last_synced_id_map,
    _izom_propui_free_store_last_synced_id_map,
)
from ..core.targets import izom_propui_free_owner_path_label
from .lists_common_value_labels import _izom_propui_free_entry_value
from .operators_sync_common import (
    _izom_propui_free_apply_entry_snapshots,
    _izom_propui_free_current_prop_owner_maps,
    _izom_propui_free_entry_owner_path,
    _izom_propui_free_notify_idprop_owners_changed,
    _izom_propui_free_owner_key,
    _izom_propui_free_resolve_entry_owner,
    _izom_propui_free_resolve_owner_path_cached,
    _izom_propui_free_resolved_target_owners,
    _izom_propui_free_syncable_prop_type,
)



def izom_propui_free_execute_fast_replace_all_managed(self, context, params, default_owner, owner_by_path):
    entries = _izom_propui_free_apply_entry_snapshots(params)
    if not entries:
        return None

    managed_entries = [
        entry for entry in entries
        if _izom_propui_free_syncable_prop_type(entry.get('prop_type'))
    ]
    if not managed_entries:
        return None

    default_owner_key = _izom_propui_free_owner_key(default_owner)
    for entry in managed_entries:
        owner_path = _izom_propui_free_entry_owner_path(params, entry)
        target_owner = _izom_propui_free_resolve_owner_path_cached(owner_path, owner_by_path)
        if target_owner is None:
            self.report({'ERROR'}, f"Could not resolve the target for entry '{entry.get('label', entry.get('prop_id', 'Property'))}'")
            return {'CANCELLED'}

    current_entry_ids_by_owner_path, current_owner_keys_by_prop_id = _izom_propui_free_current_prop_owner_maps(
        params,
        entries,
        owner_by_path=owner_by_path,
    )
    last_synced_id_map = _izom_propui_free_load_last_synced_id_map(params)
    reserved_ids_by_owner_path = {}
    for owner_path, current_entry_ids in current_entry_ids_by_owner_path.items():
        owner = _izom_propui_free_resolve_owner_path_cached(owner_path, owner_by_path)
        if owner is None:
            continue
        previous_ids = set(last_synced_id_map.get(owner_path, set()))
        owner_keys = () if _izom_propui_free_owner_key(owner) == default_owner_key else owner.keys()
        reserved_ids_by_owner_path[owner_path] = {
            key for key in owner_keys
            if not _izom_propui_free_should_skip_import_key(key) and key not in previous_ids and key not in current_entry_ids
        }

    used_ids_by_owner_path = {}
    for entry in managed_entries:
        owner_path = _izom_propui_free_entry_owner_path(params, entry)
        raw = str(entry.get('prop_id', '') or '').strip() or 'prop'
        used_ids = used_ids_by_owner_path.setdefault(owner_path, set())
        unique = _izom_propui_free_unique_prop_id(raw, reserved_ids_by_owner_path.get(owner_path, set()) | used_ids)
        if unique != raw:
            return None
        used_ids.add(unique)

    cleared_for_replace = len(izom_propui_free_remove_custom_props(default_owner))
    resolved_owner_items = _izom_propui_free_resolved_target_owners(
        params,
        entries,
        include_default=True,
        owner_by_path=owner_by_path,
    )
    relevant_owners = [owner for _path, owner in resolved_owner_items]
    if default_owner not in relevant_owners:
        relevant_owners.append(default_owner)

    existing_locations_by_prop_id = {}
    for owner in relevant_owners:
        try:
            owner_key = _izom_propui_free_owner_key(owner)
            for key in owner.keys():
                if not _izom_propui_free_should_skip_import_key(key):
                    existing_locations_by_prop_id.setdefault(str(key), set()).add(owner_key)
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )

    entry_owner_by_uid = {}
    for entry in managed_entries:
        target_owner = _izom_propui_free_resolve_entry_owner(params, entry, owner_by_path)
        if target_owner is None:
            self.report({'ERROR'}, f"Could not resolve the target for entry '{entry.get('label', entry.get('prop_id', 'Property'))}'")
            return {'CANCELLED'}
        entry_owner_by_uid[str(entry.get('uid', '') or '').strip()] = target_owner

    created = 0
    updated = 0
    seen_keys = set()
    target_owner_by_prop_id = {}
    reset_value_prop_keys = {
        (default_owner_key, str(entry.get('prop_id', '') or '').strip())
        for entry in managed_entries
        if _izom_propui_free_owner_key(entry_owner_by_uid.get(str(entry.get('uid', '') or '').strip())) == default_owner_key
        and str(entry.get('prop_id', '') or '').strip()
    }

    for entry in managed_entries:
        prop_id = str(entry.get('prop_id', '') or '').strip()
        target_owner = entry_owner_by_uid.get(str(entry.get('uid', '') or '').strip())
        owner_key = _izom_propui_free_owner_key(target_owner)
        prop_key = (owner_key, prop_id)
        if not prop_id or prop_key in seen_keys:
            continue
        seen_keys.add(prop_key)
        try:
            value, source_owner, _source_type, target_has_prop, current_value, current_ui_data, current_type = _izom_propui_free_entry_value_for_owner(
                entry,
                target_owner,
                relevant_owners,
                prefer_editor_default=(prop_key in reset_value_prop_keys),
            )
        except ValueError as exc:
            self.report({'ERROR'}, f"{entry.get('label', prop_id) or prop_id}: {exc}")
            return {'CANCELLED'}
        if value is None:
            continue
        target_owner_by_prop_id.setdefault(prop_id, set()).add(owner_key)

        desired_ui_kwargs = _izom_propui_free_build_entry_custom_prop_ui_kwargs(entry, prop_id, fallback_value=value)
        desired_ui_kwargs_for_compare = dict(desired_ui_kwargs or {})
        desired_ui_kwargs_for_compare.pop('_skip_ui_default', None)
        desired_overridable = bool(_izom_propui_free_entry_value(entry, 'library_overridable', True))
        existed_anywhere = bool(existing_locations_by_prop_id.get(prop_id))
        existed_on_target_before_apply = target_has_prop

        needs_update = True
        if target_has_prop:
            try:
                current_ui_kwargs = _izom_propui_free_build_copy_ui_data_kwargs(current_ui_data, current_value)
                current_overridable = _izom_propui_free_is_library_overridable(target_owner, prop_id)
                needs_update = (
                    not _izom_propui_free_value_matches_generic(current_value, value)
                    or (current_type != entry.get('prop_type'))
                    or (current_ui_kwargs != desired_ui_kwargs_for_compare)
                    or (current_overridable != desired_overridable)
                )
            except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )
                needs_update = True
        if not needs_update:
            continue
        try:
            _izom_propui_free_create_or_update_custom_prop(
                target_owner,
                prop_id,
                value,
                ui_kwargs=desired_ui_kwargs,
                library_overridable=desired_overridable,
                assume_missing=not target_has_prop,
            )
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            self.report({'ERROR'}, f"{entry.get('label', prop_id) or prop_id}: {exc}")
            return {'CANCELLED'}
        if existed_on_target_before_apply:
            updated += 1
        elif existed_anywhere and source_owner is not None and source_owner != target_owner:
            created += 1
        elif existed_anywhere:
            updated += 1
        else:
            created += 1

    for owner_path, current_entry_ids in current_entry_ids_by_owner_path.items():
        if current_entry_ids:
            last_synced_id_map[owner_path] = set(current_entry_ids)
        else:
            last_synced_id_map.pop(owner_path, None)
    _izom_propui_free_store_last_synced_id_map(params, last_synced_id_map)

    if created == 0 and updated == 0 and cleared_for_replace == 0:
        self.report({'INFO'}, "Nothing to do on the resolved targets")
        return {'FINISHED'}

    _izom_propui_free_notify_idprop_owners_changed(relevant_owners)

    target_labels = sorted({
        izom_propui_free_owner_path_label(_izom_propui_free_entry_owner_path(params, entry))
        for entry in managed_entries
    })
    target_label = target_labels[0] if len(target_labels) == 1 else "multiple targets"
    message = f"Applied PropUI properties on {target_label}: created {created}, updated {updated}"
    if cleared_for_replace:
        message += f"; cleared {cleared_for_replace} custom propert{'y' if cleared_for_replace == 1 else 'ies'} from Property Storage"
    self.report({'INFO'}, message)
    return {'FINISHED'}


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

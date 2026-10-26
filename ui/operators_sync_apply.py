# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from types import SimpleNamespace

from .operators_sync_values import (
    _izom_propui_free_entry_value_for_owner,
    _izom_propui_free_has_custom_prop,
    izom_propui_free_log_recovered,
)
from .operators_sync_apply_fast import izom_propui_free_execute_fast_replace_all_managed
from ..bpy_support.idprops import (
    _izom_propui_free_clear_custom_prop_ui_data,
    _izom_propui_free_create_or_update_custom_prop,
    _izom_propui_free_is_library_overridable,
    izom_propui_free_remove_custom_props,
)
from ..core.context import izom_propui_free_context_params
from ..core.entry_ids import _izom_propui_free_unique_prop_id
from ..core.runtime_idprops import (
    _izom_propui_free_should_skip_import_key,
    _izom_propui_free_value_matches_generic,
)
from ..core.runtime_ui_kwargs import (
    _izom_propui_free_build_copy_ui_data_kwargs,
    _izom_propui_free_build_entry_custom_prop_ui_kwargs,
)
from ..core.snapshot_entries_consistency import (
    _izom_propui_free_active_uid,
    izom_propui_free_ensure_consistency,
)
from ..core.snapshot_entries_restore import izom_propui_free_restore_entries
from ..core.snapshot_entries_runtime import (
    izom_propui_free_snapshot_entries,
    izom_propui_free_snapshot_runtime_entries,
)
from ..core.sync_state import (
    _izom_propui_free_load_last_synced_id_map,
    _izom_propui_free_store_last_synced_id_map,
)
from ..core.targets import izom_propui_free_owner_path_label
from .lists_common_value_labels import _izom_propui_free_entry_value
from .operators_sync_common import (
    _izom_propui_free_clean_old_targets_for_apply,
    _izom_propui_free_current_prop_owner_maps,
    _izom_propui_free_default_owner_path,
    _izom_propui_free_entries_for_sync_mode,
    _izom_propui_free_entry_owner_path,
    _izom_propui_free_native_conflict_prop_keys,
    _izom_propui_free_native_conflicts_by_owner_path,
    _izom_propui_free_notify_idprop_owners_changed,
    _izom_propui_free_owner_key,
    _izom_propui_free_replace_storage_for_apply,
    _izom_propui_free_resolve_entry_owner,
    _izom_propui_free_resolve_owner_path_cached,
    _izom_propui_free_resolved_cleanup_target_owners,
    _izom_propui_free_resolved_target_owners,
    _izom_propui_free_syncable_prop_type,
)

class _IZOM_PROPUI_FREE_ApplyTargetPropsRunner:
    def __init__(
            self,
            reporter=None,
            *,
            replace_storage_mode='APPLY_SETTING',
            clean_old_targets_mode='APPLY_SETTING',
            native_conflict_action='OVERWRITE',
            native_conflicts_confirmed=False,
            skip_consistency=False,
    ):
        self._reporter = reporter
        self.replace_storage_mode = replace_storage_mode
        self.clean_old_targets_mode = clean_old_targets_mode
        self.native_conflict_action = native_conflict_action
        self.native_conflicts_confirmed = native_conflicts_confirmed
        self.skip_consistency = skip_consistency
        self.renamed = []

    def report(self, levels, message):
        if self._reporter is not None:
            try:
                self._reporter.report(levels, message)
                return
            except (RuntimeError, ValueError, TypeError, AttributeError, ReferenceError):
                pass

    def _execute_fast_replace_all_managed(self, context, params, default_owner, owner_by_path):
        return izom_propui_free_execute_fast_replace_all_managed(self, context, params, default_owner, owner_by_path)

    def execute(self, context=None, *, params=None):
        ctx_or_result = self._apply_context(context, params=params)
        if not isinstance(ctx_or_result, SimpleNamespace):
            return ctx_or_result
        ctx = ctx_or_result

        fast_result = self._maybe_execute_fast_apply(context, ctx)
        if fast_result is not None:
            return fast_result

        result = self._prepare_apply_snapshots(context, ctx)
        if result is not None:
            return result
        result = self._validate_apply_snapshots(ctx)
        if result is not None:
            return result

        if ctx.replace_storage:
            ctx.cleared_for_replace = len(izom_propui_free_remove_custom_props(ctx.default_owner))

        self._prepare_current_owner_maps(ctx)
        self._rename_conflicting_prop_ids(context, ctx)
        self._prepare_apply_entries_and_targets(context, ctx)
        result = self._prepare_native_conflict_actions(ctx)
        if result is not None:
            return result
        result = self._apply_entries_to_targets(ctx)
        if result is not None:
            return result
        self._clean_old_targets(ctx)
        self._store_last_synced_metadata(ctx)
        return self._report_apply_result(ctx)

    def _apply_context(self, context=None, *, params=None):
        if params is None:
            params = izom_propui_free_context_params(context)
        if params is None:
            return {'CANCELLED'}
        if not bool(getattr(self, 'skip_consistency', False)):
            izom_propui_free_ensure_consistency(params)

        owner_by_path = {}
        default_owner = _izom_propui_free_resolve_owner_path_cached(
            _izom_propui_free_default_owner_path(params),
            owner_by_path,
        )
        if default_owner is None:
            self.report({'ERROR'}, "Set a valid Property Storage target before applying properties")
            return {'CANCELLED'}

        return SimpleNamespace(
            params=params,
            sync_mode='ALL_MANAGED',
            owner_by_path=owner_by_path,
            default_owner=default_owner,
            replace_storage=_izom_propui_free_replace_storage_for_apply(
                params,
                getattr(self, 'replace_storage_mode', 'APPLY_SETTING'),
            ),
            clean_old_targets=_izom_propui_free_clean_old_targets_for_apply(
                params,
                getattr(self, 'clean_old_targets_mode', 'APPLY_SETTING'),
            ),
            cleared_for_replace=0,
            snapshots=[],
            processed_snapshots=[],
            active_uid='',
            current_entry_ids_by_owner_path={},
            current_owner_keys_by_prop_id={},
            processed_entry_ids_by_owner_path={},
            last_synced_id_map=_izom_propui_free_load_last_synced_id_map(params),
            entries=[],
            resolved_owner_items=[],
            cleanup_owner_items=[],
            missing_cleanup_owner_paths=[],
            relevant_owners=[],
            native_conflicts={},
            skipped_conflict_prop_keys=set(),
            reset_value_prop_keys=set(),
            renamed=[],
            created=0,
            updated=0,
            moved=0,
            target_owner_by_prop_id={},
        )

    def _maybe_execute_fast_apply(self, context, ctx):
        if ctx.sync_mode == 'ALL_MANAGED' and ctx.replace_storage and not ctx.clean_old_targets:
            return self._execute_fast_replace_all_managed(
                context,
                ctx.params,
                ctx.default_owner,
                ctx.owner_by_path,
            )
        return None

    def _prepare_apply_snapshots(self, context, ctx):
        ctx.snapshots = izom_propui_free_snapshot_runtime_entries(ctx.params)
        ctx.processed_snapshots = ctx.snapshots
        return None

    def _validate_apply_snapshots(self, ctx):
        for snap in ctx.processed_snapshots:
            if not _izom_propui_free_syncable_prop_type(snap.get('prop_type')):
                continue
            owner_path = _izom_propui_free_entry_owner_path(ctx.params, snap)
            if owner_path and _izom_propui_free_resolve_owner_path_cached(owner_path, ctx.owner_by_path) is None:
                self.report({'ERROR'}, f"Could not resolve the target for entry '{snap.get('label', snap.get('prop_id', 'Property'))}'")
                return {'CANCELLED'}
        return None

    def _prepare_current_owner_maps(self, ctx):
        ctx.active_uid = _izom_propui_free_active_uid(ctx.params)
        ctx.current_entry_ids_by_owner_path, ctx.current_owner_keys_by_prop_id = _izom_propui_free_current_prop_owner_maps(
            ctx.params,
            ctx.snapshots,
            owner_by_path=ctx.owner_by_path,
        )
        ctx.reserved_ids_by_owner_path = self._reserved_ids_by_owner_path(ctx)

    def _reserved_ids_by_owner_path(self, ctx):
        reserved = {}
        for owner_path, current_entry_ids in ctx.current_entry_ids_by_owner_path.items():
            owner = _izom_propui_free_resolve_owner_path_cached(owner_path, ctx.owner_by_path)
            if owner is None:
                continue
            previous_ids = set(ctx.last_synced_id_map.get(owner_path, set()))
            reserved[owner_path] = {
                key for key in owner.keys()
                if not _izom_propui_free_should_skip_import_key(key) and key not in previous_ids and key not in current_entry_ids
            }
        return reserved

    def _rename_conflicting_prop_ids(self, context, ctx):
        used_ids_by_owner_path = {}
        renamed_prop_id_by_uid = {}
        changed_ids = False
        for snap in ctx.processed_snapshots:
            if not _izom_propui_free_syncable_prop_type(snap.get('prop_type')):
                continue
            owner_path = _izom_propui_free_entry_owner_path(ctx.params, snap)
            owner = _izom_propui_free_resolve_owner_path_cached(owner_path, ctx.owner_by_path)
            if owner is None:
                continue
            raw = str(snap.get('prop_id', '') or '').strip() or 'prop'
            used_ids = used_ids_by_owner_path.setdefault(owner_path, set())
            unique = _izom_propui_free_unique_prop_id(raw, ctx.reserved_ids_by_owner_path.get(owner_path, set()) | used_ids)
            if unique != raw:
                snap['prop_id'] = unique
                snap_uid = str(snap.get('uid', '') or '').strip()
                if snap_uid:
                    renamed_prop_id_by_uid[snap_uid] = unique
                ctx.renamed.append((raw, unique))
                changed_ids = True
            used_ids.add(unique)
        if not changed_ids:
            return
        self._apply_renamed_prop_ids(context, ctx, renamed_prop_id_by_uid)

    def _apply_renamed_prop_ids(self, context, ctx, renamed_prop_id_by_uid):
        full_snapshots = izom_propui_free_snapshot_entries(ctx.params, limit_strings=False)
        for full_snap in full_snapshots:
            full_uid = str(full_snap.get('uid', '') or '').strip()
            if full_uid in renamed_prop_id_by_uid:
                full_snap['prop_id'] = renamed_prop_id_by_uid[full_uid]
        ctx.snapshots = full_snapshots
        ctx.processed_snapshots = ctx.snapshots
        izom_propui_free_restore_entries(ctx.params, ctx.snapshots, active_uid=ctx.active_uid)
        izom_propui_free_ensure_consistency(ctx.params)
        ctx.snapshots = izom_propui_free_snapshot_entries(ctx.params, limit_strings=False)
        ctx.processed_snapshots = ctx.snapshots
        ctx.current_entry_ids_by_owner_path, ctx.current_owner_keys_by_prop_id = _izom_propui_free_current_prop_owner_maps(
            ctx.params,
            ctx.snapshots,
            owner_by_path=ctx.owner_by_path,
        )

    def _prepare_apply_entries_and_targets(self, context, ctx):
        ctx.entries = _izom_propui_free_entries_for_sync_mode(context, ctx.params, 'ALL_MANAGED', snapshots=ctx.snapshots)
        ctx.processed_entry_ids_by_owner_path, _processed_owner_keys_by_prop_id = _izom_propui_free_current_prop_owner_maps(
            ctx.params,
            ctx.entries,
            owner_by_path=ctx.owner_by_path,
        )
        ctx.resolved_owner_items = _izom_propui_free_resolved_target_owners(
            ctx.params,
            ctx.entries,
            include_default=True,
            owner_by_path=ctx.owner_by_path,
        )
        if ctx.clean_old_targets:
            ctx.cleanup_owner_items, ctx.missing_cleanup_owner_paths = _izom_propui_free_resolved_cleanup_target_owners(
                ctx.params,
                ctx.resolved_owner_items,
                owner_by_path=ctx.owner_by_path,
            )
        ctx.relevant_owners = [owner for _path, owner in ctx.resolved_owner_items]
        if ctx.default_owner not in ctx.relevant_owners:
            ctx.relevant_owners.append(ctx.default_owner)

    def _prepare_native_conflict_actions(self, ctx):
        ctx.native_conflicts = {}
        ctx.skipped_conflict_prop_keys = set()
        ctx.reset_value_prop_keys = set()
        if ctx.replace_storage:
            self._prepare_replace_storage_reset_keys(ctx)
            return None

        ctx.native_conflicts = _izom_propui_free_native_conflicts_by_owner_path(
            ctx.params,
            ctx.entries,
            owner_by_path=ctx.owner_by_path,
        )
        if ctx.native_conflicts and not bool(getattr(self, 'native_conflicts_confirmed', False)):
            self.report({'WARNING'}, "Resolve custom property conflicts before applying managed properties")
            return {'CANCELLED'}
        if ctx.native_conflicts:
            self._resolve_native_conflicts(ctx)
        return None

    def _prepare_replace_storage_reset_keys(self, ctx):
        default_owner_key = _izom_propui_free_owner_key(ctx.default_owner)
        for entry in ctx.entries:
            if not _izom_propui_free_syncable_prop_type(entry.get('prop_type')):
                continue
            if _izom_propui_free_resolve_entry_owner(ctx.params, entry, ctx.owner_by_path) != ctx.default_owner:
                continue
            prop_id = str(entry.get('prop_id', '') or '').strip()
            if prop_id:
                ctx.reset_value_prop_keys.add((default_owner_key, prop_id))

    def _resolve_native_conflicts(self, ctx):
        conflict_keys = _izom_propui_free_native_conflict_prop_keys(ctx.native_conflicts, owner_by_path=ctx.owner_by_path)
        action = str(getattr(self, 'native_conflict_action', 'OVERWRITE') or 'OVERWRITE').strip().upper()
        if action == 'SKIP':
            ctx.skipped_conflict_prop_keys = conflict_keys
            return
        for owner_path, prop_ids in ctx.native_conflicts.items():
            owner = _izom_propui_free_resolve_owner_path_cached(owner_path, ctx.owner_by_path)
            if owner is None:
                continue
            previously_synced = set(ctx.last_synced_id_map.get(owner_path, set()))
            owner_key = _izom_propui_free_owner_key(owner)
            for prop_id in prop_ids:
                if prop_id in previously_synced:
                    continue
                ctx.reset_value_prop_keys.add((owner_key, prop_id))
                _izom_propui_free_clear_custom_prop_ui_data(owner, prop_id)
                try:
                    if prop_id in owner:
                        del owner[prop_id]
                except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                    izom_propui_free_log_recovered(
                        category='UI',
                        exception=exc,
                    )

    def _apply_entries_to_targets(self, ctx):
        ctx.created = 0
        ctx.updated = 0
        ctx.moved = 0
        ctx.target_owner_by_prop_id = {}
        seen_keys = set()
        existing_locations_by_prop_id = self._existing_locations_by_prop_id(ctx)
        entry_owner_by_uid = self._entry_owner_by_uid(ctx)
        if entry_owner_by_uid is None:
            return {'CANCELLED'}

        for entry in ctx.entries:
            if not _izom_propui_free_syncable_prop_type(entry.get('prop_type')):
                continue
            result = self._apply_single_entry_to_target(
                ctx,
                entry,
                entry_owner_by_uid,
                existing_locations_by_prop_id,
                seen_keys,
            )
            if result is not None:
                return result
        return None

    def _existing_locations_by_prop_id(self, ctx):
        existing_locations_by_prop_id = {}
        for owner in ctx.relevant_owners:
            try:
                for key in owner.keys():
                    if not _izom_propui_free_should_skip_import_key(key):
                        existing_locations_by_prop_id.setdefault(str(key), set()).add(_izom_propui_free_owner_key(owner))
            except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )
        return existing_locations_by_prop_id

    def _entry_owner_by_uid(self, ctx):
        entry_owner_by_uid = {}
        for entry in ctx.entries:
            if not _izom_propui_free_syncable_prop_type(entry.get('prop_type')):
                continue
            target_owner = _izom_propui_free_resolve_entry_owner(ctx.params, entry, ctx.owner_by_path)
            if target_owner is None:
                self.report({'ERROR'}, f"Could not resolve the target for entry '{entry.get('label', entry.get('prop_id', 'Property'))}'")
                return None
            entry_owner_by_uid[str(entry.get('uid', '') or '').strip()] = target_owner
        return entry_owner_by_uid

    def _apply_single_entry_to_target(self, ctx, entry, entry_owner_by_uid, existing_locations_by_prop_id, seen_keys):
        prop_id = str(entry.get('prop_id', '') or '').strip()
        target_owner = entry_owner_by_uid.get(str(entry.get('uid', '') or '').strip())
        owner_key = _izom_propui_free_owner_key(target_owner)
        prop_key = (owner_key, prop_id)
        if not prop_id or prop_key in seen_keys or prop_key in ctx.skipped_conflict_prop_keys:
            return None
        seen_keys.add(prop_key)
        value_result = self._entry_value_for_apply(ctx, entry, target_owner, prop_key, prop_id)
        if not isinstance(value_result, tuple):
            return value_result
        value, source_owner, target_has_prop, current_value, current_ui_data, current_type = value_result
        if value is None:
            return None
        entry['_current_value'] = value
        ctx.target_owner_by_prop_id.setdefault(prop_id, set()).add(owner_key)

        desired_ui_kwargs = _izom_propui_free_build_entry_custom_prop_ui_kwargs(entry, prop_id, fallback_value=value)
        desired_ui_kwargs_for_compare = dict(desired_ui_kwargs or {})
        desired_ui_kwargs_for_compare.pop('_skip_ui_default', None)
        desired_overridable = bool(_izom_propui_free_entry_value(entry, 'library_overridable', True))
        existed_anywhere = bool(existing_locations_by_prop_id.get(prop_id))
        existed_on_target_before_apply = target_has_prop
        if not self._entry_needs_apply_update(
            entry,
            target_owner,
            prop_id,
            value,
            current_value,
            current_ui_data,
            current_type,
            desired_ui_kwargs_for_compare,
            desired_overridable,
            target_has_prop,
        ):
            return None
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
        self._record_apply_update_counts(ctx, existed_on_target_before_apply, existed_anywhere, source_owner, target_owner)
        return None

    def _entry_value_for_apply(self, ctx, entry, target_owner, prop_key, prop_id):
        try:
            value, source_owner, _source_type, target_has_prop, current_value, current_ui_data, current_type = _izom_propui_free_entry_value_for_owner(
                entry,
                target_owner,
                ctx.relevant_owners,
                prefer_editor_default=(prop_key in ctx.reset_value_prop_keys),
            )
        except ValueError as exc:
            self.report({'ERROR'}, f"{entry.get('label', prop_id) or prop_id}: {exc}")
            return {'CANCELLED'}
        return value, source_owner, target_has_prop, current_value, current_ui_data, current_type

    def _entry_needs_apply_update(
        self,
        entry,
        target_owner,
        prop_id,
        value,
        current_value,
        current_ui_data,
        current_type,
        desired_ui_kwargs_for_compare,
        desired_overridable,
        target_has_prop,
    ):
        if not target_has_prop:
            return True
        try:
            current_overridable = _izom_propui_free_is_library_overridable(target_owner, prop_id)
            current_ui_kwargs = _izom_propui_free_build_copy_ui_data_kwargs(current_ui_data, current_value)
            return (
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
            return True

    def _record_apply_update_counts(self, ctx, existed_on_target_before_apply, existed_anywhere, source_owner, target_owner):
        if existed_on_target_before_apply:
            ctx.updated += 1
        elif existed_anywhere and source_owner is not None and source_owner != target_owner:
            ctx.created += 1
        elif existed_anywhere:
            ctx.updated += 1
        else:
            ctx.created += 1

    def _clean_old_targets(self, ctx):
        if not ctx.clean_old_targets:
            return
        previous_synced_ids_by_owner_path = ctx.last_synced_id_map
        current_cleanup_owner_keys = {
            _izom_propui_free_owner_key(owner)
            for _owner_path, owner in ctx.resolved_owner_items
            if owner is not None
        }
        current_cleanup_prop_ids = set(ctx.target_owner_by_prop_id)
        for owner_path, owner in ctx.cleanup_owner_items:
            self._clean_old_target_owner(
                ctx,
                owner_path,
                owner,
                previous_synced_ids_by_owner_path,
                current_cleanup_owner_keys,
                current_cleanup_prop_ids,
            )

    def _clean_old_target_owner(
        self,
        ctx,
        owner_path,
        owner,
        previous_synced_ids_by_owner_path,
        current_cleanup_owner_keys,
        current_cleanup_prop_ids,
    ):
        owner_key = _izom_propui_free_owner_key(owner)
        prop_ids_to_check = set(current_cleanup_prop_ids) if owner_key in current_cleanup_owner_keys else set()
        prop_ids_to_check.update(previous_synced_ids_by_owner_path.get(owner_path, set()))
        for prop_id in prop_ids_to_check:
            target_owner_keys = ctx.target_owner_by_prop_id.get(prop_id, set())
            if owner_key in target_owner_keys:
                continue
            if owner_key in ctx.current_owner_keys_by_prop_id.get(prop_id, set()):
                continue
            had_prop = _izom_propui_free_has_custom_prop(owner, prop_id)
            _izom_propui_free_clear_custom_prop_ui_data(owner, prop_id)
            if not had_prop:
                continue
            try:
                del owner[prop_id]
                ctx.moved += 1
            except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )

    def _store_last_synced_metadata(self, ctx):
        if ctx.skipped_conflict_prop_keys and ctx.native_conflicts:
            self._remove_skipped_conflicts_from_metadata_sets(ctx)
        if ctx.clean_old_targets:
            ctx.last_synced_id_map = {
                owner_path: set(current_entry_ids)
                for owner_path, current_entry_ids in ctx.current_entry_ids_by_owner_path.items()
                if owner_path and current_entry_ids
            }
        else:
            for owner_path, current_entry_ids in ctx.current_entry_ids_by_owner_path.items():
                if current_entry_ids:
                    ctx.last_synced_id_map[owner_path] = set(current_entry_ids)
                else:
                    ctx.last_synced_id_map.pop(owner_path, None)
        _izom_propui_free_store_last_synced_id_map(ctx.params, ctx.last_synced_id_map)

    def _remove_skipped_conflicts_from_metadata_sets(self, ctx):
        for owner_path, prop_ids in ctx.native_conflicts.items():
            if owner_path in ctx.current_entry_ids_by_owner_path:
                ctx.current_entry_ids_by_owner_path[owner_path] -= set(prop_ids)
            if owner_path in ctx.processed_entry_ids_by_owner_path:
                ctx.processed_entry_ids_by_owner_path[owner_path] -= set(prop_ids)

    def _report_apply_result(self, ctx):
        if (
            ctx.created == 0
            and ctx.updated == 0
            and ctx.moved == 0
            and not ctx.renamed
            and ctx.cleared_for_replace == 0
        ):
            self.report({'INFO'}, "Nothing to do on the resolved targets")
            return {'FINISHED'}

        _izom_propui_free_notify_idprop_owners_changed(
            [owner for _path, owner in ctx.resolved_owner_items]
            + [owner for _path, owner in ctx.cleanup_owner_items]
            + [ctx.default_owner]
        )

        target_labels = sorted({
            izom_propui_free_owner_path_label(_izom_propui_free_entry_owner_path(ctx.params, entry))
            for entry in ctx.entries
            if _izom_propui_free_syncable_prop_type(entry.get('prop_type'))
        })
        target_label = target_labels[0] if len(target_labels) == 1 else "multiple targets"
        message = f"Applied PropUI properties on {target_label}: created {ctx.created}, updated {ctx.updated}"
        if ctx.cleared_for_replace:
            message += f"; cleared {ctx.cleared_for_replace} custom propert{'y' if ctx.cleared_for_replace == 1 else 'ies'} from Property Storage"
        if ctx.moved:
            message += f"; cleaned {ctx.moved} matching managed propert{'y' if ctx.moved == 1 else 'ies'} from old targets"
        if ctx.renamed:
            message += f"; auto-renamed {len(ctx.renamed)} conflicting Property ID{'s' if len(ctx.renamed) != 1 else ''}"
        if ctx.skipped_conflict_prop_keys:
            message += f"; skipped {len(ctx.skipped_conflict_prop_keys)} native conflict{'s' if len(ctx.skipped_conflict_prop_keys) != 1 else ''}"
        self.report({'INFO'}, message)
        return {'FINISHED'}


def izom_propui_free_apply_target_props_internal(
        reporter,
        params,
        *,
        replace_storage_mode='APPLY_SETTING',
        clean_old_targets_mode='APPLY_SETTING',
        native_conflict_action='OVERWRITE',
        native_conflicts_confirmed=False,
        skip_consistency=False,
):
    runner = _IZOM_PROPUI_FREE_ApplyTargetPropsRunner(
        reporter,
        replace_storage_mode=replace_storage_mode,
        clean_old_targets_mode=clean_old_targets_mode,
        native_conflict_action=native_conflict_action,
        native_conflicts_confirmed=native_conflicts_confirmed,
        skip_consistency=skip_consistency,
    )
    return runner.execute(params=params)


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

# SPDX-License-Identifier: GPL-3.0-or-later

from .generated_storage_transaction import IzomPropUIFreeGenerationTransaction
from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
import time

from .generated_operators_generate_timing import (
    _izom_propui_free_generate_timing_log,
    _izom_propui_free_generate_timing_mark,
    _izom_propui_free_generate_timing_reset,
    time,
)
from .generated_operators_generate_state import (
    _izom_propui_free_capture_generate_editor_state,
    _izom_propui_free_restore_generate_editor_state,
)
from .generated_operators_generate_consistency import (
    _izom_propui_free_ensure_generate_consistency,
)
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty,
)
from bpy.types import Operator
from ..core.constants_display import (
    IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TAB,
    IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TITLE,
)
from ..core.context import izom_propui_free_context_params
from ..core.runtime_entries import izom_propui_free_runtime_entries
from ..core.runtime_layout import izom_propui_free_runtime_layout_entries
from ..core.targets import izom_propui_free_resolve_owner_path
from .confirmations import izom_propui_free_confirmation_value
from .generated_branding import (
    izom_propui_free_generated_branding_from_params,
    izom_propui_free_resolve_generated_branding,
)
from .generated_registry_scripts import restore_generated_panel_from_scenes
from .generated_slots_common import _izom_propui_free_new_generated_slot_uid
from .generated_slots_storage import (
    _izom_propui_free_generated_slots_from_params,
    _izom_propui_free_store_generated_slots,
)
from .generated_source_build import izom_propui_free_build_generated_draw_source
from .generated_source_prepare import (
    _izom_propui_free_prepare_generated_entries,
)
from .operators_sync_common import (
    _IZOM_PROPUI_FREE_NATIVE_CONFLICT_ACTION_ITEMS,
    _izom_propui_free_native_conflict_summary,
    _izom_propui_free_native_conflicts_by_owner_path,
)
from .operators_sync_apply import izom_propui_free_apply_target_props_internal


def _izom_propui_free_slot_text_key(value, fallback=''):
    return (str(value or '').strip() or str(fallback or '').strip()).casefold()


def _izom_propui_free_sidebar_destinations_overlap(left_slot, right_slot):
    left_tab = _izom_propui_free_slot_text_key((left_slot or {}).get('tab'), IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TAB)
    right_tab = _izom_propui_free_slot_text_key((right_slot or {}).get('tab'), IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TAB)
    return left_tab == right_tab


def _izom_propui_free_generated_slots_match_current_identity(left_slot, right_slot):
    left_title = _izom_propui_free_slot_text_key(
        (left_slot or {}).get('title'),
        IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TITLE,
    )
    right_title = _izom_propui_free_slot_text_key(
        (right_slot or {}).get('title'),
        IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TITLE,
    )
    if left_title != right_title:
        return False
    return _izom_propui_free_sidebar_destinations_overlap(left_slot, right_slot)


def _izom_propui_free_current_generated_slot_identity(params):
    if params is None:
        return {}
    return {
        'tab': str(getattr(params, 'izom_propui_free_generated_panel_tab', '') or '').strip()
        or IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TAB,
        'title': str(getattr(params, 'izom_propui_free_generated_panel_title', '') or '').strip()
        or IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TITLE,
        'target_path': str(getattr(params, 'izom_propui_free_default_target_owner_path', '') or '').strip(),
    }


class IZOM_PROPUI_FREE_OT_generate_ui(Operator):
    bl_idname = "wm.izom_propui_free_generate_ui"
    bl_label = "Generate UI"
    bl_description = "Apply managed properties and generate the standalone PropUI panel"
    bl_options = {'UNDO'}

    message: StringProperty(default="", options={'HIDDEN'})
    current_conflict_action: EnumProperty(
        name="Current Generated UI",
        description="Choose whether Generate overwrites the existing saved UI",
        items=(
            ('OVERWRITE', 'Overwrite Existing', 'Update the existing generated UI for the current editor state'),
        ),
        default='OVERWRITE',
    )
    empty_layout_action: EnumProperty(
        name="Empty Generated Layout",
        description="Choose what Generate should do when entries exist but Generated Layout is empty",
        items=(
            ('CANCEL', 'Cancel', 'Skip generation entirely'),
        ),
        default='CANCEL',
    )
    native_conflict_action: EnumProperty(
        name="Native Property Conflicts",
        description="Choose how to handle managed Property IDs that already exist as native custom properties",
        items=_IZOM_PROPUI_FREE_NATIVE_CONFLICT_ACTION_ITEMS,
        default='OVERWRITE',
    )
    native_conflicts_confirmed: BoolProperty(
        default=False,
        options={'HIDDEN'},
    )
    replace_storage_confirmed: BoolProperty(default=False, options={'HIDDEN', 'SKIP_SAVE'})
    native_conflict_summary: StringProperty(
        default="",
        options={'HIDDEN'},
    )
    popup_kind: EnumProperty(
        name="Popup Kind",
        items=(
            ('NONE', 'None', ''),
            ('REPLACE_STORAGE', 'Replace Storage', ''),
            ('EMPTY_LAYOUT', 'Empty Layout', ''),
            ('CURRENT_CONFLICT', 'Current Conflict', ''),
            ('NATIVE_CONFLICT', 'Native Conflict', ''),
            ('EMPTY_LAYOUT_AND_NATIVE_CONFLICT', 'Empty Layout And Native Conflict', ''),
            ('CURRENT_AND_NATIVE_CONFLICT', 'Current And Native Conflict', ''),
        ),
        default='NONE',
        options={'HIDDEN'},
    )

    @classmethod
    def poll(cls, context):
        return izom_propui_free_context_params(context) is not None

    def _slot_with_current_identity_exists(self, params):
        current_identity = _izom_propui_free_current_generated_slot_identity(params)
        for slot in _izom_propui_free_generated_slots_from_params(params):
            if _izom_propui_free_generated_slots_match_current_identity(slot, current_identity):
                return True
        return False

    def _current_editor_has_empty_layout(self, params):
        entries = getattr(params, 'izom_propui_free_entries', None) or []
        layout_items = getattr(params, 'izom_propui_free_layout_items', None) or []
        return len(entries) > 0 and len(layout_items) == 0

    def invoke(self, context, _event):
        params = izom_propui_free_context_params(context)
        if params is None:
            return {'CANCELLED'}

        # Default both actions before deciding which (if any) popup to surface.
        self.current_conflict_action = 'OVERWRITE'
        self.empty_layout_action = 'CANCEL'
        self.native_conflict_action = 'OVERWRITE'
        self.native_conflicts_confirmed = False
        self.replace_storage_confirmed = False
        self.native_conflict_summary = ''
        self.popup_kind = 'NONE'

        needs_native_conflict_prompt = False
        if not bool(getattr(params, 'izom_propui_free_replace_storage_on_generate', False)):
            current_editor_entries = izom_propui_free_runtime_entries(params)
            current_editor_native_conflicts = _izom_propui_free_native_conflicts_by_owner_path(params, current_editor_entries)
            if current_editor_native_conflicts:
                self.native_conflict_summary = _izom_propui_free_native_conflict_summary(current_editor_native_conflicts)
                native_behavior = izom_propui_free_confirmation_value(
                    params,
                    'izom_propui_free_confirmation_generate_native_conflict',
                    default='ASK',
                )
                if native_behavior in {'OVERWRITE', 'SKIP'}:
                    self.native_conflict_action = native_behavior
                    self.native_conflicts_confirmed = True
                else:
                    needs_native_conflict_prompt = True

        if self._current_editor_has_empty_layout(params):
            self.report({'INFO'}, "Skipped Generate (no entries in Generated Layout)")
            return {'CANCELLED'}

        if bool(getattr(params, 'izom_propui_free_replace_storage_on_generate', False)):
            self.replace_storage_confirmed = True
            self.popup_kind = 'REPLACE_STORAGE'
            return context.window_manager.invoke_props_dialog(self, width=520)

        if self._slot_with_current_identity_exists(params):
            behavior = izom_propui_free_confirmation_value(
                params,
                'izom_propui_free_confirmation_generate_current_conflict',
                default='ASK',
            )
            if behavior == 'OVERWRITE':
                self.current_conflict_action = behavior
                if needs_native_conflict_prompt:
                    self.native_conflicts_confirmed = True
                    self.popup_kind = 'NATIVE_CONFLICT'
                    return context.window_manager.invoke_props_dialog(self, width=520)
                return self.execute(context)
            self.native_conflicts_confirmed = needs_native_conflict_prompt
            self.popup_kind = 'CURRENT_AND_NATIVE_CONFLICT' if needs_native_conflict_prompt else 'CURRENT_CONFLICT'
            return context.window_manager.invoke_props_dialog(self, width=520 if needs_native_conflict_prompt else 430)
        if needs_native_conflict_prompt:
            self.native_conflicts_confirmed = True
            self.popup_kind = 'NATIVE_CONFLICT'
            return context.window_manager.invoke_props_dialog(self, width=520)
        return self.execute(context)

    def draw(self, _context):
        layout = self.layout
        kind = str(getattr(self, 'popup_kind', 'NONE') or 'NONE').strip().upper() or 'NONE'
        if kind == 'REPLACE_STORAGE':
            layout.label(text='Replace all custom properties on Property Storage?', icon='ERROR')
            layout.label(text='Unrelated custom properties will also be removed.')
            layout.label(text='Generate will then rebuild the managed properties and panel.')
            return
        if kind == 'EMPTY_LAYOUT':
            layout.label(text="Generated Layout is empty.", icon='QUESTION')
            layout.label(text="Generate needs at least one row in the Generated Layout.")
            layout.prop(self, "empty_layout_action", expand=True)
            return
        if kind in {'NATIVE_CONFLICT', 'EMPTY_LAYOUT_AND_NATIVE_CONFLICT', 'CURRENT_AND_NATIVE_CONFLICT'}:
            if kind == 'EMPTY_LAYOUT_AND_NATIVE_CONFLICT':
                layout.label(text="Generated Layout is empty.", icon='QUESTION')
                layout.label(text="Generate needs at least one row in the Generated Layout.")
                layout.prop(self, "empty_layout_action", expand=True)
                layout.separator()
            elif kind == 'CURRENT_AND_NATIVE_CONFLICT':
                layout.label(text="A generated panel already exists in this destination.", icon='QUESTION')
                layout.label(text="Generate will replace it.")
                layout.separator()
            layout.label(text="Some managed Property IDs already exist as custom properties on the target.", icon='QUESTION')
            summary = str(getattr(self, 'native_conflict_summary', '') or '').strip()
            if summary:
                layout.label(text=summary)
            layout.label(text="Choose what to do with only the conflicting properties.")
            layout.prop(self, "native_conflict_action", expand=True)
            return
        layout.label(text="A generated panel already exists in this destination.", icon='QUESTION')
        layout.label(text="Generate will replace it.")

    def _build_slot_from_current_settings(self, params, *, slot_uid=''):
        phase_start = time.perf_counter()
        _izom_propui_free_ensure_generate_consistency(params)
        _izom_propui_free_generate_timing_mark(self, 'apply/sync: consistency gate', phase_start)
        default_owner_path = str(getattr(params, 'izom_propui_free_default_target_owner_path', '') or '').strip()
        if izom_propui_free_resolve_owner_path(default_owner_path) is None:
            self.report({'ERROR'}, "Set a valid Property Storage target before generating UI")
            return None, None, None

        replace_storage_mode = 'REPLACE' if bool(getattr(params, 'izom_propui_free_replace_storage_on_generate', False)) else 'PRESERVE'
        phase_start = time.perf_counter()
        apply_result = izom_propui_free_apply_target_props_internal(
            self,
            params,
            replace_storage_mode=replace_storage_mode,
            clean_old_targets_mode='CLEAN' if bool(getattr(params, 'izom_propui_free_clean_old_targets_on_generate', True)) else 'KEEP',
            native_conflict_action=getattr(self, 'native_conflict_action', 'OVERWRITE'),
            native_conflicts_confirmed=bool(getattr(self, 'native_conflicts_confirmed', False)),
            skip_consistency=True,
        )
        if 'CANCELLED' in apply_result:
            return None, None, None
        _izom_propui_free_generate_timing_mark(self, 'apply/sync: managed properties', phase_start)

        tab = str(getattr(params, 'izom_propui_free_generated_panel_tab', '') or '').strip() or IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TAB
        title = (
            str(getattr(params, 'izom_propui_free_generated_panel_title', '') or '').strip()
            or IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TITLE
        )
        target_path = str(getattr(params, 'izom_propui_free_default_target_owner_path', '') or '').strip()
        scene_name = str(getattr(getattr(params, 'id_data', None), 'name', '') or '').strip()
        branding = izom_propui_free_generated_branding_from_params(params)
        resolved_branding = izom_propui_free_resolve_generated_branding(branding)
        phase_start = time.perf_counter()
        runtime_layout_entries = list(izom_propui_free_runtime_layout_entries(params))
        generated_entries, owner_paths = _izom_propui_free_prepare_generated_entries(
            params,
            runtime_layout_entries=runtime_layout_entries,
        )
        generated_control_keys = {}
        _izom_propui_free_generate_timing_mark(self, 'runtime snapshot/layout', phase_start)
        phase_start = time.perf_counter()
        try:
            source, owner_paths = izom_propui_free_build_generated_draw_source(
                params,
                generated_control_keys=generated_control_keys,
                entries=generated_entries,
                owner_paths=owner_paths,
                branding=resolved_branding,
            )
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            self.report({'ERROR'}, f"Could not generate PropUI panel: {exc}")
            return None, None, None
        _izom_propui_free_generate_timing_mark(self, 'source assembly', phase_start)

        new_slot = {
            'uid': str(slot_uid or '').strip() or _izom_propui_free_new_generated_slot_uid(),
            'scene_name': scene_name,
            'script_name': '',
            'tab': tab,
            'title': title,
            'target_path': target_path,
            'source': source,
            'branding': branding,
            'owner_paths': list(owner_paths or []),
        }
        return new_slot, source, owner_paths

    def _upsert_generated_slot(self, params, new_slot, *, allow_replace=True):
        slot_uid = str((new_slot or {}).get('uid', '') or '').strip()
        slots = list(_izom_propui_free_generated_slots_from_params(params))
        replacement_index = -1
        if allow_replace:
            # Storage can change without leaving another panel in the same
            # visible destination. Keep its existing slot and script identity.
            # Same title in another sidebar tab should stay a separate output.
            for index, slot in enumerate(slots):
                if _izom_propui_free_generated_slots_match_current_identity(slot, new_slot):
                    replacement_index = index
                    break
        if replacement_index >= 0:
            prior = slots[replacement_index]
            new_slot['uid'] = str(prior.get('uid', '') or '').strip() or slot_uid or _izom_propui_free_new_generated_slot_uid()
            if not str(new_slot.get('script_name', '') or '').strip():
                prior_script_name = str(prior.get('script_name', '') or '').strip()
                if prior_script_name:
                    new_slot['script_name'] = prior_script_name
            slots[replacement_index] = new_slot
            return slots, replacement_index
        slots.append(new_slot)
        return slots, len(slots) - 1

    def _store_generated_slot(self, params, new_slot, *, allow_replace=True):
        next_slots, slot_index = self._upsert_generated_slot(params, new_slot, allow_replace=allow_replace)
        _izom_propui_free_store_generated_slots(params, next_slots, write_scripts=False)
        return slot_index

    def _generate_current_editor_state(self, params):
        with IzomPropUIFreeGenerationTransaction(params) as transaction:
            result = self._generate_current_editor_state_unchecked(params)
            transaction.committed = result is not None
            return result

    def _generate_current_editor_state_unchecked(self, params):
        new_slot, source, owner_paths = self._build_slot_from_current_settings(
            params,
        )
        if new_slot is None:
            return None
        compile(source, '<PropUI generated draw>', 'exec')
        # Free keeps one saved panel per generated destination.
        phase_start = time.perf_counter()
        slot_index = self._store_generated_slot(params, new_slot, allow_replace=True)
        _izom_propui_free_generate_timing_mark(self, 'Text datablock write/slot storage', phase_start)
        return source, owner_paths, slot_index

    def execute(self, context):
        total_start = time.perf_counter()
        _izom_propui_free_generate_timing_reset(self)
        params = izom_propui_free_context_params(context)
        if params is None:
            return {'CANCELLED'}
        if params.izom_propui_free_replace_storage_on_generate and not self.replace_storage_confirmed:
            self.report({'WARNING'}, 'Confirm Replace Storage through Generate UI before removing custom properties')
            return {'CANCELLED'}
        editor_state = _izom_propui_free_capture_generate_editor_state(params)
        try:
            # If invoke() routed through the empty-layout popup, honour that action
            # the user just made rather than running the normal generate flow.
            popup_kind = str(getattr(self, 'popup_kind', 'NONE') or 'NONE').strip().upper()
            if popup_kind in {'EMPTY_LAYOUT', 'EMPTY_LAYOUT_AND_NATIVE_CONFLICT'}:
                self.report({'INFO'}, "Skipped Generate (no entries in Generated Layout)")
                return {'CANCELLED'}

            if self._current_editor_has_empty_layout(params):
                self.report({'INFO'}, "Skipped Generate (no entries in Generated Layout)")
                return {'CANCELLED'}

            try:
                result = self._generate_current_editor_state(
                    params,
                )
            except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                self.report({'ERROR'}, f'Could not generate PropUI panel: {exc}')
                return {'CANCELLED'}
            if result is None:
                return {'CANCELLED'}
            phase_start = time.perf_counter()
            registered = restore_generated_panel_from_scenes()
            _izom_propui_free_generate_timing_mark(self, 'compile/register/lifecycle', phase_start)
            if not registered:
                self.report({'WARNING'}, "Generated UI data was saved, but no generated panel could be registered")
                return {'FINISHED'}
            self.report({'INFO'}, "Generated PropUI output")
            return {'FINISHED'}
        finally:
            _izom_propui_free_restore_generate_editor_state(params, editor_state)
            _izom_propui_free_generate_timing_log(self, total_start)


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

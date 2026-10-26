# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from ..core.diagnostics import izom_propui_free_log_recovered
import bpy
from bpy.props import BoolProperty, StringProperty
from bpy.types import Operator
from ..core.context import izom_propui_free_context_params

from ..bpy_support import (
    _izom_propui_free_clear_custom_prop_ui_data,
    izom_propui_free_managed_prop_ids,
)
from ..core.cache import izom_propui_free_invalidate_params_cache
from ..core.editor_state_schema import IZOM_PROPUI_FREE_EDITOR_EXPANDED_PROPERTY_SPECS
from ..core.constants_display import (
    IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TAB,
    IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TITLE,
)
from ..core.targets import (
    izom_propui_free_apply_owner_picker_from_path,
    izom_propui_free_resolve_owner_path,
)
from .confirmations import (
    izom_propui_free_confirm_or_execute,
    izom_propui_free_confirmation_value,
)


_IZOM_PROPUI_FREE_EDITOR_EXPANDED_FIELDS = frozenset(
    field_name for field_name, _label, _description in IZOM_PROPUI_FREE_EDITOR_EXPANDED_PROPERTY_SPECS
)


class IZOM_PROPUI_FREE_OT_toggle_editor_expanded(Operator):
    bl_idname = "wm.izom_propui_free_toggle_editor_expanded"
    bl_label = "Toggle Editor Section"
    bl_description = "Expand or collapse an editor-only section without adding an undo-history step"
    bl_options = {'INTERNAL'}

    property_name: StringProperty(name="Expanded Property", default="", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return izom_propui_free_context_params(context) is not None

    def execute(self, context):
        params = izom_propui_free_context_params(context)
        property_name = str(getattr(self, 'property_name', '') or '').strip()
        if (
            params is None
            or property_name not in _IZOM_PROPUI_FREE_EDITOR_EXPANDED_FIELDS
            or not hasattr(params, property_name)
        ):
            return {'CANCELLED'}
        setattr(params, property_name, not bool(getattr(params, property_name)))
        area = getattr(context, 'area', None)
        if area is not None:
            area.tag_redraw()
        return {'FINISHED'}


def _izom_propui_free_clear_editor_collections(params):
    while params.izom_propui_free_entries:
        params.izom_propui_free_entries.remove(len(params.izom_propui_free_entries) - 1)
    from .editor_session import izom_propui_free_invalidate_editor_session_bindings

    izom_propui_free_invalidate_editor_session_bindings()
    while getattr(params, 'izom_propui_free_layout_rows', None):
        params.izom_propui_free_layout_rows.remove(len(params.izom_propui_free_layout_rows) - 1)
    while getattr(params, 'izom_propui_free_layout_items', None):
        params.izom_propui_free_layout_items.remove(len(params.izom_propui_free_layout_items) - 1)
    while getattr(params, 'izom_propui_free_layout_view_items', None):
        params.izom_propui_free_layout_view_items.remove(len(params.izom_propui_free_layout_view_items) - 1)


def _izom_propui_free_reset_editor_state(params, *, include_collapsed_state=True):
    _izom_propui_free_clear_editor_collections(params)

    params.izom_propui_free_active_index = 0
    if hasattr(params, 'izom_propui_free_layout_active_index'):
        params.izom_propui_free_layout_active_index = 0
    if hasattr(params, 'izom_propui_free_layout_view_active_index'):
        params.izom_propui_free_layout_view_active_index = 0

    params.izom_propui_free_active_uid = ""
    if hasattr(params, 'izom_propui_free_layout_active_uid'):
        params.izom_propui_free_layout_active_uid = ""
    if hasattr(params, 'izom_propui_free_layout_view_active_uid'):
        params.izom_propui_free_layout_view_active_uid = ""

    params.izom_propui_free_selected_uids_json = "[]"
    params.izom_propui_free_selection_anchor_uid = ""
    if hasattr(params, 'izom_propui_free_layout_selected_uids_json'):
        params.izom_propui_free_layout_selected_uids_json = "[]"
    if hasattr(params, 'izom_propui_free_layout_view_selected_uids_json'):
        params.izom_propui_free_layout_view_selected_uids_json = "[]"
    if hasattr(params, 'izom_propui_free_layout_selection_anchor_uid'):
        params.izom_propui_free_layout_selection_anchor_uid = ""
    if hasattr(params, 'izom_propui_free_layout_view_selection_anchor_uid'):
        params.izom_propui_free_layout_view_selection_anchor_uid = ""

    if include_collapsed_state:
        if hasattr(params, 'izom_propui_free_entry_collapsed_uids_json'):
            params.izom_propui_free_entry_collapsed_uids_json = "[]"
        if hasattr(params, 'izom_propui_free_layout_collapsed_row_uids_json'):
            params.izom_propui_free_layout_collapsed_row_uids_json = "[]"

    izom_propui_free_invalidate_params_cache(params)


def _izom_propui_free_clear_saved_defaults():
    return []


_IZOM_PROPUI_FREE_FULL_RESET_FIELD_DEFAULTS = {
    'izom_propui_free_generated_panel_tab': IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TAB,
    'izom_propui_free_generated_panel_title': IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TITLE,
    'izom_propui_free_default_target_owner_path': '',
    'izom_propui_free_default_target_object': None,
    'izom_propui_free_generated_panels_json': '[]',
    'izom_propui_free_last_synced_prop_ids_json': "{}",
    'izom_propui_free_smart_expanded_active_uid': "",
}


def _izom_propui_free_apply_field_defaults(params, defaults):
    for attr, default in (defaults or {}).items():
        if not hasattr(params, attr):
            continue
        try:
            setattr(params, attr, default)
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
                hint=f'resetting {attr}',
            )


def _izom_propui_free_apply_current_setup_defaults(params):
    _izom_propui_free_apply_field_defaults(params, _IZOM_PROPUI_FREE_FULL_RESET_FIELD_DEFAULTS)


def _izom_propui_free_apply_factory_editor_defaults(params):
    _izom_propui_free_apply_field_defaults(params, _IZOM_PROPUI_FREE_FULL_RESET_FIELD_DEFAULTS)


def _izom_propui_free_remove_managed_props_from_owners(params, managed_ids):
    removed = 0
    seen_keys = set()
    owners = []
    for owner_path in (str(getattr(params, 'izom_propui_free_default_target_owner_path', '') or '').strip(),):
        owner = izom_propui_free_resolve_owner_path(owner_path)
        if owner is None:
            continue
        try:
            owner_key = int(owner.as_pointer())
        except (AttributeError, TypeError, ValueError):
            owner_key = id(owner)
        if owner_key in seen_keys:
            continue
        seen_keys.add(owner_key)
        owners.append(owner)

    for owner in owners:
        for prop_id in managed_ids:
            _izom_propui_free_clear_custom_prop_ui_data(owner, prop_id)
            try:
                if prop_id in owner:
                    del owner[prop_id]
                    removed += 1
            except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                    hint='deleting managed custom property',
                )
    return removed


def _izom_propui_free_reset_setup_params(params):
    if params is None:
        return 0

    managed_ids = {str(prop_id).strip() for prop_id in izom_propui_free_managed_prop_ids(params) if str(prop_id).strip()}
    removed_props = _izom_propui_free_remove_managed_props_from_owners(params, managed_ids)

    _izom_propui_free_reset_editor_state(params, include_collapsed_state=True)
    _izom_propui_free_apply_current_setup_defaults(params)
    izom_propui_free_apply_owner_picker_from_path(params, 'izom_propui_free_default_target', '')
    return removed_props


def _izom_propui_free_removed_props_suffix(removed_props):
    return f" and cleaned {removed_props} managed prop{'s' if removed_props != 1 else ''}" if removed_props else ""


class IZOM_PROPUI_FREE_OT_remove_all_entries(Operator):
    bl_idname = "wm.izom_propui_free_remove_all_entries"
    bl_label = "Clear Entry List"
    bl_description = "Clear every entry from this izom PropUI project"
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        params = izom_propui_free_context_params(context)
        return bool(params and len(params.izom_propui_free_entries) > 0)

    def invoke(self, context, event):
        return izom_propui_free_confirm_or_execute(
            self, context, event, prop_name='izom_propui_free_confirmation_clear_entry_list'
        )

    def execute(self, context):
        params = izom_propui_free_context_params(context)
        _izom_propui_free_reset_editor_state(params, include_collapsed_state=False)
        self.report({'INFO'}, "Cleared izom PropUI Entry List")
        return {'FINISHED'}


class IZOM_PROPUI_FREE_OT_full_factory_reset(Operator):
    bl_idname = "wm.izom_propui_free_full_factory_reset"
    bl_label = "Full Factory Reset"
    bl_description = "Wipe PropUI editor data from every scene in this blend file and delete all saved defaults"
    bl_options = {'UNDO', 'INTERNAL'}

    confirm_full_factory_reset: BoolProperty(
        name="I understand this wipes PropUI editor data in this blend and all saved defaults",
        description="Required confirmation for full izom PropUI factory reset",
        default=False,
    )

    @classmethod
    def poll(cls, context):
        return izom_propui_free_context_params(context) is not None

    def invoke(self, context, event):
        behavior = izom_propui_free_confirmation_value(
            izom_propui_free_context_params(context),
            'izom_propui_free_confirmation_full_factory_reset',
            default='ASK',
        )
        if behavior == 'CONFIRM':
            self.confirm_full_factory_reset = True
            return self.execute(context)
        if behavior == 'CANCEL':
            self.report({'INFO'}, "Skipped Full Factory Reset")
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self, width=520)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False
        warning = layout.column(align=True)
        warning.alert = True
        warning.label(text="Full factory reset wipes PropUI editor data from every scene.", icon='ERROR')
        warning.label(text="This removes current free-edition setups and generated panel data.")
        layout.prop(self, "confirm_full_factory_reset")

    def execute(self, context):
        if not bool(getattr(self, 'confirm_full_factory_reset', False)):
            self.report({'WARNING'}, "Confirm the full factory reset first")
            return {'CANCELLED'}
        try:
            cleared = _izom_propui_free_clear_saved_defaults()
        except ValueError as exc:
            self.report({'WARNING'}, str(exc))
            return {'CANCELLED'}
        from .generated_registry_unregister import izom_propui_free_unregister_all_running_generated_uis
        from .generated_slots_storage import _izom_propui_free_clear_generated_slots

        scene_count = 0
        removed_props = 0
        for scene in getattr(bpy.data, 'scenes', []) or []:
            params = getattr(scene, 'izom_propui_free', None)
            if params is None:
                continue
            scene_count += 1
            removed_props += _izom_propui_free_reset_setup_params(params)
            _izom_propui_free_clear_generated_slots(params)
            _izom_propui_free_apply_factory_editor_defaults(params)
            _izom_propui_free_apply_field_defaults(params, _IZOM_PROPUI_FREE_FULL_RESET_FIELD_DEFAULTS)
        izom_propui_free_unregister_all_running_generated_uis()
        if getattr(context, 'area', None) is not None:
            context.area.tag_redraw()
        self.report(
            {'INFO'},
            f"Fully factory reset izom PropUI across {scene_count} scene{'s' if scene_count != 1 else ''}"
            f"{_izom_propui_free_removed_props_suffix(removed_props)}",
        )
        return {'FINISHED'}


CLASSES = (
    IZOM_PROPUI_FREE_OT_toggle_editor_expanded,
    IZOM_PROPUI_FREE_OT_remove_all_entries,
    IZOM_PROPUI_FREE_OT_full_factory_reset,
)

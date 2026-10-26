# SPDX-License-Identifier: GPL-3.0-or-later

from .operators_value_labels_common import (
    IZOM_PROPUI_FREE_VALUE_LABEL_TARGET_MODE_ITEMS_WITH_DESCRIPTIONS,
    _izom_propui_free_assign_exact_match_defaults,
    _izom_propui_free_assign_self_component_defaults,
    _izom_propui_free_entry_component_rule_info,
    _izom_propui_free_finalize_value_label_thresholds,
    _izom_propui_free_finish_value_label_collection_mutation,
    _izom_propui_free_focus_value_label_editor,
    _izom_propui_free_new_uid,
    _izom_propui_free_selected_value_label_indexes_direct,
    _izom_propui_free_selected_value_label_uids,
    _izom_propui_free_value_label_collection_name,
    _izom_propui_free_value_label_operator_entry,
    _izom_propui_free_value_label_target_info,
    _izom_propui_free_value_label_target_mode_label,
    izom_propui_free_context_params,
    izom_propui_free_log_recovered,
)
from bpy.props import (
    EnumProperty,
    StringProperty,
)
from bpy.types import Operator
from types import SimpleNamespace
from ..core.cache_value_labels import izom_propui_free_remember_value_label_owner
from ..core.value_access_common import izom_propui_free_is_numeric_value_kind
from .helper_cache_updates_session import (
    _izom_propui_free_resume_value_label_update_callbacks,
    _izom_propui_free_suspend_value_label_update_callbacks,
)



_IZOM_PROPUI_FREE_VALUE_LABEL_ADD_RNA_ERRORS = (
    AttributeError,
    TypeError,
    ValueError,
    RuntimeError,
    ReferenceError,
)

class IZOM_PROPUI_FREE_OT_add_value_label(Operator):
    bl_idname = "wm.izom_propui_free_add_value_label"
    bl_label = "Add Dynamic Label"
    bl_description = "Add a new dynamic-label row for the active entry"
    bl_options = {'UNDO', 'INTERNAL'}

    target_mode: EnumProperty(
        name="Target Mode",
        items=IZOM_PROPUI_FREE_VALUE_LABEL_TARGET_MODE_ITEMS_WITH_DESCRIPTIONS,
        default='SELF',
        options={'HIDDEN'},
    )
    entry_uid: StringProperty(default="", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        params = izom_propui_free_context_params(context)
        return bool(params is not None and len(getattr(params, 'izom_propui_free_entries', []) or []) > 0)

    @classmethod
    def description(cls, _context, properties):
        return f"Add a new row to {_izom_propui_free_value_label_target_mode_label(getattr(properties, 'target_mode', 'SELF'))}"

    def execute(self, context):
        ctx = self._value_label_add_context(context)
        if ctx is None:
            return {'CANCELLED'}

        self._create_value_label_item(ctx)
        return self._configure_self_value_label(ctx)

    def _value_label_add_context(self, context):
        entry = _izom_propui_free_value_label_operator_entry(context, getattr(self, 'entry_uid', ''))
        info = _izom_propui_free_value_label_target_info(entry, context, self.target_mode)
        if not info:
            return None

        params = _izom_propui_free_focus_value_label_editor(info, self.target_mode)
        collection = info['collection']
        active_owner = info.get('active_owner', entry)
        collection_name = _izom_propui_free_value_label_collection_name(self.target_mode)
        selected_uids = _izom_propui_free_selected_value_label_uids(active_owner, collection_name)
        selected_indexes = _izom_propui_free_selected_value_label_indexes_direct(
            active_owner,
            collection_name,
            collection,
            selected_uids,
        )
        active_index = self._active_value_label_index(active_owner, collection_name, collection)
        basis_index = max(selected_indexes) if selected_indexes else (active_index if len(collection) > 0 else -1)
        insert_index = basis_index + 1 if basis_index >= 0 else len(collection)
        return SimpleNamespace(
            context=context,
            entry=entry,
            info=info,
            params=params,
            collection=collection,
            active_owner=active_owner,
            collection_name=collection_name,
            insert_index=insert_index,
            item=None,
            new_uid='',
        )

    def _active_value_label_index(self, active_owner, collection_name, collection):
        try:
            return max(
                0,
                min(
                    int(getattr(active_owner, f"{collection_name}_active_index", 0) or 0),
                    max(0, len(collection) - 1),
                ),
            )
        except _IZOM_PROPUI_FREE_VALUE_LABEL_ADD_RNA_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            return max(0, len(collection) - 1)

    def _create_value_label_item(self, ctx):
        item = ctx.collection.add()
        ctx.new_uid = _izom_propui_free_new_uid()
        item.uid = ctx.new_uid
        if ctx.insert_index < len(ctx.collection) - 1:
            ctx.collection.move(len(ctx.collection) - 1, ctx.insert_index)
            try:
                item = ctx.collection[ctx.insert_index]
            except _IZOM_PROPUI_FREE_VALUE_LABEL_ADD_RNA_ERRORS as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )
        ctx.item = item
        izom_propui_free_remember_value_label_owner(
            ctx.params,
            item,
            ctx.entry,
            ctx.active_owner,
            ctx.collection_name,
            ctx.insert_index,
        )
        _izom_propui_free_suspend_value_label_update_callbacks()
        try:
            item.label = ""
        finally:
            _izom_propui_free_resume_value_label_update_callbacks()

    def _configure_self_value_label(self, ctx):
        prop_type = ctx.info['source_type']
        reference_entry = ctx.info.get('source_entry') or ctx.entry
        self._assign_self_basis_defaults(ctx, reference_entry)
        component_info = _izom_propui_free_entry_component_rule_info(
            ctx.entry,
            ctx.item,
            reference_entry=reference_entry,
        )
        effective_prop_type = (
            str(component_info['component_meta'].get('component_kind', prop_type) or prop_type)
            if component_info.get('use_component') else prop_type
        )
        if not izom_propui_free_is_numeric_value_kind(effective_prop_type):
            return self._configure_exact_value_label(
                ctx,
                prop_type,
                field_root='target_value',
                reference_entry=reference_entry,
            )

        return self._finish_value_label_collection_mutation(ctx)

    def _assign_self_basis_defaults(self, ctx, reference_entry):
        _izom_propui_free_suspend_value_label_update_callbacks()
        try:
            _izom_propui_free_assign_self_component_defaults(
                ctx.item,
                ctx.entry,
                reference_entry=reference_entry,
            )
        finally:
            _izom_propui_free_resume_value_label_update_callbacks()

    def _configure_exact_value_label(self, ctx, source_type, *, field_root, reference_entry):
        _izom_propui_free_suspend_value_label_update_callbacks()
        try:
            _izom_propui_free_assign_exact_match_defaults(
                ctx.item,
                source_type,
                field_root=field_root,
                reference_entry=reference_entry,
                params=ctx.params,
            )
        finally:
            _izom_propui_free_resume_value_label_update_callbacks()
        return self._finish_value_label_collection_mutation(ctx)

    def _finish_value_label_collection_mutation(self, ctx):
        _izom_propui_free_finalize_value_label_thresholds(
            ctx.collection,
            ctx.entry,
            ctx.active_owner,
            ctx.collection_name,
            ctx.info,
        )
        _izom_propui_free_finish_value_label_collection_mutation(
            ctx.active_owner,
            ctx.collection_name,
            ctx.collection,
            ctx.new_uid,
            ctx.insert_index,
            params=ctx.params,
        )
        return {'FINISHED'}


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

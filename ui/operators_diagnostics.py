# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
import bpy
from bpy.types import Operator
from bpy.props import StringProperty
import textwrap

from ..core.diagnostics import izom_propui_free_clear_diagnostics, izom_propui_free_log_info
from .generated_registry_lifecycle import izom_propui_free_generated_lifecycle_status
from .generated_registry_text import _izom_propui_free_is_portable_generated_text
from .generated_slots_storage import _izom_propui_free_generated_slots_from_params

def _izom_propui_free_text_names_matching(predicate):
    try:
        texts = list(bpy.data.texts)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_info(
            "Could not inspect Text datablocks for blend data audit",
            category='Blend Data Audit',
            exception=exc,
        )
        return []
    names = []
    for text in texts:
        name = str(getattr(text, 'name', '') or '').strip()
        try:
            if predicate(text, name):
                names.append(name)
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_info(
                f"Skipped Text datablock {name or 'Text'} during blend data audit",
                category='Blend Data Audit',
                exception=exc,
            )
    return sorted(names)

def izom_propui_free_build_blend_data_audit(context=None):
    try:
        scenes = list(bpy.data.scenes)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_info(
            "Could not inspect scenes for blend data audit",
            category='Blend Data Audit',
            exception=exc,
        )
        scenes = []

    scene_rows = []
    entry_count = 0
    saved_slot_count = 0
    for scene in scenes:
        params = getattr(scene, 'izom_propui_free', None)
        if params is None:
            continue
        entries = getattr(params, 'izom_propui_free_entries', None) or []
        slots = _izom_propui_free_generated_slots_from_params(params)
        row = {
            'scene_name': str(getattr(scene, 'name', '') or 'Scene'),
            'entries': len(entries),
            'saved_generated_slots': len(slots),
        }
        scene_rows.append(row)
        entry_count += row['entries']
        saved_slot_count += row['saved_generated_slots']

    generated_text_names = _izom_propui_free_text_names_matching(
        lambda text, _name: _izom_propui_free_is_portable_generated_text(text)
    )
    generated_status = izom_propui_free_generated_lifecycle_status(deep=True, refresh=True)
    active_scene = getattr(context, 'scene', None) if context is not None else None
    return {
        'active_scene': str(getattr(active_scene, 'name', '') or ''),
        'scene_count': len(scenes),
        'propui_scene_count': len(scene_rows),
        'scene_rows': scene_rows,
        'entry_count': entry_count,
        'saved_slot_count': saved_slot_count,
        'generated_text_count': len(generated_text_names),
        'generated_text_names': generated_text_names,
        'generated_lifecycle': generated_status,
    }

def _izom_propui_free_join_preview(names, *, limit=3):
    visible = [str(name or '').strip() for name in names or [] if str(name or '').strip()]
    if not visible:
        return 'None'
    suffix = f", +{len(visible) - limit} more" if len(visible) > limit else ''
    return ', '.join(visible[:limit]) + suffix

class IZOM_PROPUI_FREE_OT_diagnostic_details(Operator):
    bl_idname = "wm.izom_propui_free_diagnostic_details"
    bl_label = "Diagnostic Details"
    bl_description = "Inspect the complete diagnostic; confirm to copy its displayed details"
    bl_options = {'INTERNAL'}

    text: StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})

    def invoke(self, context, _event):
        if not self.text:
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self, width=760)

    def draw(self, _context):
        self.layout.label(text='Confirm to copy these details to the clipboard.', icon='COPYDOWN')
        for paragraph in self.text.splitlines():
            for line in textwrap.wrap(paragraph, width=108, replace_whitespace=False) or ['']:
                self.layout.label(text=line)

    def execute(self, context):
        context.window_manager.clipboard = self.text
        self.report({'INFO'}, 'Copied diagnostic details')
        return {'FINISHED'}


class IZOM_PROPUI_FREE_OT_clear_diagnostics(Operator):
    bl_idname = "wm.izom_propui_free_clear_diagnostics"
    bl_label = "Clear PropUI Warnings"
    bl_description = "Clear the internal izom PropUI warning and error history"
    bl_options = {'INTERNAL'}

    def execute(self, _context):
        count = izom_propui_free_clear_diagnostics()
        self.report({'INFO'}, f"Cleared {count} PropUI diagnostic{'s' if count != 1 else ''}")
        return {'FINISHED'}

class IZOM_PROPUI_FREE_OT_audit_blend_data(Operator):
    bl_idname = "wm.izom_propui_free_audit_blend_data"
    bl_label = "Audit Blend Data"
    bl_description = "Show the izom PropUI data currently stored in this blend file"
    bl_options = {'INTERNAL'}

    def _audit(self, context):
        audit = getattr(self, '_izom_propui_free_audit', None)
        if audit is None:
            audit = izom_propui_free_build_blend_data_audit(context)
            self._izom_propui_free_audit = audit
        return audit

    def invoke(self, context, _event):
        self._izom_propui_free_audit = izom_propui_free_build_blend_data_audit(context)
        return context.window_manager.invoke_props_dialog(self, width=520)

    def draw(self, context):
        audit = self._audit(context)
        layout = self.layout
        col = layout.column(align=True)
        col.label(text=f"Scenes with PropUI runtime settings: {audit.get('propui_scene_count', 0)}")
        col.label(text=f"Editor entries: {audit.get('entry_count', 0)}")
        col.label(text=f"Saved generated UI slots: {audit.get('saved_slot_count', 0)}")
        col.separator(factor=0.5)
        col.label(text=f"Generated .py Text scripts: {audit.get('generated_text_count', 0)}", icon='TEXT')
        col.label(text=_izom_propui_free_join_preview(audit.get('generated_text_names', [])))
        generated = audit.get('generated_lifecycle', {}) or {}
        col.separator(factor=0.5)
        running_panel_count = generated.get(
            'registered_panel_class_count',
            generated.get('running_class_count', 0),
        )
        col.label(text=f"Running generated panels: {running_panel_count}", icon='PLAY')
        stale = int(generated.get('stale_running_count', generated.get('stale_registry_count', 0)) or 0)
        stale_row = col.row(align=True)
        stale_row.alert = stale > 0
        stale_row.label(text=f"Stale running generated UIs: {stale}", icon='ERROR' if stale else 'CHECKMARK')
        missing = int(generated.get('missing_text_count', 0) or 0)
        missing_row = col.row(align=True)
        missing_row.alert = missing > 0
        missing_row.label(text=f"Missing generated Text scripts: {missing}", icon='ERROR' if missing else 'CHECKMARK')

    def execute(self, context):
        audit = izom_propui_free_build_blend_data_audit(context)
        self._izom_propui_free_audit = audit
        generated = audit.get('generated_lifecycle', {}) or {}
        running_panel_count = generated.get(
            'registered_panel_class_count',
            generated.get('running_class_count', 0),
        )
        summary = (
            f"PropUI blend data: {audit.get('generated_text_count', 0)} generated script Text, "
            f"{audit.get('saved_slot_count', 0)} saved generated slot, "
            f"{running_panel_count} running panel"
        )
        izom_propui_free_log_info(summary, category='Blend Data Audit')
        self.report({'INFO'}, summary)
        return {'FINISHED'}


CLASSES = (
    IZOM_PROPUI_FREE_OT_diagnostic_details,
    IZOM_PROPUI_FREE_OT_clear_diagnostics,
    IZOM_PROPUI_FREE_OT_audit_blend_data,
)

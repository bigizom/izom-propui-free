# SPDX-License-Identifier: GPL-3.0-or-later

"""Setup JSON transfer for PropUI Free, including Full and Rigify imports."""

from ..core.atomic_files import izom_propui_free_atomic_write_text
import json
import textwrap

from bpy.props import BoolProperty, StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper, ImportHelper

from ..core.context import izom_propui_free_context_params
from ..core.setup_compat import (
    izom_propui_free_make_setup_document,
    izom_propui_free_parse_compatible_setup_document,
)
from ..core.snapshot_entries_runtime import izom_propui_free_snapshot_entries
from ..core.snapshot_entries_restore import izom_propui_free_restore_entries
from ..core.snapshot_layout_common import (
    izom_propui_free_snapshot_layout_items,
    izom_propui_free_snapshot_layout_rows,
)
from ..core.targets import izom_propui_free_apply_owner_picker_from_path
from .operators_layout_restore_snapshots import _izom_propui_free_restore_layout_snapshots


_IZOM_PROPUI_FREE_SETUP_SETTING_FIELDS = (
    'izom_propui_free_generated_panel_tab',
    'izom_propui_free_generated_panel_title',
    'izom_propui_free_default_target_owner_path',
    'izom_propui_free_replace_storage_on_generate',
    'izom_propui_free_clean_old_targets_on_generate',
)


def _izom_propui_free_capture_setup_document(params):
    settings = {
        field_name: getattr(params, field_name)
        for field_name in _IZOM_PROPUI_FREE_SETUP_SETTING_FIELDS
        if hasattr(params, field_name)
    }
    return izom_propui_free_make_setup_document(
        project_settings=settings,
        entries=izom_propui_free_snapshot_entries(params),
        layout_rows=izom_propui_free_snapshot_layout_rows(params),
        layout_items=izom_propui_free_snapshot_layout_items(params),
    )


def _izom_propui_free_target_armature(params, context):
    target = getattr(params, 'izom_propui_free_default_target_object', None)
    if target is None:
        target = getattr(context, 'active_object', None)
    if str(getattr(target, 'type', '') or '').strip().upper() != 'ARMATURE':
        return None
    return target


def _izom_propui_free_import_message(report):
    source = str(report.get('source_edition', 'FULL') or 'FULL').strip().upper().title()
    message = (
        f"Imported {source} setup: {int(report.get('imported_entries', 0) or 0)} entries and "
        f"{int(report.get('imported_layout_items', 0) or 0)} Generated Layout items"
    )
    notes = []
    skipped_types = report.get('skipped_entry_types', {})
    if isinstance(skipped_types, dict) and skipped_types:
        summary = ', '.join(
            f'{name} x{count}'
            for name, count in sorted(skipped_types.items())
        )
        notes.append(f'skipped unsupported entry types ({summary})')
    flattened = int(report.get('flattened_subpanels', 0) or 0)
    if flattened:
        notes.append(f'flattened {flattened} subpanel container(s) into ordered rows')
    skipped_boxes = int(report.get('skipped_row_boxes', 0) or 0)
    if skipped_boxes:
        notes.append(f'skipped {skipped_boxes} row box(es)')
    skipped_storage = int(report.get('skipped_storage_targets', 0) or 0)
    if skipped_storage:
        notes.append(f'skipped {skipped_storage} per-entry or unavailable storage target(s)')
    skipped_visibility = int(report.get('skipped_visibility_targets', 0) or 0)
    if skipped_visibility:
        notes.append(f'skipped {skipped_visibility} visibility target(s)')
    mapped_storage = int(report.get('mapped_storage_bones', 0) or 0)
    if mapped_storage:
        if str(report.get('source_edition', '') or '').strip().upper() == 'RIGIFY':
            notes.append('adapted shared Rigify bone storage to the receiving armature Object')
        else:
            notes.append(f'adapted {mapped_storage} storage owner path(s) to Object storage')
    skipped_layout = int(report.get('skipped_layout_items', 0) or 0)
    if skipped_layout:
        notes.append(f'removed {skipped_layout} layout item(s) whose entry is unsupported')
    split_rows = int(report.get('split_oversized_rows', 0) or 0)
    if split_rows:
        notes.append(f'split {split_rows} row(s) to Free\'s three-column limit')
    adapted_entries = int(report.get('adapted_entry_options', 0) or 0)
    if adapted_entries:
        notes.append(f'adapted Full-only options on {adapted_entries} supported entry/entries')
    adapted_layout = int(report.get('adapted_layout_options', 0) or 0)
    if adapted_layout:
        notes.append(f'adapted {adapted_layout} advanced layout option group(s)')
    if notes:
        message += '; ' + '; '.join(notes)
    return message


def _izom_propui_free_apply_setup_document(params, document, *, context):
    target = _izom_propui_free_target_armature(params, context)
    payload, report = izom_propui_free_parse_compatible_setup_document(
        document,
        target_object_name=str(getattr(target, 'name', '') or '').strip(),
        fallback_owner_path=str(
            getattr(params, 'izom_propui_free_default_target_owner_path', '') or ''
        ).strip(),
    )
    for field_name, value in payload.get('project_settings', {}).items():
        if hasattr(params, field_name):
            setattr(params, field_name, value)

    entries = list(payload.get('entries', []) or [])
    active_entry_uid = str((entries[0] if entries else {}).get('uid', '') or '').strip()
    izom_propui_free_restore_entries(
        params,
        entries,
        active_uid=active_entry_uid,
        preserve_layout_items=True,
    )
    layout_items = list(payload.get('layout_items', []) or [])
    active_layout_uid = str((layout_items[0] if layout_items else {}).get('uid', '') or '').strip()
    _izom_propui_free_restore_layout_snapshots(
        params,
        layout_items,
        active_layout_uid=active_layout_uid,
        layout_snapshots_are_ordered=True,
    )
    params.izom_propui_free_entry_collapsed_uids_json = '[]'
    params.izom_propui_free_layout_collapsed_row_uids_json = '[]'
    izom_propui_free_apply_owner_picker_from_path(
        params,
        'izom_propui_free_default_target',
        str(getattr(params, 'izom_propui_free_default_target_owner_path', '') or '').strip(),
        context=context,
    )
    return _izom_propui_free_import_message(report)


def _izom_propui_free_json_text(document):
    return json.dumps(document, indent=2, sort_keys=True)


def _izom_propui_free_json_document(text):
    try:
        document = json.loads(str(text or ''))
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError(f'Invalid JSON: {exc}') from exc
    if not isinstance(document, dict):
        raise ValueError('Import data must be a JSON object')
    return document


class _IZOM_PROPUI_FREE_SetupTransferMixin:
    @classmethod
    def poll(cls, context):
        return izom_propui_free_context_params(context) is not None

    def _preview_setup(self, context, document):
        params = izom_propui_free_context_params(context)
        target = _izom_propui_free_target_armature(params, context)
        _payload, report = izom_propui_free_parse_compatible_setup_document(
            document,
            target_object_name=str(getattr(target, 'name', '') or '').strip(),
            fallback_owner_path=str(getattr(params, 'izom_propui_free_default_target_owner_path', '') or '').strip(),
        )
        self.preview_document_json = json.dumps(document)
        self.preview_summary = _izom_propui_free_import_message(report).replace('Imported ', 'Will import ', 1)
        return context.window_manager.invoke_props_dialog(self, width=600)

    def draw(self, _context):
        if self.preview_summary:
            self.layout.label(text='Replace the current Free setup?', icon='QUESTION')
            for paragraph in self.preview_summary.split('; '):
                for line in textwrap.wrap(paragraph, width=82):
                    self.layout.label(text=line)

    def cancel(self, _context):
        self.preview_document_json = ''
        self.preview_summary = ''


class IZOM_PROPUI_FREE_OT_export_setup_json(Operator, _IZOM_PROPUI_FREE_SetupTransferMixin, ExportHelper):
    bl_idname = 'wm.izom_propui_free_export_setup_json'
    bl_label = 'Export PropUI Free Setup'
    bl_description = 'Export the Entry List, Generated Layout, compatible entry options, and Free output settings'
    bl_options = {'INTERNAL'}

    filename_ext = '.json'
    filter_glob: StringProperty(default='*.json', options={'HIDDEN'})

    def execute(self, context):
        params = izom_propui_free_context_params(context)
        try:
            izom_propui_free_atomic_write_text(
                self.filepath, _izom_propui_free_json_text(_izom_propui_free_capture_setup_document(params))
            )
        except (OSError, ValueError) as exc:
            self.report({'WARNING'}, str(exc))
            return {'CANCELLED'}
        self.report({'INFO'}, 'Exported PropUI Free setup JSON')
        return {'FINISHED'}


class IZOM_PROPUI_FREE_OT_import_setup_json(Operator, _IZOM_PROPUI_FREE_SetupTransferMixin, ImportHelper):
    bl_idname = 'wm.izom_propui_free_import_setup_json'
    bl_label = 'Import PropUI Setup'
    bl_description = 'Replace the current Free setup with the compatible parts of a Full, Free, or Rigify setup'
    bl_options = {'UNDO', 'INTERNAL'}

    filename_ext = '.json'
    filter_glob: StringProperty(default='*.json', options={'HIDDEN'})
    preview_before_apply: BoolProperty(default=False, options={'HIDDEN', 'SKIP_SAVE'})
    preview_document_json: StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})
    preview_summary: StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})

    def invoke(self, context, event):
        self.preview_before_apply = True
        self.preview_document_json = ''
        return ImportHelper.invoke(self, context, event)

    def execute(self, context):
        params = izom_propui_free_context_params(context)
        try:
            if self.preview_document_json:
                document = _izom_propui_free_json_document(self.preview_document_json)
            else:
                with open(self.filepath, 'r', encoding='utf-8') as handle:
                    document = _izom_propui_free_json_document(handle.read())
            if self.preview_before_apply:
                self.preview_before_apply = False
                return self._preview_setup(context, document)
            message = _izom_propui_free_apply_setup_document(params, document, context=context)
        except (OSError, ValueError) as exc:
            self.report({'WARNING'}, str(exc))
            return {'CANCELLED'}
        self.report({'INFO'}, message)
        return {'FINISHED'}


class IZOM_PROPUI_FREE_OT_copy_setup_json(Operator, _IZOM_PROPUI_FREE_SetupTransferMixin):
    bl_idname = 'wm.izom_propui_free_copy_setup_json'
    bl_label = 'Copy PropUI Free Setup'
    bl_description = 'Copy the current Free setup as edition-compatible JSON'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        params = izom_propui_free_context_params(context)
        context.window_manager.clipboard = _izom_propui_free_json_text(
            _izom_propui_free_capture_setup_document(params)
        )
        self.report({'INFO'}, 'Copied PropUI Free setup JSON')
        return {'FINISHED'}


class IZOM_PROPUI_FREE_OT_paste_setup_json(Operator, _IZOM_PROPUI_FREE_SetupTransferMixin):
    bl_idname = 'wm.izom_propui_free_paste_setup_json'
    bl_label = 'Paste PropUI Setup'
    bl_description = 'Replace the current Free setup with compatible Full, Free, or Rigify setup JSON from the clipboard'
    bl_options = {'UNDO', 'INTERNAL'}

    preview_document_json: StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})
    preview_summary: StringProperty(default='', options={'HIDDEN', 'SKIP_SAVE'})

    def invoke(self, context, _event):
        try:
            document = _izom_propui_free_json_document(context.window_manager.clipboard)
            return self._preview_setup(context, document)
        except ValueError as exc:
            self.report({'WARNING'}, str(exc))
            return {'CANCELLED'}

    def execute(self, context):
        params = izom_propui_free_context_params(context)
        try:
            document = _izom_propui_free_json_document(self.preview_document_json or context.window_manager.clipboard)
            message = _izom_propui_free_apply_setup_document(params, document, context=context)
        except ValueError as exc:
            self.report({'WARNING'}, str(exc))
            return {'CANCELLED'}
        self.report({'INFO'}, message)
        return {'FINISHED'}


CLASSES = (
    IZOM_PROPUI_FREE_OT_export_setup_json,
    IZOM_PROPUI_FREE_OT_import_setup_json,
    IZOM_PROPUI_FREE_OT_copy_setup_json,
    IZOM_PROPUI_FREE_OT_paste_setup_json,
)


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

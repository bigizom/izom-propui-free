# SPDX-License-Identifier: GPL-3.0-or-later

"""Portable setup documents and cross-edition normalization for PropUI Free."""

from copy import deepcopy
import ast
import json

from .constants import IZOM_PROPUI_FREE_PROP_TYPE_IDS
from .entry_ids import _izom_propui_free_new_uid


IZOM_PROPUI_FREE_SETUP_KIND = 'propui_project_setup'
IZOM_PROPUI_FREE_RIGIFY_SETUP_KIND = 'rigify_host_bone_setup'
IZOM_PROPUI_FREE_SETUP_SCHEMA_VERSION = 1


_IZOM_PROPUI_FREE_PORTABLE_SETTING_FIELDS = {
    'izom_propui_generated_panel_tab': 'izom_propui_free_generated_panel_tab',
    'izom_propui_generated_panel_title': 'izom_propui_free_generated_panel_title',
    'izom_propui_default_target_owner_path': 'izom_propui_free_default_target_owner_path',
    'izom_propui_replace_storage_on_generate': 'izom_propui_free_replace_storage_on_generate',
    'izom_propui_clean_old_targets_on_generate': 'izom_propui_free_clean_old_targets_on_generate',
}


def _izom_propui_free_compat_owner_path(object_name, bone_name=''):
    object_name = str(object_name or '').strip()
    bone_name = str(bone_name or '').strip()
    if not object_name:
        return ''
    path = f'bpy.data.objects[{json.dumps(object_name)}]'
    if bone_name:
        path += f'.pose.bones[{json.dumps(bone_name)}]'
    return path


def _izom_propui_free_object_name_from_owner_path(owner_path):
    text = str(owner_path or '').strip()
    if not text:
        return '', False
    try:
        expression = ast.parse(text, mode='eval').body
    except (SyntaxError, TypeError, ValueError):
        return '', False
    # Follow only the owner-access chain. This recognizes both the exact
    # object path and deeper owners such as ``.pose.bones[\"control\"]``
    # without evaluating imported text.
    node = expression
    while isinstance(node, (ast.Attribute, ast.Subscript)):
        if isinstance(node, ast.Subscript):
            collection = node.value
            if isinstance(collection, ast.Attribute) and collection.attr == 'objects':
                data = collection.value
                if (
                    isinstance(data, ast.Attribute)
                    and data.attr == 'data'
                    and isinstance(data.value, ast.Name)
                    and data.value.id == 'bpy'
                ):
                    key = node.slice
                    if isinstance(key, ast.Constant) and isinstance(key.value, str):
                        return str(key.value or '').strip(), expression is node
            node = node.value
        else:
            node = node.value
    return '', False


def _izom_propui_free_validate_setup_document(document):
    source = document if isinstance(document, dict) else {}
    kind = str(source.get('kind', '') or '').strip()
    if kind not in {IZOM_PROPUI_FREE_SETUP_KIND, IZOM_PROPUI_FREE_RIGIFY_SETUP_KIND}:
        raise ValueError(
            f'Expected {IZOM_PROPUI_FREE_SETUP_KIND} or {IZOM_PROPUI_FREE_RIGIFY_SETUP_KIND} data, '
            f'got {kind or "unknown"}'
        )
    try:
        schema_version = int(source.get('schema_version', 0) or 0)
    except (TypeError, ValueError):
        schema_version = 0
    if schema_version != IZOM_PROPUI_FREE_SETUP_SCHEMA_VERSION:
        raise ValueError(f'Unsupported schema version: {schema_version}')
    payload = source.get('payload')
    if not isinstance(payload, dict):
        raise ValueError('Setup payload is missing')
    return kind, payload


def izom_propui_free_make_setup_document(*, project_settings, entries, layout_rows, layout_items):
    portable_settings = {}
    source_settings = project_settings if isinstance(project_settings, dict) else {}
    for portable_name, free_name in _IZOM_PROPUI_FREE_PORTABLE_SETTING_FIELDS.items():
        if free_name in source_settings:
            portable_settings[portable_name] = source_settings[free_name]
        elif portable_name in source_settings:
            portable_settings[portable_name] = source_settings[portable_name]
    return {
        'kind': IZOM_PROPUI_FREE_SETUP_KIND,
        'schema_version': IZOM_PROPUI_FREE_SETUP_SCHEMA_VERSION,
        'source_edition': 'FREE',
        'payload': {
            'project_settings': deepcopy(portable_settings),
            'entries': deepcopy(list(entries or [])),
            'layout_rows': deepcopy(list(layout_rows or [])),
            'layout_items': deepcopy(list(layout_items or [])),
            'layout_subpanels': [],
            'layout_box_ranges': [],
        },
    }


def _izom_propui_free_source_edition(document, kind):
    edition = str((document or {}).get('source_edition', '') or '').strip().upper()
    if edition in {'FULL', 'FREE', 'RIGIFY'}:
        return edition
    return 'RIGIFY' if kind == IZOM_PROPUI_FREE_RIGIFY_SETUP_KIND else 'FULL'


def _izom_propui_free_import_settings(payload, source_edition, *, target_object_name='', fallback_owner_path=''):
    settings = {}
    mapped_storage_bones = 0
    skipped_storage_targets = 0
    skipped_visibility_targets = 0
    if source_edition == 'RIGIFY':
        host = payload.get('host_settings')
        host = host if isinstance(host, dict) else {}
        if host.get('izom_propui_rigify_generated_ui_panel_location') == 'SEPARATE_PANEL':
            settings['izom_propui_free_generated_panel_title'] = str(host.get('izom_propui_rigify_generated_ui_panel_title', '') or '')
            settings['izom_propui_free_generated_panel_tab'] = str(host.get('izom_propui_rigify_generated_ui_sidebar_tab', 'Item') or 'Item')
        bone_name = ''
        if bool(host.get('izom_propui_rigify_use_one_prop_bone', False)):
            bone_name = str(host.get('izom_propui_rigify_one_prop_bone', '') or '').strip()
        if bone_name and target_object_name:
            settings['izom_propui_free_default_target_owner_path'] = _izom_propui_free_compat_owner_path(
                target_object_name,
            )
            mapped_storage_bones += 1
        elif bone_name:
            skipped_storage_targets += 1
            if fallback_owner_path:
                settings['izom_propui_free_default_target_owner_path'] = fallback_owner_path
        elif fallback_owner_path:
            settings['izom_propui_free_default_target_owner_path'] = fallback_owner_path
        skipped_visibility_targets = 0 if bool(host.get('izom_propui_rigify_generated_ui_always_visible', False)) else len({
            str(item.get('bone_name', item.get('name', '')) if isinstance(item, dict) else item or '').strip()
            for item in payload.get('visible_on_bones', []) or []
            if str(item.get('bone_name', item.get('name', '')) if isinstance(item, dict) else item or '').strip()
        })
        return settings, mapped_storage_bones, skipped_storage_targets, skipped_visibility_targets

    raw_settings = payload.get('project_settings')
    raw_settings = raw_settings if isinstance(raw_settings, dict) else {}
    for portable_name, free_name in _IZOM_PROPUI_FREE_PORTABLE_SETTING_FIELDS.items():
        if portable_name in raw_settings:
            settings[free_name] = raw_settings[portable_name]
        elif free_name in raw_settings:
            settings[free_name] = raw_settings[free_name]

    imported_owner_path = str(settings.get('izom_propui_free_default_target_owner_path', '') or '').strip()
    if imported_owner_path:
        object_name, is_exact_object = _izom_propui_free_object_name_from_owner_path(imported_owner_path)
        if object_name:
            settings['izom_propui_free_default_target_owner_path'] = _izom_propui_free_compat_owner_path(object_name)
            if not is_exact_object:
                mapped_storage_bones += 1
        elif target_object_name:
            settings['izom_propui_free_default_target_owner_path'] = _izom_propui_free_compat_owner_path(target_object_name)
            mapped_storage_bones += 1
        elif fallback_owner_path:
            settings['izom_propui_free_default_target_owner_path'] = fallback_owner_path
            skipped_storage_targets += 1
        else:
            settings.pop('izom_propui_free_default_target_owner_path', None)
            skipped_storage_targets += 1

    visibility_mode = str(raw_settings.get('izom_propui_generated_visibility_mode', 'ALWAYS') or 'ALWAYS').strip().upper()
    if visibility_mode == 'SELECTED_OBJECTS':
        raw_targets = raw_settings.get('izom_propui_generated_visibility_targets_json', [])
        if isinstance(raw_targets, str):
            try:
                raw_targets = json.loads(raw_targets)
            except (TypeError, ValueError, json.JSONDecodeError):
                raw_targets = []
        skipped_visibility_targets = len(raw_targets) if isinstance(raw_targets, list) else 0
    return settings, mapped_storage_bones, skipped_storage_targets, skipped_visibility_targets


_IZOM_PROPUI_FREE_UNSUPPORTED_ENTRY_OPTION_DEFAULTS = {
    'bool_ui_style': 'CHECKBOX',
    'bool_icon_true': 'NONE',
    'bool_icon_false': 'NONE',
    'stacked_label_use_text_style': False,
    'array_component_label_style': 'AUTO',
    'array_component_label_custom_base': 'AUTO',
    'hidden_in_editor': False,
    'use_other_entry_labels': False,
    'text_use_other_entry_labels': False,
    'shared_row_hidden_mode': 'FILL_ROW',
    'bool_child_availability': 'ALWAYS',
    'number_child_availability': 'ALWAYS',
    'availability_inheritance_depth': 1,
    'availability_use_component': False,
}


def _izom_propui_free_entry_uses_unsupported_options(entry):
    for field_name, default_value in _IZOM_PROPUI_FREE_UNSUPPORTED_ENTRY_OPTION_DEFAULTS.items():
        if field_name in entry and entry.get(field_name) != default_value:
            return True
    for field_name, value in entry.items():
        if field_name.startswith('array_component_label_') and field_name not in {
            'array_component_label_style',
            'array_component_label_custom_base',
        } and str(value or '').strip():
            return True
    for label in entry.get('value_labels', []) or []:
        if not isinstance(label, dict):
            continue
        if (
            bool(label.get('text_override_style', False))
            or bool(label.get('use_other_entry_labels', False))
            or str(label.get('source_entry_uid', '') or '').strip()
        ):
            return True
    return False


def _izom_propui_free_supported_entries(payload, source_edition):
    raw_entries = [deepcopy(item) for item in payload.get('entries', []) or [] if isinstance(item, dict)]
    raw_by_uid = {
        str(item.get('uid', '') or '').strip(): item
        for item in raw_entries
        if str(item.get('uid', '') or '').strip()
    }
    supported = []
    supported_uids = set()
    skipped_types = {}
    skipped_storage_targets = 0
    adapted_entry_options = 0
    for entry in raw_entries:
        prop_type = str(entry.get('prop_type', 'FLOAT') or 'FLOAT').strip().upper()
        if prop_type == 'FLOAT_ARRAY':
            prop_type = 'ARRAY'
            entry['prop_type'] = prop_type
        if prop_type not in IZOM_PROPUI_FREE_PROP_TYPE_IDS:
            skipped_types[prop_type] = skipped_types.get(prop_type, 0) + 1
            continue
        if _izom_propui_free_entry_uses_unsupported_options(entry):
            adapted_entry_options += 1
        uid = str(entry.get('uid', '') or '').strip() or _izom_propui_free_new_uid()
        entry['uid'] = uid
        supported_uids.add(uid)
        if source_edition == 'RIGIFY':
            if entry.get('entry_prop_bone_override_enabled', True) and str(entry.get('entry_prop_bone', '') or '').strip():
                skipped_storage_targets += 1
        elif str(entry.get('entry_target_owner_path', '') or '').strip():
            skipped_storage_targets += 1
        entry.pop('entry_prop_bone', None)
        entry.pop('entry_prop_bone_override_enabled', None)
        entry.pop('entry_target_owner_path', None)
        supported.append(entry)

    # If an unsupported parent is removed, attach the child to its nearest
    # supported ancestor so that compatible hierarchy remains meaningful.
    for entry in supported:
        parent_uid = str(entry.get('parent_uid', '') or '').strip()
        visited = set()
        while parent_uid and parent_uid not in supported_uids and parent_uid not in visited:
            visited.add(parent_uid)
            parent = raw_by_uid.get(parent_uid)
            parent_uid = str((parent or {}).get('parent_uid', '') or '').strip()
        entry['parent_uid'] = parent_uid if parent_uid in supported_uids else ''
    return supported, supported_uids, skipped_types, skipped_storage_targets, adapted_entry_options


def _izom_propui_free_flatten_layout(payload, supported_uids):
    raw_items = [
        (index, deepcopy(item))
        for index, item in enumerate(payload.get('layout_items', []) or [])
        if isinstance(item, dict)
    ]
    kept = [
        (index, item)
        for index, item in raw_items
        if str(item.get('entry_uid', '') or '').strip() in supported_uids
    ]
    skipped_layout_items = len(raw_items) - len(kept)
    kept.sort(key=lambda pair: (
        max(1, int(pair[1].get('row_index', 1) or 1)),
        max(1, int(pair[1].get('column_index', 1) or 1)),
        pair[0],
    ))
    grouped = {}
    source_rows = []
    for pair in kept:
        source_row = max(1, int(pair[1].get('row_index', 1) or 1))
        if source_row not in grouped:
            source_rows.append(source_row)
            grouped[source_row] = []
        grouped[source_row].append(pair)

    raw_rows = {
        max(1, int(item.get('row_index', 1) or 1)): item
        for item in payload.get('layout_rows', []) or []
        if isinstance(item, dict)
    }
    layout_items = []
    layout_rows = []
    split_oversized_rows = 0
    adapted_layout_options = 0
    next_row_index = 1
    for source_row in source_rows:
        raw = raw_rows.get(source_row, {})
        source_items = grouped[source_row]
        chunks = [source_items[index:index + 3] for index in range(0, len(source_items), 3)]
        if len(chunks) > 1:
            split_oversized_rows += 1
        try:
            row_height = float(raw.get('row_height_scale', 1.0) or 1.0)
        except (TypeError, ValueError):
            row_height = 1.0
            adapted_layout_options += 1
        if bool(raw.get('row_inset_right_enabled', False)) or row_height > 2.0:
            adapted_layout_options += 1
        if bool(raw.get('row_inset_left_enabled', False)):
            try:
                if abs(float(raw.get('row_inset_left_amount', 0.25) or 0.25) - 0.25) > 1e-6:
                    adapted_layout_options += 1
            except (TypeError, ValueError):
                adapted_layout_options += 1
        for chunk in chunks:
            row_snapshot = {
                'row_index': next_row_index,
                'row_height_scale': raw.get('row_height_scale', 1.0),
                'row_inset_left_enabled': bool(raw.get('row_inset_left_enabled', False)),
                'row_inset_left_amount': raw.get('row_inset_left_amount', 0.25),
            }
            layout_rows.append(row_snapshot)
            for column_index, (_source_index, item) in enumerate(chunk, start=1):
                if (
                    bool(item.get('row_width_enabled', False))
                    or str(item.get('single_row_alignment', 'LEFT') or 'LEFT').strip().upper() != 'LEFT'
                ):
                    adapted_layout_options += 1
                layout_items.append({
                    'uid': str(item.get('uid', '') or '').strip() or _izom_propui_free_new_uid(),
                    'entry_uid': str(item.get('entry_uid', '') or '').strip(),
                    'row_index': next_row_index,
                    'column_index': column_index,
                    **row_snapshot,
                })
            next_row_index += 1
    return layout_rows, layout_items, skipped_layout_items, split_oversized_rows, adapted_layout_options


def izom_propui_free_parse_compatible_setup_document(
    document,
    *,
    target_object_name='',
    fallback_owner_path='',
):
    kind, payload = _izom_propui_free_validate_setup_document(document)
    source_edition = _izom_propui_free_source_edition(document, kind)
    settings, mapped_storage_bones, skipped_default_storage, skipped_visibility = (
        _izom_propui_free_import_settings(
            payload,
            source_edition,
            target_object_name=str(target_object_name or '').strip(),
            fallback_owner_path=str(fallback_owner_path or '').strip(),
        )
    )
    entries, supported_uids, skipped_types, skipped_entry_storage, adapted_entry_options = _izom_propui_free_supported_entries(
        payload,
        source_edition,
    )
    layout_rows, layout_items, skipped_layout_items, split_oversized_rows, adapted_layout_options = _izom_propui_free_flatten_layout(
        payload,
        supported_uids,
    )
    subpanels = [item for item in payload.get('layout_subpanels', []) or [] if isinstance(item, dict)]
    boxes = [item for item in payload.get('layout_box_ranges', []) or [] if isinstance(item, dict)]
    return {
        'project_settings': settings,
        'entries': entries,
        'layout_rows': layout_rows,
        'layout_items': layout_items,
    }, {
        'source_edition': source_edition,
        'imported_entries': len(entries),
        'imported_layout_items': len(layout_items),
        'skipped_entry_types': skipped_types,
        'skipped_layout_items': skipped_layout_items,
        'split_oversized_rows': split_oversized_rows,
        'adapted_entry_options': adapted_entry_options,
        'adapted_layout_options': adapted_layout_options,
        'flattened_subpanels': len(subpanels),
        'skipped_row_boxes': len(boxes),
        'mapped_storage_bones': mapped_storage_bones,
        'skipped_storage_targets': skipped_default_storage + skipped_entry_storage,
        'skipped_visibility_targets': skipped_visibility,
    }


from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

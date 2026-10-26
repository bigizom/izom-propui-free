# SPDX-License-Identifier: GPL-3.0-or-later

import ast
import json

import bpy

from .diagnostics import izom_propui_free_log_recovered


def izom_propui_free_quote_data_path_key(value):
    return json.dumps(str(value or ''))


def izom_propui_free_object_owner_path(obj):
    if obj is None:
        return ''
    name = str(getattr(obj, 'name', '') or '').strip()
    if not name:
        return ''
    return f"bpy.data.objects[{izom_propui_free_quote_data_path_key(name)}]"


def izom_propui_free_owner_path_from_picker_owner(owner, prefix, *, context=None, allow_default=False):
    default_kind = 'DEFAULT' if allow_default else 'OBJECT'
    kind = str(getattr(owner, f'{prefix}_kind', default_kind) or default_kind).strip().upper()
    if kind == 'DEFAULT' and allow_default:
        return ''
    obj = getattr(owner, f'{prefix}_object', None)
    if obj is None:
        obj = getattr(context or getattr(bpy, 'context', None), 'active_object', None)
    return izom_propui_free_object_owner_path(obj)


def izom_propui_free_sync_owner_path_from_picker(owner, prefix, path_attr, *, context=None, allow_default=False):
    owner_path = izom_propui_free_owner_path_from_picker_owner(
        owner,
        prefix,
        context=context,
        allow_default=allow_default,
    )
    try:
        if getattr(owner, path_attr, '') != owner_path:
            setattr(owner, path_attr, owner_path)
    except (AttributeError, TypeError, ValueError, RuntimeError, ReferenceError) as exc:
        izom_propui_free_log_recovered(category='Core', exception=exc)
    return owner_path


def izom_propui_free_apply_owner_picker_from_path(owner, prefix, owner_path, *, context=None):
    obj = None
    text = str(owner_path or '').strip()
    if text:
        obj = izom_propui_free_resolve_owner_path(text)
    if obj is None:
        obj = getattr(context or getattr(bpy, 'context', None), 'active_object', None)
    try:
        setattr(owner, f'{prefix}_kind', 'OBJECT')
        setattr(owner, f'{prefix}_object', obj)
    except (AttributeError, TypeError, ValueError, RuntimeError, ReferenceError) as exc:
        izom_propui_free_log_recovered(category='Core', exception=exc)


def izom_propui_free_resolve_owner_path_strict(owner_path):
    text = str(owner_path or '').strip()
    if not text:
        raise ValueError('Owner path is empty')
    try:
        expression = ast.parse(text, mode='eval').body
    except SyntaxError as exc:
        raise ValueError(str(exc)) from exc

    def resolve_node(node):
        if isinstance(node, ast.Name):
            if node.id != 'bpy':
                raise ValueError(f"Unsupported owner path root {node.id!r}")
            return bpy
        if isinstance(node, ast.Attribute):
            return getattr(resolve_node(node.value), node.attr)
        if isinstance(node, ast.Subscript):
            target = resolve_node(node.value)
            key = node.slice
            if isinstance(key, ast.Constant) and isinstance(key.value, (str, int)):
                return target[key.value]
            if (
                isinstance(key, ast.UnaryOp)
                and isinstance(key.op, ast.USub)
                and isinstance(key.operand, ast.Constant)
                and isinstance(key.operand.value, int)
            ):
                return target[-key.operand.value]
            raise ValueError('Owner path subscripts must use literal string or integer keys')
        raise ValueError(f"Unsupported owner path expression {type(node).__name__}")

    try:
        owner = resolve_node(expression)
    except (AttributeError, TypeError, KeyError, IndexError, RuntimeError, ReferenceError, ValueError) as exc:
        raise ValueError(str(exc)) from exc
    if not isinstance(owner, bpy.types.Object):
        raise ValueError('Free property storage target must be an Object')
    return owner


def izom_propui_free_resolve_owner_path(owner_path):
    try:
        return izom_propui_free_resolve_owner_path_strict(owner_path)
    except ValueError as exc:
        izom_propui_free_log_recovered(category='Core', exception=exc)
        return None


def izom_propui_free_owner_path_label(owner_path):
    owner = izom_propui_free_resolve_owner_path(owner_path)
    if owner is None:
        return str(owner_path or '').strip() or 'None'
    name = str(getattr(owner, 'name', '') or '').strip()
    type_name = type(owner).__name__
    return f"{type_name}: {name}" if name else type_name

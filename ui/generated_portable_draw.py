# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
import ast
import hashlib
import json

from ..core.constants import (
    IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TAB,
    IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TITLE,
)
from ..core.diagnostics import izom_propui_free_log_recovered
from .generated_slots import (
    _izom_propui_free_generated_slot_panel_specs,
)
from .generated_branding import izom_propui_free_generated_panel_class_name


def _izom_propui_free_portable_direct_class_name(slot, index, space_type):
    identity = {
        "uid": str((slot or {}).get("uid", "") or ""),
        "space_type": str(space_type or ""),
        "scene_name": str((slot or {}).get("scene_name", "") or ""),
        "tab": str((slot or {}).get("tab", "") or ""),
        "title": str((slot or {}).get("title", "") or ""),
        "index": int(index),
    }
    digest = hashlib.sha1(json.dumps(identity, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    return izom_propui_free_generated_panel_class_name((slot or {}).get('branding'), digest)

def _izom_propui_free_portable_direct_draw_name(index):
    return f"_draw_{int(index) + 1}"

def _izom_propui_free_portable_direct_owner_var(index):
    return f"izom_propui_free_target_owner_{int(index) + 1}"

def _izom_propui_free_portable_target_owner_path(line):
    text = str(line or "").strip().rstrip(",")
    marker = ": _izom_propui_free_resolve_owner_path("
    if marker not in text or not text.endswith(")"):
        return ""
    key_expr, arg_expr = text.split(marker, 1)
    arg_expr = arg_expr[:-1]
    try:
        key_value = ast.literal_eval(key_expr.strip())
        arg_value = ast.literal_eval(arg_expr.strip())
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        return ""
    key_text = str(key_value or "").strip()
    arg_text = str(arg_value or "").strip()
    return key_text if key_text and key_text == arg_text else ""

def _izom_propui_free_portable_apply_owner_vars(lines, owner_vars):
    text = "\n".join(lines)
    for owner_path, owner_var in (owner_vars or {}).items():
        literal = repr(str(owner_path or ""))
        text = text.replace(f"target_owners.get({literal}, {{}})", f"({owner_var} or {{}})")
        text = text.replace(f"target_owners.get({literal})", owner_var)
    return text

def _izom_propui_free_portable_direct_skip_nested_function(lines, index):
    index += 1
    while index < len(lines) and (lines[index].startswith("        ") or not lines[index].strip()):
        index += 1
    return index

def _izom_propui_free_portable_direct_insert_target_owner_mapping(text, owner_vars):
    if "target_owners" not in str(text or "") or "    target_owners = {" in str(text or ""):
        return text
    lines = str(text or "").splitlines()
    if not lines:
        return text
    mapping_lines = ["    target_owners = {"]
    for owner_path, owner_var in (owner_vars or {}).items():
        mapping_lines.append(f"        {owner_path!r}: {owner_var},")
    mapping_lines.append("    }")
    insert_at = 1
    while insert_at < len(lines):
        candidate = lines[insert_at]
        if candidate.startswith("    izom_propui_free_target_owner_") or not candidate.strip():
            insert_at += 1
            continue
        break
    return "\n".join(lines[:insert_at] + mapping_lines + lines[insert_at:])

def _izom_propui_free_portable_direct_function_blocks(source):
    lines = str(source or "").strip().splitlines()
    blocks = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.startswith("def ") or "(" not in line:
            index += 1
            continue
        name = line[4:].split("(", 1)[0].strip()
        start = index
        index += 1
        while index < len(lines) and not lines[index].startswith("def "):
            index += 1
        if name:
            blocks[name] = "\n".join(lines[start:index]).rstrip()
    return blocks

def _izom_propui_free_portable_direct_transform_draw_text(text):
    lines = str(text or "").strip().splitlines()
    cleaned = []
    owner_vars = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        if line == "    import bpy":
            index += 1
            continue
        if "_owner_path_ast_cache = globals().setdefault('_IZOM_PROPUI_FREE_OWNER_PATH_AST_CACHE', {})" in line:
            index += 1
            continue
        if line == "    def _izom_propui_free_resolve_owner_path(_path):":
            index = _izom_propui_free_portable_direct_skip_nested_function(lines, index)
            continue
        if line.startswith("    def izom_propui_free_compact_label_value_layout("):
            index = _izom_propui_free_portable_direct_skip_nested_function(lines, index)
            continue
        if line == "    target_owners = {}":
            index += 1
            continue
        if line == "    target_owners = {":
            index += 1
            while index < len(lines) and lines[index] != "    }":
                owner_path = _izom_propui_free_portable_target_owner_path(lines[index])
                if owner_path and owner_path not in owner_vars:
                    owner_var = _izom_propui_free_portable_direct_owner_var(len(owner_vars))
                    owner_vars[owner_path] = owner_var
                    cleaned.append(f"    {owner_var} = _izom_propui_free_resolve_owner_path({owner_path!r})")
                index += 1
            if index < len(lines) and lines[index] == "    }":
                index += 1
            continue
        cleaned.append(line)
        index += 1
    portable_text = _izom_propui_free_portable_apply_owner_vars(cleaned, owner_vars)
    portable_text = portable_text.replace(
        "izom_propui_free_compact_label_value_layout(",
        "_compact_label_value_layout(",
    )
    portable_text = _izom_propui_free_portable_direct_insert_target_owner_mapping(portable_text, owner_vars)
    return portable_text.rstrip()

def _izom_propui_free_portable_direct_draw_source(source, function_name):
    if isinstance(function_name, dict):
        text = str(source or "").strip()
        if not text:
            return "\n".join([
                "def _draw_missing(context, layout):",
                "    layout.label(text='Generated PropUI draw function is missing.', icon='ERROR')",
            ])
        function_blocks = _izom_propui_free_portable_direct_function_blocks(text)
        transformed = []
        for source_name, target_name in sorted(
            ((str(key or "").strip(), str(value or "").strip()) for key, value in function_name.items()),
            key=lambda item: -len(item[0]),
        ):
            if not source_name or not target_name:
                continue
            block = function_blocks.get(source_name, "")
            if not block:
                transformed.append("\n".join([
                    f"def {target_name}(context, layout):",
                    "    layout.label(text='Generated PropUI draw function is missing.', icon='ERROR')",
                ]))
                continue
            block = block.replace(
                f"def {source_name}(context, layout):",
                f"def {target_name}(context, layout):",
                1,
            )
            transformed.append(_izom_propui_free_portable_direct_transform_draw_text(block))
        return "\n\n".join(item for item in transformed if str(item or "").strip()).rstrip()

    text = str(source or "").strip()
    needle = "def _izom_propui_free_generated_draw(context, layout):"
    replacement = f"def {function_name}(context, layout):"
    if needle in text:
        text = text.replace(needle, replacement, 1).rstrip()
    else:
        return "\n".join([
            replacement,
            "    layout.label(text='Generated PropUI draw function is missing.', icon='ERROR')",
        ])

    return _izom_propui_free_portable_direct_transform_draw_text(text)


def _izom_propui_free_prepare_direct_portable_script(slots):
    panels = []
    draw_sources = []
    for slot_index, slot in enumerate(slots or []):
        if not isinstance(slot, dict):
            continue
        source = str(slot.get("source", "") or "").strip()
        if not source:
            continue
        base_draw_name = _izom_propui_free_portable_direct_draw_name(len(draw_sources))
        draw_sources.append(_izom_propui_free_portable_direct_draw_source(source, base_draw_name))
        panel_specs = list(_izom_propui_free_generated_slot_panel_specs(slot))
        for panel_spec in panel_specs:
            panel_key = ":".join((
                "SIDEBAR",
                str(panel_spec.get("space_type", "") or "").strip().upper(),
                str(panel_spec.get("region_type", "") or "").strip().upper(),
            ))
            panels.append({
                "class_name": _izom_propui_free_portable_direct_class_name(slot, slot_index, panel_key),
                "draw_fn": base_draw_name,
                "space_type": "VIEW_3D",
                "region_type": "UI",
                "title": str(slot.get("title", "") or "").strip() or IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TITLE,
                "tab": (
                    str(panel_spec.get("tab", "") or slot.get("tab", "") or "").strip()
                    or IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TAB
                ),
                "scene_name": str(slot.get("scene_name", "") or "").strip(),
            })
    return panels, draw_sources

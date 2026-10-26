# SPDX-License-Identifier: GPL-3.0-or-later


def _izom_propui_free_skip_generated_nested_function(lines, index):
    index += 1
    while index < len(lines) and (lines[index].startswith("        ") or not str(lines[index]).strip()):
        index += 1
    return index


def _izom_propui_free_generated_helper_used_outside(lines, signature, call_name):
    body_lines = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if str(line).startswith(signature):
            index = _izom_propui_free_skip_generated_nested_function(lines, index)
            continue
        body_lines.append(line)
        index += 1
    return f"{call_name}(" in "\n".join(body_lines)


def _izom_propui_free_strip_generated_nested_function(lines, signature):
    cleaned = []
    index = 0
    changed = False
    while index < len(lines):
        line = lines[index]
        if str(line).startswith(signature):
            index = _izom_propui_free_skip_generated_nested_function(lines, index)
            changed = True
            continue
        cleaned.append(line)
        index += 1
    return cleaned, changed


def _izom_propui_free_prune_generated_draw_helpers(lines):
    specs = (
        ("    def _izom_propui_free_resolve_owner_path(", "_izom_propui_free_resolve_owner_path"),
        ("    def izom_propui_free_compact_label_value_layout(", "izom_propui_free_compact_label_value_layout"),
    )
    pruned = list(lines or ())
    changed = True
    while changed:
        changed = False
        for signature, call_name in specs:
            if _izom_propui_free_generated_helper_used_outside(pruned, signature, call_name):
                continue
            pruned, removed = _izom_propui_free_strip_generated_nested_function(pruned, signature)
            changed = changed or removed
    if not any(str(line).startswith("    def _izom_propui_free_resolve_owner_path(") for line in pruned):
        pruned = [
            line for line in pruned
            if "_owner_path_ast_cache = globals().setdefault('_IZOM_PROPUI_FREE_OWNER_PATH_AST_CACHE', {})" not in str(line)
        ]
    return pruned



from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

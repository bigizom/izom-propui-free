# SPDX-License-Identifier: GPL-3.0-or-later

import textwrap





def _izom_propui_free_portable_direct_poll_lines(panel):
    scene_name = str(panel.get("scene_name", "") or "").strip()
    if not scene_name:
        return []
    return [
        "    @classmethod",
        "    def poll(cls, context):",
        f"        return getattr(getattr(context, 'scene', None), 'name', '') in ('', {scene_name!r})",
    ]




def _izom_propui_free_portable_direct_owner_path_resolver_section():
    return textwrap.dedent("""\
        _OWNER_PATH_AST_CACHE = {}


        def _izom_propui_free_resolve_owner_path(path):
            try:
                import ast as _ast
                text = str(path or "").strip()
                if not text:
                    raise ValueError("Owner path is empty")
                expression = _OWNER_PATH_AST_CACHE.get(text)
                if expression is None:
                    expression = _ast.parse(text, mode="eval").body
                    _OWNER_PATH_AST_CACHE[text] = expression

                def resolve_node(node):
                    if isinstance(node, _ast.Name):
                        if node.id != "bpy":
                            raise ValueError("Unsupported owner path root %r" % node.id)
                        return bpy
                    if isinstance(node, _ast.Attribute):
                        return getattr(resolve_node(node.value), node.attr)
                    if isinstance(node, _ast.Subscript):
                        target = resolve_node(node.value)
                        key = node.slice
                        if isinstance(key, _ast.Constant) and isinstance(key.value, (str, int)):
                            return target[key.value]
                        if (
                            isinstance(key, _ast.UnaryOp)
                            and isinstance(key.op, _ast.USub)
                            and isinstance(key.operand, _ast.Constant)
                            and isinstance(key.operand.value, int)
                        ):
                            return target[-key.operand.value]
                        raise ValueError("Owner path subscripts must use literal string or integer keys")
                    raise ValueError("Unsupported owner path expression %s" % type(node).__name__)

                return resolve_node(expression)
            except (RuntimeError, ValueError, TypeError, AttributeError, SyntaxError, ReferenceError, LookupError, OSError, ImportError, KeyError, IndexError) as exc:
                print("[izom PropUI Free][WARNING][Generated UI] Could not resolve owner path %r: %s" % (path, exc))
                return None
    """).strip()


def _izom_propui_free_portable_direct_layout_section(
    *,
    include_compact_label_layout=False,
):
    include_compact_label_layout = bool(include_compact_label_layout)
    if not include_compact_label_layout:
        return ""
    section = textwrap.dedent("""\
        _COMPACT_LABEL_WIDTH_CACHE = {}
        _BLF_DIMENSIONS = None


        def _compact_label_value_layout(context, row, label_text):
            global _BLF_DIMENSIONS
            text = str(label_text or "")
            if not text:
                return row.row(align=True)
            ui_scale = max(
                0.25,
                float(getattr(getattr(getattr(context, "preferences", None), "system", None), "ui_scale", 1.0) or 1.0),
            )
            label_pixels = _COMPACT_LABEL_WIDTH_CACHE.get(text)
            if label_pixels is None:
                if _BLF_DIMENSIONS is None:
                    try:
                        import blf
                        _BLF_DIMENSIONS = blf.dimensions
                    except (RuntimeError, ValueError, TypeError, AttributeError, SyntaxError, ReferenceError, LookupError, OSError, ImportError) as exc:
                        print("[izom PropUI Free][WARNING][Generated UI] Could not load label measurement helper: %s" % exc)
                        _BLF_DIMENSIONS = False
                if _BLF_DIMENSIONS:
                    try:
                        label_pixels = float(_BLF_DIMENSIONS(0, text)[0] or 0.0)
                        if label_pixels <= 0.0:
                            raise ValueError("zero measured label width")
                    except (RuntimeError, ValueError, TypeError, AttributeError, SyntaxError, ReferenceError, LookupError, OSError, ImportError) as exc:
                        print("[izom PropUI Free][WARNING][Generated UI] Could not measure inline label width: %s" % exc)
                        label_pixels = len(text) * 5.5
                else:
                    label_pixels = len(text) * 5.5
                _COMPACT_LABEL_WIDTH_CACHE[text] = label_pixels
            label_pixels = min(720.0, max(24.0, (label_pixels * ui_scale * 1.08) + (18.0 * ui_scale)))
            region_width = max(1.0, float(getattr(getattr(context, "region", None), "width", 320) or 320))
            available_width = max(1.0, region_width - (20.0 * ui_scale))
            value_min_pixels = max(10.0, 14.0 * ui_scale)
            label_width_pixels = min(label_pixels, max(24.0, available_width - value_min_pixels))
            label_factor = max(0.04, min(0.985, label_width_pixels / available_width))
            split = row.split(factor=label_factor, align=True)
            label_col = split.row(align=True)
            label_col.label(text=text)
            return split.row(align=True)

    """).strip()
    return section

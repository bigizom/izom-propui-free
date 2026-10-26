# SPDX-License-Identifier: GPL-3.0-or-later


_IZOM_PROPUI_FREE_GENERATED_SOURCE_HEADER_CACHE = {}
_IZOM_PROPUI_FREE_GENERATED_SOURCE_HEADER_CACHE_LIMIT = 96


def _izom_propui_free_clear_generated_source_header_cache():
    _IZOM_PROPUI_FREE_GENERATED_SOURCE_HEADER_CACHE.clear()


def _izom_propui_free_generated_source_header(owner_paths, *, function_name='_izom_propui_free_generated_draw', branding=None):
    draw_name = str(function_name or '_izom_propui_free_generated_draw').strip() or '_izom_propui_free_generated_draw'
    owner_path_list = tuple(str(path or '').strip() for path in (owner_paths or []) if str(path or '').strip())
    cache_key = (draw_name, owner_path_list)
    cached = _IZOM_PROPUI_FREE_GENERATED_SOURCE_HEADER_CACHE.get(cache_key)
    if cached is not None:
        return list(cached)

    lines = [
        f"def {draw_name}(context, layout):",
        "    import bpy",
        "    _owner_path_ast_cache = globals().setdefault('_IZOM_PROPUI_FREE_OWNER_PATH_AST_CACHE', {})",
        "    def _izom_propui_free_resolve_owner_path(_path):",
        "        try:",
        "            import ast as _ast",
        "            _text = str(_path or '').strip()",
        "            if not _text:",
        "                raise ValueError('Owner path is empty')",
        "            _expression = _owner_path_ast_cache.get(_text)",
        "            if _expression is None:",
        "                _expression = _ast.parse(_text, mode='eval').body",
        "                _owner_path_ast_cache[_text] = _expression",
        "            def _resolve_node(_node):",
        "                if isinstance(_node, _ast.Name):",
        "                    if _node.id != 'bpy':",
        "                        raise ValueError('Unsupported owner path root %r' % _node.id)",
        "                    return bpy",
        "                if isinstance(_node, _ast.Attribute):",
        "                    return getattr(_resolve_node(_node.value), _node.attr)",
        "                if isinstance(_node, _ast.Subscript):",
        "                    _target = _resolve_node(_node.value)",
        "                    _key = _node.slice",
        "                    if isinstance(_key, _ast.Constant) and isinstance(_key.value, (str, int)):",
        "                        return _target[_key.value]",
        "                    if (",
        "                        isinstance(_key, _ast.UnaryOp)",
        "                        and isinstance(_key.op, _ast.USub)",
        "                        and isinstance(_key.operand, _ast.Constant)",
        "                        and isinstance(_key.operand.value, int)",
        "                    ):",
        "                        return _target[-_key.operand.value]",
        "                    raise ValueError('Owner path subscripts must use literal string or integer keys')",
        "                raise ValueError('Unsupported owner path expression %s' % type(_node).__name__)",
        "            return _resolve_node(_expression)",
        "        except (RuntimeError, ValueError, TypeError, AttributeError, SyntaxError, ReferenceError, LookupError, OSError, ImportError, KeyError, IndexError) as exc:",
        "            print('[izom PropUI Free][WARNING][Generated UI] Could not resolve owner path %r: %s' % (_path, exc))",
        "            return None",
        "    def izom_propui_free_compact_label_value_layout(_context, _row, _label_text):",
        "        _text = str(_label_text or '')",
        "        if not _text:",
        "            return _row.row(align=True)",
        "        _ui_scale = max(0.25, float(getattr(getattr(getattr(_context, 'preferences', None), 'system', None), 'ui_scale', 1.0) or 1.0))",
        "        _compact_label_width_cache = globals().setdefault('_IZOM_PROPUI_FREE_COMPACT_LABEL_WIDTH_CACHE', {})",
        "        _label_pixels = _compact_label_width_cache.get(_text)",
        "        if _label_pixels is None:",
        "            _blf_dimensions = globals().get('_IZOM_PROPUI_FREE_BLF_DIMENSIONS', None)",
        "            if _blf_dimensions is None:",
        "                try:",
        "                    import blf",
        "                    _blf_dimensions = blf.dimensions",
        "                except (RuntimeError, ValueError, TypeError, AttributeError, SyntaxError, ReferenceError, LookupError, OSError, ImportError) as exc:",
        "                    print('[izom PropUI Free][WARNING][Generated UI] Could not load label measurement helper: %s' % exc)",
        "                    _blf_dimensions = False",
        "                globals()['_IZOM_PROPUI_FREE_BLF_DIMENSIONS'] = _blf_dimensions",
        "            if _blf_dimensions:",
        "                try:",
        "                    _label_pixels = float(_blf_dimensions(0, _text)[0] or 0.0)",
        "                    if _label_pixels <= 0.0:",
        "                        raise ValueError('zero measured label width')",
        "                except (RuntimeError, ValueError, TypeError, AttributeError, SyntaxError, ReferenceError, LookupError, OSError, ImportError) as exc:",
        "                    print('[izom PropUI Free][WARNING][Generated UI] Could not measure inline label width: %s' % exc)",
        "                    _label_pixels = len(_text) * 5.5",
        "            else:",
        "                _label_pixels = len(_text) * 5.5",
        "            _compact_label_width_cache[_text] = _label_pixels",
        "        _label_pixels = min(720.0, max(24.0, (_label_pixels * _ui_scale * 1.08) + (18.0 * _ui_scale)))",
        "        _region_width = max(1.0, float(getattr(getattr(_context, 'region', None), 'width', 320) or 320))",
        "        _available_width = max(1.0, _region_width - (20.0 * _ui_scale))",
        "        _value_min_pixels = max(10.0, 14.0 * _ui_scale)",
        "        _label_width_pixels = min(_label_pixels, max(24.0, _available_width - _value_min_pixels))",
        "        _label_factor = max(0.04, min(0.985, _label_width_pixels / _available_width))",
        "        _split = _row.split(factor=_label_factor, align=True)",
        "        _label_col = _split.row(align=True)",
        "        _label_col.label(text=_text)",
        "        return _split.row(align=True)",
    ]
    if owner_path_list:
        lines.append("    target_owners = {")
        for owner_path in owner_path_list:
            lines.append(f"        {owner_path!r}: _izom_propui_free_resolve_owner_path({owner_path!r}),")
        lines.append("    }")
    else:
        lines.append("    target_owners = {}")
    lines.append("    izom_propui_free_root = layout.column(align=True)")
    if len(_IZOM_PROPUI_FREE_GENERATED_SOURCE_HEADER_CACHE) >= _IZOM_PROPUI_FREE_GENERATED_SOURCE_HEADER_CACHE_LIMIT:
        _IZOM_PROPUI_FREE_GENERATED_SOURCE_HEADER_CACHE.clear()
    _IZOM_PROPUI_FREE_GENERATED_SOURCE_HEADER_CACHE[cache_key] = tuple(lines)
    return list(lines)



from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401
__all__ = izom_propui_free_public_names(globals(), all_public=True)

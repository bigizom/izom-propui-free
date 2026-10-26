# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.constants import (
    IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TAB,
    IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TITLE,
)
from .generated_portable_runtime_sections import _izom_propui_free_portable_direct_poll_lines


def _izom_propui_free_portable_direct_panel_section(panel):
    class_name = str(panel.get("class_name", "") or "").strip()
    draw_fn = str(panel.get("draw_fn", "") or "").strip()
    lines = [
        f"class {class_name}(bpy.types.Panel):",
        f"    bl_idname = {class_name!r}",
        "    _izom_propui_free_registry_key = _REGISTRY_KEY",
        f"    bl_label = {str(panel.get('title', '') or IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TITLE)!r}",
        "    bl_space_type = 'VIEW_3D'",
        "    bl_region_type = 'UI'",
        f"    bl_category = {str(panel.get('tab', '') or IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TAB)!r}",
    ]
    poll_lines = _izom_propui_free_portable_direct_poll_lines(panel)
    if poll_lines:
        lines.append("")
        lines.extend(poll_lines)
    lines.extend([
        "",
        "    def draw(self, context):",
        f"        {draw_fn}(context, self.layout)",
    ])
    return "\n".join(lines)


def _izom_propui_free_portable_direct_register_section(class_names):
    class_list = "[" + ", ".join(class_names) + "]"
    lines = [
        "@persistent",
        "def _izom_propui_free_generated_load_pre(_dummy):",
        "    try:",
        "        unregister()",
        "    except (RuntimeError, ValueError, TypeError, AttributeError, SyntaxError, ReferenceError, LookupError, OSError, ImportError) as exc:",
        "        print(f'[izom PropUI Free][WARNING][Generated UI] Could not clean generated UI before loading a new file: {exc}')",
        "",
        "",
        "def unregister():",
        "    old_lifecycle_handlers = list(bpy.app.driver_namespace.get(_REGISTRY_KEY + ':lifecycle_handlers', []) or [])",
        "    for lifecycle_item in old_lifecycle_handlers:",
        "        if not (isinstance(lifecycle_item, tuple) and len(lifecycle_item) == 2 and callable(lifecycle_item[1])):",
        "            print(f'[izom PropUI Free][WARNING][Generated UI] Ignoring unexpected lifecycle handler item {lifecycle_item!r}')",
        "            continue",
        "        handler_name, handler = lifecycle_item",
        "        handlers = getattr(bpy.app.handlers, str(handler_name or ''), None)",
        "        if handlers is not None and handler in handlers:",
        "            try:",
        "                handlers.remove(handler)",
        "            except (RuntimeError, ValueError, TypeError, AttributeError, SyntaxError, ReferenceError, LookupError, OSError, ImportError) as exc:",
        "                print(f'[izom PropUI Free][WARNING][Generated UI] Could not remove lifecycle handler {handler_name}: {exc}')",
        "    bpy.app.driver_namespace[_REGISTRY_KEY + ':lifecycle_handlers'] = []",
        "    old_registry_items = list(bpy.app.driver_namespace.get(_REGISTRY_KEY, []) or [])",
        "    old_classes = [item for item in old_registry_items if isinstance(item, type)]",
        "    for cls in reversed(old_classes):",
        "        try:",
        "            bpy.utils.unregister_class(cls)",
        "        except (RuntimeError, ValueError, TypeError, AttributeError, SyntaxError, ReferenceError, LookupError, OSError, ImportError) as exc:",
        "            print(f'[izom PropUI Free][WARNING][Generated UI] Could not unregister {getattr(cls, \"__name__\", cls)}: {exc}')",
        "    bpy.app.driver_namespace[_REGISTRY_KEY] = []",
        "",
        "",
        "def register():",
        "    unregister()",
        "    registered = []",
        "    try:",
        f"        for cls in {class_list}:",
        "            bpy.utils.register_class(cls)",
        "            registered.append(cls)",
        "    except (RuntimeError, ValueError, TypeError, AttributeError, SyntaxError, ReferenceError, LookupError, OSError, ImportError) as exc:",
        "        print(f'[izom PropUI Free][ERROR][Generated UI] Could not register {getattr(cls, \"__name__\", cls)}: {exc}')",
        "        for old_cls in reversed(registered):",
        "            try:",
        "                bpy.utils.unregister_class(old_cls)",
        "            except (RuntimeError, ValueError, TypeError, AttributeError, SyntaxError, ReferenceError, LookupError, OSError, ImportError) as cleanup_exc:",
        "                print(f'[izom PropUI Free][WARNING][Generated UI] Could not roll back {getattr(old_cls, \"__name__\", old_cls)}: {cleanup_exc}')",
        "        bpy.app.driver_namespace[_REGISTRY_KEY] = []",
        "        raise",
        "    bpy.app.driver_namespace[_REGISTRY_KEY] = registered",
        "    lifecycle_handlers = []",
        "    try:",
        "        load_pre_handlers = bpy.app.handlers.load_pre",
        "        if _izom_propui_free_generated_load_pre not in load_pre_handlers:",
        "            load_pre_handlers.append(_izom_propui_free_generated_load_pre)",
        "        lifecycle_handlers.append(('load_pre', _izom_propui_free_generated_load_pre))",
        "    except (RuntimeError, ValueError, TypeError, AttributeError, SyntaxError, ReferenceError, LookupError, OSError, ImportError) as exc:",
        "        print(f'[izom PropUI Free][WARNING][Generated UI] Could not register generated UI file-load cleanup: {exc}')",
        "    bpy.app.driver_namespace[_REGISTRY_KEY + ':lifecycle_handlers'] = lifecycle_handlers",
        "",
        "",
        "register()",
    ]
    return "\n".join(lines)

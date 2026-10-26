# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
import hashlib

from ..core.diagnostics import izom_propui_free_log_recovered
import bpy

from bpy.types import Panel, PropertyGroup

from ..core.context import izom_propui_free_context_params
from ..core.diagnostics import izom_propui_free_log_warning
from .common import IZOM_PROPUI_FREE_AnnotatedPropertyTarget
from .editor_sections import (
    izom_propui_free_editor_section_is_visible,
    izom_propui_free_normalize_editor_section_key,
    izom_propui_free_ordered_editor_section_specs,
)
from .panel_parameters import (
    IzomPropUIPanelParametersMixin,
)
from .lifecycle import (
    izom_propui_free_editor_panel_class_registry,
    izom_propui_free_register_lifecycle_timer,
    izom_propui_free_unregister_lifecycle_timer,
)

_IZOM_PROPUI_FREE_EDITOR_PANEL_CLASSES = izom_propui_free_editor_panel_class_registry()
_IZOM_PROPUI_FREE_EDITOR_PANEL_REFRESH_PENDING = False
_IZOM_PROPUI_FREE_EDITOR_PANEL_REFRESH_CALLBACK = None
_IZOM_PROPUI_FREE_EDITOR_PANEL_REVISION = 0
_IZOM_PROPUI_FREE_BLENDER_CLASS_NAME_MAX = 64
_IZOM_PROPUI_FREE_EDITOR_PANEL_REFRESH_TIMER_NAME = 'editor_panel_refresh'
_IZOM_PROPUI_FREE_DYNAMIC_EDITOR_PANEL_ATTR = '_izom_propui_free_dynamic_editor_panel'
_IZOM_PROPUI_FREE_EDITOR_SECTION_TOKENS = {
    'DIAGNOSTICS': 'diag',
    'OUTPUT_SETUP': 'out',
    'ENTRY_LIST': 'entries',
    'SELECTED_ENTRY': 'selected',
    'GENERATED_LAYOUT': 'layout',
    'EDITOR_SETTINGS': 'settings',
}

class IZOM_PROPUI_FREE_Settings(PropertyGroup):
    """Scene-level storage for one standalone PropUI project."""

_izom_propui_free_settings_target = IZOM_PROPUI_FREE_AnnotatedPropertyTarget(IZOM_PROPUI_FREE_Settings)
IzomPropUIPanelParametersMixin.add_parameters(_izom_propui_free_settings_target)
_izom_propui_free_settings_target.apply()
del _izom_propui_free_settings_target

def _izom_propui_free_editor_panel_enabled(*, location, key):
    return str(location or '').strip().upper() == 'SIDEBAR' and str(key or '').strip().upper() == 'VIEW_3D'

def _izom_propui_free_editor_mute_message(context):
    return None

def _izom_propui_free_editor_params_for_draw(layout, context):
    scene = getattr(context, 'scene', None)
    params = izom_propui_free_context_params(context)
    if params is None:
        box = layout.box()
        box.alert = True
        box.label(text="PropUI scene settings are unavailable.", icon='ERROR')
        return None
    return params

def _izom_propui_free_editor_section_poll(*, location, key, section_key, context):
    if not _izom_propui_free_editor_panel_enabled(location=location, key=key):
        return False
    if _izom_propui_free_editor_mute_message(context) is not None:
        return False
    params = izom_propui_free_context_params(context)
    if params is None or not hasattr(params, 'izom_propui_free_entries'):
        return False
    return izom_propui_free_editor_section_is_visible(params, section_key)

def _izom_propui_free_draw_editor_root_panel(layout, context):
    mute_message = _izom_propui_free_editor_mute_message(context)
    if mute_message is not None:
        text, icon = mute_message
        layout.label(text=text, icon=icon)
        return
    params = _izom_propui_free_editor_params_for_draw(layout, context)
    if params is None:
        return
    box = layout.box()
    col = box.column(align=True)
    col.label(text="izom PropUI Free includes the core panel builder.", icon='INFO')
    col.label(text="Unlock the full addon for advanced entry types, layouts, variants, shortcuts, and generated UI management.")
    op = col.operator("wm.url_open", text="View Full Addon", icon='URL')
    op.url = "https://propui.bigizom.com"

def _izom_propui_free_draw_editor_section_panel(layout, context, section_key):
    mute_message = _izom_propui_free_editor_mute_message(context)
    if mute_message is not None:
        text, icon = mute_message
        layout.label(text=text, icon=icon)
        return
    params = _izom_propui_free_editor_params_for_draw(layout, context)
    if params is None:
        return
    normalized_section_key = izom_propui_free_normalize_editor_section_key(section_key)
    if normalized_section_key:
        IzomPropUIPanelParametersMixin.draw_editor_section_ui(layout, params, normalized_section_key)

class IZOM_PROPUI_FREE_PT_editor(Panel):
    bl_idname = "IZOM_PROPUI_FREE_PT_editor"
    bl_label = "PropUI Editor Free"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PropUI Free"

    @classmethod
    def poll(cls, _context):
        return _izom_propui_free_editor_panel_enabled(location='SIDEBAR', key='VIEW_3D')

    def draw(self, context):
        _izom_propui_free_draw_editor_root_panel(self.layout, context)

def _izom_propui_free_panel_slug(value, *, default='panel'):
    slug = ''.join(
        char.lower() if char.isalnum() else '_'
        for char in str(value or '').strip().lower()
    ).strip('_')
    while '__' in slug:
        slug = slug.replace('__', '_')
    return slug or str(default or 'panel')

def _izom_propui_free_short_panel_token(value, *, max_chars, default='panel'):
    max_chars = max(1, int(max_chars))
    slug = _izom_propui_free_panel_slug(value, default=default)
    if len(slug) <= max_chars:
        return slug
    digest = hashlib.blake2s(slug.encode('utf-8'), digest_size=3).hexdigest()
    if max_chars <= len(digest):
        return digest[:max_chars]
    prefix_len = max_chars - len(digest) - 1
    prefix = slug[:prefix_len].rstrip('_') or slug[:prefix_len] or str(default or 'p')[:1]
    return f"{prefix}_{digest}"[:max_chars]

def _izom_propui_free_editor_section_panel_class_name(parent_class_name, section_key):
    normalized_section_key = izom_propui_free_normalize_editor_section_key(section_key)
    section_token = _IZOM_PROPUI_FREE_EDITOR_SECTION_TOKENS.get(
        normalized_section_key,
        _izom_propui_free_short_panel_token(normalized_section_key, max_chars=16, default='section'),
    )
    parent_token = _izom_propui_free_short_panel_token(parent_class_name, max_chars=20, default='parent')
    class_name = f"IZOM_PROPUI_FREE_PT_es_{parent_token}_{section_token}"
    if _IZOM_PROPUI_FREE_EDITOR_PANEL_REVISION > 0:
        class_name = f"{class_name}_r{_IZOM_PROPUI_FREE_EDITOR_PANEL_REVISION}"
    if len(class_name) > _IZOM_PROPUI_FREE_BLENDER_CLASS_NAME_MAX:
        revision_suffix = f"_r{_IZOM_PROPUI_FREE_EDITOR_PANEL_REVISION}" if _IZOM_PROPUI_FREE_EDITOR_PANEL_REVISION > 0 else ''
        available = _IZOM_PROPUI_FREE_BLENDER_CLASS_NAME_MAX - len("IZOM_PROPUI_FREE_PT_es__") - len(section_token) - len(revision_suffix)
        parent_token = _izom_propui_free_short_panel_token(parent_class_name, max_chars=max(1, available), default='parent')
        class_name = f"IZOM_PROPUI_FREE_PT_es_{parent_token}_{section_token}{revision_suffix}"
    return class_name

def _izom_propui_free_bump_editor_panel_revision():
    global _IZOM_PROPUI_FREE_EDITOR_PANEL_REVISION

    _IZOM_PROPUI_FREE_EDITOR_PANEL_REVISION = (_IZOM_PROPUI_FREE_EDITOR_PANEL_REVISION + 1) % 100000
    if _IZOM_PROPUI_FREE_EDITOR_PANEL_REVISION <= 0:
        _IZOM_PROPUI_FREE_EDITOR_PANEL_REVISION = 1

def _izom_propui_free_make_editor_section_panel_class(location, key, parent_class_name, section_spec):
    location_key = 'SIDEBAR'
    target_key = 'VIEW_3D'
    section_key = str(section_spec.get('key', '') or '').strip().upper()
    class_name = _izom_propui_free_editor_section_panel_class_name(parent_class_name, section_key)

    def poll(_cls, context):
        return _izom_propui_free_editor_section_poll(
            location=location_key,
            key=target_key,
            section_key=section_key,
            context=context,
        )

    def draw(self, context):
        _izom_propui_free_draw_editor_section_panel(self.layout, context, section_key)

    attrs = {
        'bl_idname': class_name,
        'bl_label': str(section_spec.get('label', '') or 'Section'),
        'bl_parent_id': parent_class_name,
        'bl_order': int(section_spec.get('order', 0) or 0),
        'poll': classmethod(poll),
        'draw': draw,
        'bl_space_type': 'VIEW_3D',
        'bl_region_type': 'UI',
        _IZOM_PROPUI_FREE_DYNAMIC_EDITOR_PANEL_ATTR: True,
    }
    return type(class_name, (bpy.types.Panel,), attrs)

def unregister_editor_panels():
    _izom_propui_free_cancel_editor_panel_refresh_timer()
    stable_registry = izom_propui_free_editor_panel_class_registry()
    candidates = dict(stable_registry)
    candidates.update(_IZOM_PROPUI_FREE_EDITOR_PANEL_CLASSES)
    remaining = dict(candidates)
    for pass_index in range(2):
        if not remaining:
            break
        failed = {}
        for class_name, panel_class in reversed(list(remaining.items())):
            registered_class = getattr(bpy.types, class_name, None)
            if registered_class is None:
                continue
            if bool(getattr(registered_class, _IZOM_PROPUI_FREE_DYNAMIC_EDITOR_PANEL_ATTR, False)):
                panel_class = registered_class
            try:
                bpy.utils.unregister_class(panel_class)
            except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                failed[class_name] = panel_class
                if pass_index > 0:
                    izom_propui_free_log_warning(
                        f"Could not unregister editor panel {getattr(panel_class, '__name__', panel_class)}",
                        category='Registration',
                        exception=exc,
                    )
        remaining = failed
    _IZOM_PROPUI_FREE_EDITOR_PANEL_CLASSES.clear()
    _IZOM_PROPUI_FREE_EDITOR_PANEL_CLASSES.update(remaining)
    stable_registry.clear()
    stable_registry.update(remaining)
    return not remaining

def _izom_propui_free_reregister_static_editor_parent_panels():
    if getattr(bpy.types, IZOM_PROPUI_FREE_PT_editor.__name__, None) is None:
        return False
    try:
        bpy.utils.unregister_class(IZOM_PROPUI_FREE_PT_editor)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_warning(
            "Could not unregister the PropUI editor parent panel during refresh",
            category='Registration',
            exception=exc,
        )
        return False
    try:
        bpy.utils.register_class(IZOM_PROPUI_FREE_PT_editor)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_warning(
            "Could not re-register the PropUI editor parent panel during refresh",
            category='Registration',
            exception=exc,
        )
        return False
    return True

def _izom_propui_free_tag_editor_panel_redraw(context=None):
    seen_areas = set()

    def tag_area(area):
        if area is None:
            return
        try:
            area_key = int(area.as_pointer())
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS:
            area_key = id(area)
        if area_key in seen_areas:
            return
        seen_areas.add(area_key)
        try:
            if hasattr(area, 'tag_redraw'):
                area.tag_redraw()
            for region in getattr(area, 'regions', []) or []:
                if hasattr(region, 'tag_redraw'):
                    region.tag_redraw()
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )

    tag_area(getattr(context, 'area', None) if context is not None else None)
    try:
        window_manager = getattr(bpy.context, 'window_manager', None)
        for window in getattr(window_manager, 'windows', []) or []:
            screen = getattr(window, 'screen', None)
            for area in getattr(screen, 'areas', []) or []:
                tag_area(area)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )

def _izom_propui_free_register_editor_panel_class(panel_class, *, label):
    try:
        bpy.utils.register_class(panel_class)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_warning(
            f"Could not register {label}",
            category='Registration',
            exception=exc,
        )
        return False
    _IZOM_PROPUI_FREE_EDITOR_PANEL_CLASSES[panel_class.__name__] = panel_class
    return True

def _izom_propui_free_register_editor_section_panels(location, key, parent_class_name):
    params = izom_propui_free_context_params(bpy.context)
    for section_order, section_spec in enumerate(izom_propui_free_ordered_editor_section_specs(params)):
        panel_spec = dict(section_spec, order=section_order)
        panel_class = _izom_propui_free_make_editor_section_panel_class(
            location,
            key,
            parent_class_name,
            panel_spec,
        )
        _izom_propui_free_register_editor_panel_class(
            panel_class,
            label=f"editor section {panel_spec.get('key', '')} for {location}:{key}",
        )

def register_editor_panels(*, refresh_static_parents=False):
    if not unregister_editor_panels():
        raise RuntimeError('Could not remove stale PropUI Free editor panels')
    if refresh_static_parents:
        _izom_propui_free_reregister_static_editor_parent_panels()
    _izom_propui_free_register_editor_section_panels(
        'SIDEBAR',
        'VIEW_3D',
        IZOM_PROPUI_FREE_PT_editor.__name__,
    )

def refresh_editor_panels(context=None):
    _izom_propui_free_bump_editor_panel_revision()
    register_editor_panels(refresh_static_parents=True)
    _izom_propui_free_tag_editor_panel_redraw(context)

def _izom_propui_free_cancel_editor_panel_refresh_timer():
    global _IZOM_PROPUI_FREE_EDITOR_PANEL_REFRESH_PENDING, _IZOM_PROPUI_FREE_EDITOR_PANEL_REFRESH_CALLBACK

    callback = _IZOM_PROPUI_FREE_EDITOR_PANEL_REFRESH_CALLBACK
    _IZOM_PROPUI_FREE_EDITOR_PANEL_REFRESH_PENDING = False
    _IZOM_PROPUI_FREE_EDITOR_PANEL_REFRESH_CALLBACK = None
    izom_propui_free_unregister_lifecycle_timer(
        _IZOM_PROPUI_FREE_EDITOR_PANEL_REFRESH_TIMER_NAME,
        callback,
    )

def schedule_editor_panels_refresh():
    global _IZOM_PROPUI_FREE_EDITOR_PANEL_REFRESH_PENDING, _IZOM_PROPUI_FREE_EDITOR_PANEL_REFRESH_CALLBACK

    if _IZOM_PROPUI_FREE_EDITOR_PANEL_REFRESH_PENDING:
        return True
    _IZOM_PROPUI_FREE_EDITOR_PANEL_REFRESH_PENDING = True

    def _refresh_later():
        global _IZOM_PROPUI_FREE_EDITOR_PANEL_REFRESH_PENDING, _IZOM_PROPUI_FREE_EDITOR_PANEL_REFRESH_CALLBACK

        _IZOM_PROPUI_FREE_EDITOR_PANEL_REFRESH_PENDING = False
        _IZOM_PROPUI_FREE_EDITOR_PANEL_REFRESH_CALLBACK = None
        try:
            refresh_editor_panels()
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_warning(
                "Could not refresh PropUI editor panels after the UI event completed",
                category='UI',
                exception=exc,
            )
        return None

    try:
        _IZOM_PROPUI_FREE_EDITOR_PANEL_REFRESH_CALLBACK = _refresh_later
        if not izom_propui_free_register_lifecycle_timer(
            _IZOM_PROPUI_FREE_EDITOR_PANEL_REFRESH_TIMER_NAME,
            _refresh_later,
            first_interval=0.0,
        ):
            raise RuntimeError('PropUI Free lifecycle is not active')
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        _IZOM_PROPUI_FREE_EDITOR_PANEL_REFRESH_PENDING = False
        _IZOM_PROPUI_FREE_EDITOR_PANEL_REFRESH_CALLBACK = None
        izom_propui_free_log_warning(
            "Could not schedule PropUI editor panel refresh",
            category='UI',
            exception=exc,
        )
        return False
    return True


CLASSES = (
    IZOM_PROPUI_FREE_Settings,
    IZOM_PROPUI_FREE_PT_editor,
)

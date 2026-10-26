# SPDX-License-Identifier: GPL-3.0-or-later

from .generated_registry_unregister import (
    _izom_propui_free_portable_registry_class_count,
    _izom_propui_free_running_portable_registry_keys,
    _izom_propui_free_unregister_portable_registry_key,
    bpy,
    izom_propui_free_invalidate_generated_lifecycle_status_cache,
    izom_propui_free_log_warning,
)
from ..core.diagnostics import (
    IZOM_PROPUI_FREE_RECOVERABLE_ERRORS,
    izom_propui_free_log_error,
    izom_propui_free_log_recovered,
)
from .generated_naming import (
    _izom_propui_free_generated_registry_key_for_slot,
    _izom_propui_free_generated_script_name_for_slot,
)
from .generated_registry_common import (
    _izom_propui_free_is_portable_registry_key,
    _izom_propui_free_portable_module_name,
)
from .generated_registry_text import (
    _izom_propui_free_is_portable_generated_text,
    _izom_propui_free_mark_text_registry_key,
)
from .generated_state import (
    _izom_propui_free_data_collection,
)


def _izom_propui_free_portable_script_slots():
    from .generated_portable_slots import _izom_propui_free_portable_script_slots as portable_script_slots

    return portable_script_slots()


def _izom_propui_free_build_portable_generated_script(*args, **kwargs):
    from .generated_portable_builder import (
        _izom_propui_free_build_portable_generated_script as build_portable_generated_script,
    )

    return build_portable_generated_script(*args, **kwargs)


def _izom_propui_free_cleanup_obsolete_portable_scripts(texts, desired_text_names, desired_registry_keys):
    desired_names = {str(name or '').strip() for name in desired_text_names or [] if str(name or '').strip()}
    desired_keys = {str(key or '').strip() for key in desired_registry_keys or [] if str(key or '').strip()}
    try:
        namespace_keys = list(bpy.app.driver_namespace.keys())
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        namespace_keys = []
    cleaned_keys = set()
    for key in namespace_keys:
        key_text = str(key or '').strip()
        if key_text.endswith(':lifecycle_handlers'):
            suffix = ':lifecycle_handlers'
            base_key = key_text[:-len(suffix)]
            if (
                _izom_propui_free_is_portable_registry_key(base_key)
                and base_key not in desired_keys
                and base_key not in cleaned_keys
            ):
                cleaned_keys.add(base_key)
                _izom_propui_free_unregister_portable_registry_key(base_key, remove_namespace_key=True)
            continue
        if not _izom_propui_free_is_portable_registry_key(key_text):
            continue
        if key_text not in desired_keys and key_text not in cleaned_keys:
            cleaned_keys.add(key_text)
            _izom_propui_free_unregister_portable_registry_key(key_text, remove_namespace_key=True)
    if texts is None:
        return
    for text in list(texts):
        name = str(getattr(text, 'name', '') or '').strip()
        if name in desired_names:
            continue
        if _izom_propui_free_is_portable_generated_text(text):
            try:
                texts.remove(text)
                izom_propui_free_invalidate_generated_lifecycle_status_cache()
            except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                izom_propui_free_log_warning(
                    f"Could not remove obsolete generated script {name}",
                    category='Generated UI',
                    exception=exc,
                )


def _izom_propui_free_write_text_and_register(texts, text_name, source, registry_key):
    if texts is None:
        return False
    text = texts.get(text_name)
    source_matches = False
    if text is None:
        text = texts.new(text_name)
        izom_propui_free_invalidate_generated_lifecycle_status_cache()
    else:
        try:
            source_matches = str(text.as_string() or '') == str(source or '')
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_warning(
                f"Could not read generated UI Text datablock {text_name}",
                category='Generated UI',
                exception=exc,
            )
    try:
        namespace = bpy.app.driver_namespace
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(category='Generated UI', exception=exc)
        namespace = {}
    if source_matches and _izom_propui_free_portable_registry_class_count(namespace, registry_key) > 0:
        _izom_propui_free_mark_text_registry_key(text, registry_key)
        return True
    source_ready = bool(source_matches)
    if not source_matches:
        try:
            text.clear()
            text.write(source)
            text.use_module = True
            source_ready = True
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_warning(
                f"Could not write generated UI Text datablock {text_name}",
                category='Generated UI',
                exception=exc,
            )
    else:
        try:
            text.use_module = True
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(category='Generated UI', exception=exc)
    if source_ready:
        _izom_propui_free_mark_text_registry_key(text, registry_key)
    try:
        # SECURITY: source is persisted in the .blend. Automatic history
        # restoration checks Blender's auto-execution result and registered
        # Text before reaching this exec; Generate is an explicit user action.
        exec(  # noqa: S102
            compile(source, text_name, 'exec'),
            {'__name__': _izom_propui_free_portable_module_name(text_name), '__builtins__': __builtins__},
        )
        izom_propui_free_invalidate_generated_lifecycle_status_cache()
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_error(
            f"Could not register generated UI Text script {text_name}",
            category='Generated UI',
            exception=exc,
        )
        _izom_propui_free_unregister_portable_registry_key(registry_key)
        return False
    return True


def _izom_propui_free_portable_generated_script_sources(slots=None):
    if slots is None:
        slots = _izom_propui_free_portable_script_slots()

    sources = []
    for slot in slots:
        item = dict(slot or {})
        text_name = str(item.get('script_name', '') or '').strip() or _izom_propui_free_generated_script_name_for_slot(item)
        registry_key = _izom_propui_free_generated_registry_key_for_slot(item)
        sources.append((
            text_name,
            _izom_propui_free_build_portable_generated_script([item], registry_key=registry_key),
            registry_key,
        ))
    return sources


def _izom_propui_free_write_and_register_portable_generated_script(*, cleanup=True, registered_only=False):
    texts = _izom_propui_free_data_collection('texts')
    if texts is None:
        return False

    script_sources = _izom_propui_free_portable_generated_script_sources()
    desired_text_names = []
    desired_registry_keys = []
    for text_name, _source, registry_key in script_sources:
        desired_text_names.append(str(text_name or '').strip())
        desired_registry_keys.append(str(registry_key or '').strip())

    if cleanup:
        _izom_propui_free_cleanup_obsolete_portable_scripts(texts, desired_text_names, desired_registry_keys)

    ok = True
    for text_name, source, registry_key in script_sources:
        if registered_only:
            text = texts.get(text_name)
            if text is None or not text.use_module:
                continue
        ok = _izom_propui_free_write_text_and_register(
            texts,
            text_name,
            source,
            registry_key,
        ) and ok
    return ok


def restore_generated_panel_from_scenes(*, cleanup=False, registered_only=False):
    scenes = _izom_propui_free_data_collection('scenes')
    if scenes is None:
        return False
    return _izom_propui_free_write_and_register_portable_generated_script(
        cleanup=cleanup, registered_only=registered_only,
    )

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), extra=('restore_generated_panel_from_scenes',))

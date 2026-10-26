# SPDX-License-Identifier: GPL-3.0-or-later

from .generated_state import (
    IZOM_PROPUI_FREE_GENERATED_SCRIPT_PER_UI_PREFIX,
    IZOM_PROPUI_FREE_GENERATED_SCRIPT_REGISTRY_KEY,
    IZOM_PROPUI_FREE_GENERATED_SCRIPT_REGISTRY_PREFIX,
)
from .generated_branding import (
    izom_propui_free_is_branded_panel_class_name,
    izom_propui_free_is_branded_registry_key,
)
from .generated_naming import _izom_propui_free_slug

_IZOM_PROPUI_FREE_GENERATED_LIFECYCLE_STATUS_CACHE = {}
_IZOM_PROPUI_FREE_GENERATED_LIFECYCLE_STATUS_SIGNATURES = {}
_IZOM_PROPUI_FREE_GENERATED_LIFECYCLE_STATUS_CHECK_TIMES = {}
_IZOM_PROPUI_FREE_TEXT_REGISTRY_KEY_PROP = "izom_propui_free_generated_registry_key"
_IZOM_PROPUI_FREE_GENERATED_LIFECYCLE_FAST_CHECK_INTERVAL = 0.25


def _izom_propui_free_portable_module_name(text_name):
    name = str(text_name or '').strip()
    if name.endswith('.py'):
        name = name[:-3]
    return _izom_propui_free_slug(name, fallback='izom_propui_free_generated_ui')


def _izom_propui_free_is_managed_portable_text_name(name):
    text_name = str(name or '').strip()
    return text_name.startswith(IZOM_PROPUI_FREE_GENERATED_SCRIPT_PER_UI_PREFIX) and text_name.endswith('.py')


def _izom_propui_free_is_portable_registry_key(registry_key):
    key_text = str(registry_key or '').strip()
    if not key_text or key_text.endswith(':lifecycle_handlers'):
        return False
    if key_text == IZOM_PROPUI_FREE_GENERATED_SCRIPT_REGISTRY_KEY or key_text.startswith(
        IZOM_PROPUI_FREE_GENERATED_SCRIPT_REGISTRY_PREFIX
    ):
        return True
    return izom_propui_free_is_branded_registry_key(key_text)


def _izom_propui_free_is_generated_panel_class_name(name):
    name_text = str(name or '').strip()
    prefix = 'IZOM_PROPUI_FREE_PT_'
    if not name_text.startswith(prefix):
        return izom_propui_free_is_branded_panel_class_name(name_text)
    suffix = name_text[len(prefix):]
    return len(suffix) == 16 and all(char in '0123456789abcdef' for char in suffix)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

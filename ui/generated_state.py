# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
import hashlib

import bpy

from ..core.diagnostics import izom_propui_free_log_recovered

IZOM_PROPUI_FREE_BLENDER_IDENTIFIER_LIMIT = 63
IZOM_PROPUI_FREE_GENERATED_SCRIPT_NAME_LIMIT = 80
IZOM_PROPUI_FREE_GENERATED_SCRIPT_REGISTRY_KEY = "izom_propui_free_generated_panel_classes"
IZOM_PROPUI_FREE_GENERATED_SCRIPT_PER_UI_PREFIX = "izom_propui_free_generated_ui_"
IZOM_PROPUI_FREE_GENERATED_SCRIPT_REGISTRY_PREFIX = "izom_propui_free_generated_panel_classes:"
def _izom_propui_free_data_collection(name):
    try:
        return getattr(bpy.data, name)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        return None

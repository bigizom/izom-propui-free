# SPDX-License-Identifier: GPL-3.0-or-later

import json

from rna_prop_ui import rna_idprop_quote_path

from ..core.constants import (
    IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT,
)


def izom_propui_free_entry_slider_control_available(entry, value_kind, *, uses_component_draw_mode=False):
    return str(value_kind or '').strip().upper() in {'FLOAT', 'VECTOR', 'COLOR'}



from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

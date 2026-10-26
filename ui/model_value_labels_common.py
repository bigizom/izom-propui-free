# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.props import (
    BoolProperty,
    BoolVectorProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    IntVectorProperty,
    StringProperty,
)
from bpy.types import PropertyGroup

from ..core.diagnostics import izom_propui_free_log_recovered
from ..core.context import izom_propui_free_context_params
from ..core.constants import (
    IZOM_PROPUI_FREE_ARRAY_SIZE_MAX,
    IZOM_PROPUI_FREE_MAX_LABEL_INPUT_TEXT,
    IZOM_PROPUI_FREE_OTHER_LABEL_RULE_KIND_ITEMS,
    IZOM_PROPUI_FREE_RULE_SOURCE_BOOL_STATE_ITEMS,
    IZOM_PROPUI_FREE_VALUE_LABEL_MATCH_MODE_ITEMS,
)
from .helpers import (
    _izom_propui_free_bulk_entry_updates_suspended,
    _izom_propui_free_target_value_float_updated,
    _izom_propui_free_target_value_int_updated,
    _izom_propui_free_value_label_array_value_updated,
    _izom_propui_free_value_float_updated,
    _izom_propui_free_value_int_updated,
    _izom_propui_free_value_label_rule_state_updated,
    _izom_propui_free_value_label_updated,
)
from .model_proxies import (
    _izom_propui_free_add_array_component_proxy_properties,
    _izom_propui_free_add_editor_float_proxy_properties,
    _izom_propui_free_add_float_array_proxy_properties,
    _izom_propui_free_direct_float_array_color_property,
)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

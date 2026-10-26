# SPDX-License-Identifier: GPL-3.0-or-later

import bpy

from .confirmations import (
    IZOM_PROPUI_FREE_CONFIRM_ACTION_ITEMS,
    IZOM_PROPUI_FREE_CONFIRM_GENERATE_CURRENT_ITEMS,
    IZOM_PROPUI_FREE_CONFIRM_GENERATE_EMPTY_LAYOUT_ITEMS,
    IZOM_PROPUI_FREE_CONFIRM_GENERATE_NATIVE_CONFLICT_ITEMS,
    IZOM_PROPUI_FREE_CONFIRM_PARENT_DELETE_ITEMS,
)


def _izom_propui_free_confirmation_action_property(name, description):
    return bpy.props.EnumProperty(
        name=name,
        description=description,
        items=IZOM_PROPUI_FREE_CONFIRM_ACTION_ITEMS,
        default='ASK',
    )


def _izom_propui_free_add_confirmation_properties(params):
    params.izom_propui_free_confirmation_clear_entry_list = _izom_propui_free_confirmation_action_property(
        "Clear Entry List",
        "Default answer when clearing every Entry List entry",
    )
    params.izom_propui_free_confirmation_full_factory_reset = _izom_propui_free_confirmation_action_property(
        "Full Factory Reset",
        "Default answer when wiping PropUI editor data from every scene and deleting saved defaults",
    )
    params.izom_propui_free_confirmation_clear_generated_layout = _izom_propui_free_confirmation_action_property(
        "Clear Generated Layout",
        "Default answer when clearing every Generated Layout entry",
    )
    params.izom_propui_free_confirmation_clear_dynamic_labels = _izom_propui_free_confirmation_action_property(
        "Clear Dynamic Labels",
        "Default answer when clearing a Dynamic Labels list",
    )
    params.izom_propui_free_confirmation_generate_current_conflict = bpy.props.EnumProperty(
        name="Generate Current Conflict",
        description="Default answer when Generate Current would replace an existing current generated UI",
        items=IZOM_PROPUI_FREE_CONFIRM_GENERATE_CURRENT_ITEMS,
        default='ASK',
    )
    params.izom_propui_free_confirmation_generate_native_conflict = bpy.props.EnumProperty(
        name="Generate Native Conflict",
        description="Default answer when Generate preserves storage and managed Property IDs collide with existing native custom properties",
        items=IZOM_PROPUI_FREE_CONFIRM_GENERATE_NATIVE_CONFLICT_ITEMS,
        default='ASK',
    )
    params.izom_propui_free_confirmation_parent_delete = bpy.props.EnumProperty(
        name="Parent Delete",
        description="Default answer when deleting a parent entry that has children",
        items=IZOM_PROPUI_FREE_CONFIRM_PARENT_DELETE_ITEMS,
        default='ASK',
    )
    params.izom_propui_free_confirmation_generate_empty_layout = bpy.props.EnumProperty(
        name="Generate With Empty Layout",
        description="Default answer when Generate runs but no entries are placed in the Generated Layout",
        items=IZOM_PROPUI_FREE_CONFIRM_GENERATE_EMPTY_LAYOUT_ITEMS,
        default='ASK',
    )

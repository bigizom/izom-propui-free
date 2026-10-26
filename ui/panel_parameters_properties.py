# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from ..core.diagnostics import izom_propui_free_log_recovered
import bpy

from ..core.constants import (
    IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TAB,
    IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TITLE,
)
from ..core.editor_state_schema import (
    IZOM_PROPUI_FREE_EDITOR_EXPANDED_DEFAULT,
    IZOM_PROPUI_FREE_EDITOR_EXPANDED_PROPERTY_SPECS,
    IZOM_PROPUI_FREE_EDITOR_HIDE_DEFAULT,
    IZOM_PROPUI_FREE_EDITOR_HIDE_PROPERTY_SPECS,
    IZOM_PROPUI_FREE_EDITOR_ONLY_BOOL_PROPERTY_SPECS,
    IZOM_PROPUI_FREE_PROJECT_EDITOR_BOOL_PROPERTY_SPECS,
    IZOM_PROPUI_FREE_PROJECT_EDITOR_MISC_PROPERTY_SPECS,
)
from ..core.targets import izom_propui_free_sync_owner_path_from_picker
from .helpers import (
    _izom_propui_free_active_index_updated,
    _izom_propui_free_editor_float_decimals_updated,
    _izom_propui_free_layout_active_index_updated,
    _izom_propui_free_layout_view_active_index_updated,
    _izom_propui_free_params_state_updated,
)
from .models import (
    IZOM_PROPUI_FREE_LayoutItem,
    IZOM_PROPUI_FREE_LayoutRow,
    IZOM_PROPUI_FREE_LayoutViewItem,
    IZOM_PROPUI_FREE_PropertyEntry,
)
from .panel_parameters_confirmations import _izom_propui_free_add_confirmation_properties
from .editor_session import (
    izom_propui_free_session_bool_property,
    izom_propui_free_session_enum_property,
    izom_propui_free_session_int_property,
    izom_propui_free_session_string_property,
)


_IZOM_PROPUI_FREE_ENTRY_LIST_PRIMARY_COLUMN_ITEMS = (
    ('NAME', 'Name', 'Use the wide leading Entry List column for the entry label'),
    ('PROP_ID', 'Property ID', 'Use the wide leading Entry List column for the Property ID instead of the label'),
)

def _izom_propui_free_default_target_picker_updated(params, context):
    try:
        izom_propui_free_sync_owner_path_from_picker(
            params,
            'izom_propui_free_default_target',
            'izom_propui_free_default_target_owner_path',
            context=context,
        )
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
    _izom_propui_free_params_state_updated(params, context)


def _izom_propui_free_add_editor_state_properties(params):
    for field_name, label, description in IZOM_PROPUI_FREE_EDITOR_EXPANDED_PROPERTY_SPECS:
        setattr(
            params,
            field_name,
            izom_propui_free_session_bool_property(
                field_name,
                name=label,
                description=description,
                default=IZOM_PROPUI_FREE_EDITOR_EXPANDED_DEFAULT,
                options={'HIDDEN'},
            ),
        )

    for field_name, kind, label, description, default in IZOM_PROPUI_FREE_PROJECT_EDITOR_MISC_PROPERTY_SPECS:
        property_value = izom_propui_free_session_string_property(
            field_name,
            name=label,
            description=description,
            default=default,
            options={'HIDDEN'},
        )
        setattr(params, field_name, property_value)

    session_bool_fields = {'izom_propui_free_show_entry_tree_hints'}
    for specs in (IZOM_PROPUI_FREE_EDITOR_ONLY_BOOL_PROPERTY_SPECS, IZOM_PROPUI_FREE_PROJECT_EDITOR_BOOL_PROPERTY_SPECS):
        for field_name, label, description, default in specs:
            property_factory = izom_propui_free_session_bool_property if field_name in session_bool_fields else bpy.props.BoolProperty
            property_kwargs = dict(name=label, description=description, default=default)
            if property_factory is izom_propui_free_session_bool_property:
                property_kwargs['field_name'] = field_name
            setattr(
                params,
                field_name,
                property_factory(**property_kwargs),
            )

    for field_name, label, description in IZOM_PROPUI_FREE_EDITOR_HIDE_PROPERTY_SPECS:
        setattr(
            params,
            field_name,
            bpy.props.BoolProperty(
                name=label,
                description=description,
                default=IZOM_PROPUI_FREE_EDITOR_HIDE_DEFAULT,
            ),
        )


def izom_propui_free_add_panel_parameters(params):
    params.izom_propui_free_entries = bpy.props.CollectionProperty(type=IZOM_PROPUI_FREE_PropertyEntry)
    params.izom_propui_free_layout_rows = bpy.props.CollectionProperty(type=IZOM_PROPUI_FREE_LayoutRow)
    params.izom_propui_free_layout_items = bpy.props.CollectionProperty(type=IZOM_PROPUI_FREE_LayoutItem)
    params.izom_propui_free_layout_view_items = bpy.props.CollectionProperty(type=IZOM_PROPUI_FREE_LayoutViewItem)
    params.izom_propui_free_active_index = izom_propui_free_session_int_property('izom_propui_free_active_index', default=0, update=_izom_propui_free_active_index_updated)
    params.izom_propui_free_layout_active_index = izom_propui_free_session_int_property('izom_propui_free_layout_active_index', default=0, update=_izom_propui_free_layout_active_index_updated)
    params.izom_propui_free_layout_view_active_index = izom_propui_free_session_int_property('izom_propui_free_layout_view_active_index', default=0, update=_izom_propui_free_layout_view_active_index_updated)
    params.izom_propui_free_active_uid = izom_propui_free_session_string_property('izom_propui_free_active_uid',
        name="Active Entry UID",
        description="Internal active izom PropUI editor selection",
        default="",
        options={'HIDDEN'},
    )
    params.izom_propui_free_layout_active_uid = izom_propui_free_session_string_property('izom_propui_free_layout_active_uid',
        name="Layout Active Item UID",
        description="Internal active selection for the Generated Layout editor",
        default="",
        options={'HIDDEN'},
    )
    params.izom_propui_free_layout_view_active_uid = izom_propui_free_session_string_property('izom_propui_free_layout_view_active_uid',
        name="Layout View Active Item UID",
        description="Internal active selection for the grouped Generated Layout editor",
        default="",
        options={'HIDDEN'},
    )
    params.izom_propui_free_selected_uids_json = izom_propui_free_session_string_property('izom_propui_free_selected_uids_json',
        name="Selected Entry UIDs",
        description="Internal multi-selection state for the izom PropUI editors",
        default="[]",
        options={'HIDDEN'},
    )
    params.izom_propui_free_layout_selected_uids_json = izom_propui_free_session_string_property('izom_propui_free_layout_selected_uids_json',
        name="Layout Selected Item UIDs",
        description="Internal selection state for the Generated Layout editor",
        default="[]",
        options={'HIDDEN'},
    )
    params.izom_propui_free_layout_view_selected_uids_json = izom_propui_free_session_string_property('izom_propui_free_layout_view_selected_uids_json',
        name="Layout View Selected Item UIDs",
        description="Internal selection state for the grouped Generated Layout editor",
        default="[]",
        options={'HIDDEN'},
    )
    params.izom_propui_free_layout_collapsed_row_uids_json = izom_propui_free_session_string_property('izom_propui_free_layout_collapsed_row_uids_json',
        name="Collapsed Row Group UIDs",
        description="Internal collapsed Row Group state for the Generated Layout editor",
        default="[]",
        options={'HIDDEN'},
    )
    params.izom_propui_free_entry_collapsed_uids_json = izom_propui_free_session_string_property('izom_propui_free_entry_collapsed_uids_json',
        name="Collapsed Entry UIDs",
        description="Internal collapsed parent-entry state for the Entry List editor",
        default="[]",
        options={'HIDDEN'},
    )
    params.izom_propui_free_selection_anchor_uid = izom_propui_free_session_string_property('izom_propui_free_selection_anchor_uid',
        name="Selection Anchor UID",
        description="Internal range-selection anchor for the izom PropUI editors",
        default="",
        options={'HIDDEN'},
    )
    params.izom_propui_free_layout_selection_anchor_uid = izom_propui_free_session_string_property('izom_propui_free_layout_selection_anchor_uid',
        name="Layout Selection Anchor UID",
        description="Internal selection anchor for the Generated Layout editor",
        default="",
        options={'HIDDEN'},
    )
    params.izom_propui_free_layout_view_selection_anchor_uid = izom_propui_free_session_string_property('izom_propui_free_layout_view_selection_anchor_uid',
        name="Layout View Selection Anchor UID",
        description="Internal selection anchor for the grouped Generated Layout editor",
        default="",
        options={'HIDDEN'},
    )
    _izom_propui_free_add_editor_state_properties(params)
    params.izom_propui_free_generated_panel_tab = bpy.props.StringProperty(
        name="Generated Tab",
        description="Sidebar tab/category used when this generated UI appears in editor sidebars",
        default=IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TAB,
        update=_izom_propui_free_params_state_updated,
    )
    params.izom_propui_free_generated_panel_title = bpy.props.StringProperty(
        name="Generated Panel Title",
        description="Title shown on the generated panel",
        default=IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TITLE,
        update=_izom_propui_free_params_state_updated,
    )
    params.izom_propui_free_default_target_owner_path = bpy.props.StringProperty(
        name="Property Storage",
        description="Blender data path to the owner where generated managed custom properties live",
        default="",
        options={'HIDDEN'},
        update=_izom_propui_free_params_state_updated,
    )
    params.izom_propui_free_default_target_object = bpy.props.PointerProperty(
        name="Storage Object",
        description="Object used to store generated custom properties",
        type=bpy.types.Object,
        update=_izom_propui_free_default_target_picker_updated,
    )
    params.izom_propui_free_generated_panels_json = bpy.props.StringProperty(
        name="Generated Panels",
        description="Internal saved generated panel slots",
        default="[]",
        options={'HIDDEN'},
        update=_izom_propui_free_params_state_updated,
    )
    params.izom_propui_free_replace_storage_on_generate = bpy.props.BoolProperty(
        name="Replace Storage on Generate",
        description="When enabled, Generate UI first removes every custom property from the Property Storage target, then recreates only the properties managed by the current PropUI setup. Disable this to keep other existing custom properties when generating",
        default=False,
        update=_izom_propui_free_params_state_updated,
    )
    params.izom_propui_free_clean_old_targets_on_generate = bpy.props.BoolProperty(
        name="Clean Old Targets on Generate",
        description="When enabled, Generate UI removes matching managed PropUI properties from old targets that no longer own those entries",
        default=True,
        update=_izom_propui_free_params_state_updated,
    )
    params.izom_propui_free_last_synced_prop_ids_json = bpy.props.StringProperty(
        name="Last Synced Property IDs",
        description="Internal bookkeeping for stable custom-property syncing",
        default="{}",
        options={'HIDDEN'},
    )
    params.izom_propui_free_smart_expanded_active_uid = izom_propui_free_session_string_property('izom_propui_free_smart_expanded_active_uid',
        name="Smart Expanded Active UID",
        description="Internal active entry UID that last received selection-time smart section expansion",
        default="",
        options={'HIDDEN'},
    )
    params.izom_propui_free_editor_float_decimals = izom_propui_free_session_int_property('izom_propui_free_editor_float_decimals',
        name="Float Decimals",
        description="How many decimals editor float values show while editing in the izom PropUI editor",
        default=3,
        min=0,
        max=6,
        update=_izom_propui_free_editor_float_decimals_updated,
    )
    params.izom_propui_free_entry_list_primary_column = izom_propui_free_session_enum_property(
        'izom_propui_free_entry_list_primary_column',
        default_value=0,
        name="Entry List Primary Column",
        description="Choose whether the wide leading Entry List column shows the Name or the Property ID",
        items=_IZOM_PROPUI_FREE_ENTRY_LIST_PRIMARY_COLUMN_ITEMS,
    )
    _izom_propui_free_add_confirmation_properties(params)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

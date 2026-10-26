# SPDX-License-Identifier: GPL-3.0-or-later

"""Single-source metadata for editor-only state stored with a PropUI setup."""


IZOM_PROPUI_FREE_EDITOR_EXPANDED_DEFAULT = True
IZOM_PROPUI_FREE_EDITOR_HIDE_DEFAULT = False


IZOM_PROPUI_FREE_EDITOR_EXPANDED_PROPERTY_SPECS = (
    ('izom_propui_free_display_expanded', 'Display Expanded', 'Show the Display section in Selected Entry'),
    ('izom_propui_free_custom_prop_expanded', 'Value Expanded', 'Show the Value section in Selected Entry'),
    ('izom_propui_free_child_behavior_expanded', 'Conditions Expanded', 'Show the Conditions section in Selected Entry'),
    ('izom_propui_free_storage_expanded', 'Storage Expanded', 'Show the Storage section in Selected Entry'),
    ('izom_propui_free_copy_settings_expanded', 'Dynamic Labels Expanded', 'Show the Dynamic Labels section in Selected Entry'),
    ('izom_propui_free_selected_row_expanded', 'Selected Row Expanded', 'Show the Selected Row sub-section in Generated Layout'),
    ('izom_propui_free_output_setup_branding_expanded', 'Generated UI Identity Expanded', 'Show generated UI identity and branding settings in Output Setup'),
    ('izom_propui_free_output_setup_storage_expanded', 'Property Storage Expanded', 'Show property storage and sync settings in Output Setup'),
    ('izom_propui_free_editor_settings_reset_expanded', 'Reset izom PropUI Expanded', 'Show izom PropUI reset controls'),
)

IZOM_PROPUI_FREE_EDITOR_HIDE_PROPERTY_SPECS = ()

IZOM_PROPUI_FREE_PROJECT_EDITOR_MISC_PROPERTY_SPECS = (
    ('izom_propui_free_last_editor_context', 'STRING', 'Last Editor Context', 'Internal last-active izom PropUI editor context for selection sync', 'HIERARCHY'),
    ('izom_propui_free_last_entry_editor_context', 'STRING', 'Last Entry Editor Context', 'Internal last-active entry-list context for selection sync', 'HIERARCHY'),
    ('izom_propui_free_last_clicked_list_context', 'STRING', 'Last Clicked List Context', 'Internal last-clicked selectable izom PropUI list for selection sync', 'ENTRY_LIST'),
)

IZOM_PROPUI_FREE_PROJECT_EDITOR_BOOL_PROPERTY_SPECS = (
    ('izom_propui_free_show_entry_tree_hints', 'Entry List Tree Hints', 'Show lightweight parent/child indentation and icons in the flat Entry List without using collapse or hidden-row filtering', True),
)

IZOM_PROPUI_FREE_EDITOR_ONLY_BOOL_PROPERTY_SPECS = (
    ('izom_propui_free_gl_safe_import', 'Safe Import', 'Prevent importing the same Entry List entry into Generated Layout more than once', True),
)

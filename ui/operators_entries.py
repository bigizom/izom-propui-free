# SPDX-License-Identifier: GPL-3.0-or-later

from .operators_entries_core import (
    IZOM_PROPUI_FREE_OT_add_entry,
    IZOM_PROPUI_FREE_OT_duplicate_entry,
    IZOM_PROPUI_FREE_OT_move_entry,
    IZOM_PROPUI_FREE_OT_remove_entry,
    IZOM_PROPUI_FREE_OT_select_entry,
)
from .operators_entries_tools import (
    IZOM_PROPUI_FREE_OT_pick_icon,
    IZOM_PROPUI_FREE_OT_toggle_active_entry_collapse,
    IZOM_PROPUI_FREE_OT_toggle_active_layout_row_group_collapse,
    IZOM_PROPUI_FREE_OT_toggle_layout_row_group_collapse,
)


CLASSES = (
    IZOM_PROPUI_FREE_OT_toggle_active_entry_collapse,
    IZOM_PROPUI_FREE_OT_pick_icon,
    IZOM_PROPUI_FREE_OT_toggle_layout_row_group_collapse,
    IZOM_PROPUI_FREE_OT_toggle_active_layout_row_group_collapse,
    IZOM_PROPUI_FREE_OT_add_entry,
    IZOM_PROPUI_FREE_OT_remove_entry,
    IZOM_PROPUI_FREE_OT_move_entry,
    IZOM_PROPUI_FREE_OT_select_entry,
    IZOM_PROPUI_FREE_OT_duplicate_entry,
)

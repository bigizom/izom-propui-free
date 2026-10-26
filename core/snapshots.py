# SPDX-License-Identifier: GPL-3.0-or-later

"""
Namespace Consolidation Module (core/snapshots.py)

Gathers and re-exports core state snapshot operations from snapshot_entries,
snapshot_layout, and snapshot_tree. It acts as a single-entry namespace for the
rest of the package.

CRITICAL: Routing snapshot operations through this module ensures circular dependencies
are resolved at initialization time. Do NOT remove or restructure these re-exports.
"""

from .snapshot_entries import (
    _izom_propui_free_active_uid,
    _izom_propui_free_make_default_snapshot,
    _izom_propui_free_restore_value_labels,
    _izom_propui_free_restore_value_labels_collection,
    _izom_propui_free_snapshot_entry,
    _izom_propui_free_snapshot_value_label,
    izom_propui_free_ensure_consistency,
    izom_propui_free_restore_entries,
    izom_propui_free_snapshot_entries,
    izom_propui_free_snapshot_runtime_entries,
)
from .snapshot_layout import (
    _izom_propui_free_layout_column_label,
    _izom_propui_free_layout_row_count,
    _izom_propui_free_make_default_layout_row_snapshot,
    _izom_propui_free_make_default_layout_snapshot,
    _izom_propui_free_normalize_layout_snapshots,
    _izom_propui_free_order_layout_rows_by_container,
    _izom_propui_free_restore_layout_items,
    _izom_propui_free_restore_layout_rows,
    _izom_propui_free_snapshot_layout_item,
    _izom_propui_free_snapshot_layout_row,
    _izom_propui_free_sync_entry_layout_fields,
    izom_propui_free_ensure_layout_items,
    izom_propui_free_snapshot_layout_items,
    izom_propui_free_snapshot_layout_rows,
)
from .snapshot_tree import (
    _izom_propui_free_build_state_from_snapshots,
    _izom_propui_free_clamp_snapshot_compare_value,
    _izom_propui_free_clamp_snapshot_default_value,
    _izom_propui_free_clamp_visibility_inheritance_depth,
    _izom_propui_free_descendant_uids,
    _izom_propui_free_entry_ancestor_chain_from_state,
    _izom_propui_free_move_block_down,
    _izom_propui_free_move_block_up,
    _izom_propui_free_normalize_snapshot_display_rows,
    _izom_propui_free_snapshot_numeric_bounds,
    _izom_propui_free_subtree_end,
    _izom_propui_free_visibility_inheritance_depth_from_state,
)

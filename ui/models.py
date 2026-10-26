# SPDX-License-Identifier: GPL-3.0-or-later

"""
Namespace Consolidation Module (ui/models.py)

Exposes UI-specific model classes (PropertyEntry, LayoutItem, VisibilityTargetItem, etc.)
by grouping them from sibling model files (model_entries, model_layout, model_visibility).

CRITICAL: Routing imports through this consolidated module breaks circular dependency loops
during addon initialization. Do NOT remove or restructure these re-exports.
"""

from .model_entries import IZOM_PROPUI_FREE_PropertyEntry
from .model_layout import (
    IZOM_PROPUI_FREE_LayoutItem,
    IZOM_PROPUI_FREE_LayoutRow,
    IZOM_PROPUI_FREE_LayoutViewItem,
)

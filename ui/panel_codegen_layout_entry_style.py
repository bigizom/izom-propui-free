# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.constants import (
    izom_propui_free_normalize_multi_component_layout,
    izom_propui_free_normalize_multi_component_draw_mode,
    izom_propui_free_normalize_value_label_layout,
)
from .panel_codegen_layout_common import (
    izom_propui_free_uses_scalar_label_layout,
)

class _IzomPropUICodegenLayoutEntryStyleMixin:
    def _entry_multi_component_layout(self, entry):
        return izom_propui_free_normalize_multi_component_layout(entry.get('multi_component_layout'))

    def _entry_multi_component_draw_mode(self, entry):
        return izom_propui_free_normalize_multi_component_draw_mode(
            entry.get('multi_component_draw_mode', 'WIDGET')
        )

    def _entry_value_label_layout(self, entry):
        return izom_propui_free_normalize_value_label_layout(entry.get('value_label_layout'))

    def _entry_uses_scalar_label_above(self, entry):
        value_kind = self._entry_value_kind(entry)
        if not izom_propui_free_uses_scalar_label_layout(value_kind):
            return False
        return self._entry_value_label_layout(entry) == 'LABEL_ABOVE'

    def _entry_uses_scalar_split_label(self, entry):
        value_kind = self._entry_value_kind(entry)
        if not izom_propui_free_uses_scalar_label_layout(value_kind):
            return False
        return self._entry_value_label_layout(entry) == 'SPLIT_LABEL'


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

# SPDX-License-Identifier: GPL-3.0-or-later

class _IzomPropUICodegenPropertyCellMixin:
    def _append_raw_draw_property_lines(self, lines, layout_var, owner_var, owner_path, prop_path_expr, label_expr, suffix, entry, prop_id, *, base_indent=''):
        lines.append(f"{base_indent}{layout_var}.prop({owner_var}, {prop_path_expr}, text={label_expr}{suffix})")

    def _append_draw_property_lines(self, lines, layout_var, owner_var, owner_path, prop_path_expr, label_expr, suffix, entry, prop_id, *, base_indent=''):
        self._append_raw_draw_property_lines(
            lines,
            layout_var,
            owner_var,
            owner_path,
            prop_path_expr,
            label_expr,
            suffix,
            entry,
            prop_id,
            base_indent=base_indent,
        )

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

# SPDX-License-Identifier: GPL-3.0-or-later

from .panel_codegen_cell_common import (
    IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT,
)

class _IzomPropUICodegenTextCellMixin:
    def _append_single_text_group_lines(self, lines, entry, index, row_var, layout_var, *, base_indent='', row_insets=None, source_value_vars=None):
        text_layout_var = layout_var
        use_row_height = abs(self._entry_row_height_scale(entry) - IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT) > 1e-6
        left_depth, right_depth = self._row_inset_depths(row_insets)
        use_row_inset = left_depth > 0 or right_depth > 0
        if use_row_inset:
            lines.append(f"{base_indent}{row_var} = {layout_var}.row(align=False)")
            if left_depth > 0:
                self._append_row_inset_lines(lines, row_var, left_depth, base_indent=base_indent, side='left')
            text_layout_var = row_var
            if use_row_height:
                text_height_var = f"izom_propui_free_text_height_{index}"
                lines.append(f"{base_indent}{text_height_var} = {text_layout_var}.column(align=True)")
                self._append_row_height_scale_lines(lines, text_height_var, entry, base_indent=base_indent)
                text_layout_var = text_height_var
        elif use_row_height:
            text_layout_var = f"izom_propui_free_text_layout_{index}"
            lines.append(f"{base_indent}{text_layout_var} = {layout_var}.column(align=True)")
            if use_row_height:
                self._append_row_height_scale_lines(lines, text_layout_var, entry, base_indent=base_indent)
        self._append_static_text_block_render_lines(
            lines,
            text_layout_var,
            f"text_{index}_single",
            entry,
            base_indent=base_indent,
        )
        if right_depth > 0:
            self._append_row_inset_lines(lines, row_var, right_depth, base_indent=base_indent, side='right')


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

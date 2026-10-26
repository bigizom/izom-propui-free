# SPDX-License-Identifier: GPL-3.0-or-later

class _IzomPropUICodegenSpecialCellMixin:
    def _append_text_entry_cell_lines(self, lines, entry, index, row_var, *, base_indent='', source_value_vars=None):
        cell_var = f"izom_propui_free_cell_{index}"
        lines.append(f"{base_indent}{cell_var} = {row_var}.column(align=True)")
        text_var = f"izom_propui_free_text_label_{index}"
        self._append_static_text_block_render_lines(
            lines,
            cell_var,
            f"text_{index}_shared",
            entry,
            base_indent=base_indent,
        )

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

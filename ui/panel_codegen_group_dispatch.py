# SPDX-License-Identifier: GPL-3.0-or-later

class _IzomPropUICodegenGroupDispatchMixin:
    def _draw_entry_group(self, ui_target, group):
        if not group:
            return

        _first_entry, first_index, _first_condition = group[0]
        row_insets = self._group_row_insets(group)
        layout_var = ui_target.layout
        row_var = f"izom_propui_free_row_{first_index}"
        bone_var = f"izom_propui_free_owner_{first_index}"
        lines = []
        base_indent = ''

        source_value_vars = self._append_group_source_read_lines(
            lines,
            group,
            first_index,
            base_indent=base_indent,
            bone_var=None,
        )

        if len(group) > 1:
            self._append_fill_row_group_lines(
                lines,
                group,
                row_var,
                bone_var,
                layout_var,
                base_indent=base_indent,
                row_insets=row_insets,
                source_value_vars=source_value_vars,
            )
        else:
            self._append_standard_group_lines(
                lines,
                group,
                row_var,
                bone_var,
                layout_var,
                base_indent=base_indent,
                row_insets=row_insets,
                source_value_vars=source_value_vars,
            )

        group_condition = self._group_condition_expr(group)
        if group_condition is not None:
            ui_target.add_line(f"if {group_condition}:")
            for line in lines:
                ui_target.add_line(f"    {line}")
            return

        for line in lines:
            ui_target.add_line(line)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

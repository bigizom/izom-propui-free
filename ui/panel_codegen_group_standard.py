# SPDX-License-Identifier: GPL-3.0-or-later

class _IzomPropUICodegenStandardGroupMixin:
    def _append_standard_group_lines(self, lines, group, row_var, bone_var, layout_var, *, base_indent='', row_insets=None, source_value_vars=None):
        left_depth, right_depth = self._row_inset_depths(row_insets)
        group_size = len(group)
        if group_size == 1 and str(group[0][0].get('prop_type', '') or '') == 'TEXT':
            entry, index, condition = group[0]
            entry_indent = base_indent
            if condition is not None:
                lines.append(f"{base_indent}if {condition}:")
                entry_indent = base_indent + '    '
            self._append_single_text_group_lines(
                lines,
                entry,
                index,
                row_var,
                layout_var,
                base_indent=entry_indent,
                row_insets=row_insets,
                source_value_vars=source_value_vars,
            )
            return

        if group_size == 1:
            entry, index, condition = group[0]
            entry_indent = base_indent
            if condition is not None:
                lines.append(f"{base_indent}if {condition}:")
                entry_indent = base_indent + '    '
            if self._entry_uses_label_above(entry):
                self._append_single_label_above_group_lines(
                    lines,
                    entry,
                    index,
                    row_var,
                    bone_var,
                    layout_var,
                    base_indent=entry_indent,
                    row_insets=row_insets,
                    source_value_vars=source_value_vars,
                )
            else:
                lines.append(f"{entry_indent}{row_var} = {layout_var}.row(align=True)")
                self._append_group_row_height_scale_lines(lines, row_var, group, base_indent=entry_indent)
                if left_depth > 0:
                    self._append_row_inset_lines(lines, row_var, left_depth, base_indent=entry_indent, side='left')
                self._append_entry_cell_lines(
                    lines,
                    entry,
                    index,
                    row_var,
                    bone_var,
                    base_indent=entry_indent,
                    group_size=group_size,
                    source_value_vars=source_value_vars,
                )
                if right_depth > 0:
                    self._append_row_inset_lines(lines, row_var, right_depth, base_indent=entry_indent, side='right')
            return

        lines.append(f"{base_indent}{row_var} = {layout_var}.row(align=True)")
        self._append_group_row_height_scale_lines(lines, row_var, group, base_indent=base_indent)
        if left_depth > 0:
            self._append_row_inset_lines(lines, row_var, left_depth, base_indent=base_indent, side='left')

        slot_layout_vars = [f"izom_propui_free_slot_layout_{group[0][1]}_{slot_index}" for slot_index in range(group_size)]
        self._append_dynamic_slot_layout_lines(
            lines,
            row_var,
            slot_layout_vars,
            str(group_size),
            f"standard_{group[0][1]}",
            base_indent=base_indent,
        )
        for slot_index, (entry, index, condition) in enumerate(group):
            entry_indent = base_indent
            if condition is not None:
                lines.append(f"{base_indent}if {condition}:")
                entry_indent = base_indent + '    '
            self._append_entry_cell_lines(
                lines,
                entry,
                index,
                slot_layout_vars[slot_index],
                bone_var,
                base_indent=entry_indent,
                group_size=group_size,
                source_value_vars=source_value_vars,
            )
        if right_depth > 0:
            self._append_row_inset_lines(lines, row_var, right_depth, base_indent=base_indent, side='right')


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

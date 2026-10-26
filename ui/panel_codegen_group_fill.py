# SPDX-License-Identifier: GPL-3.0-or-later

class _IzomPropUICodegenFillGroupMixin:
    def _append_fill_row_group_dispatch_lines(
        self,
        lines,
        group,
        slot_var,
        slot_entry_index_var,
        bone_var,
        *,
        base_indent='',
        source_value_vars=None,
        labels_only=False,
        suppress_label_above=False,
    ):
        for entry, index, _condition in group:
            lines.append(f"{base_indent}if {slot_entry_index_var} == {index}:")
            if labels_only:
                if self._entry_uses_shared_row_label_above(entry):
                    self._append_entry_label_above_lines(
                        lines,
                        entry,
                        index,
                        slot_var,
                        source_value_vars=source_value_vars,
                        base_indent=base_indent + '    ',
                    )
                else:
                    lines.append(f"{base_indent}    pass")
            else:
                self._append_entry_cell_lines(
                    lines,
                    entry,
                    index,
                    slot_var,
                    bone_var,
                    base_indent=base_indent + '    ',
                    group_size=len(group),
                    source_value_vars=source_value_vars,
                    suppress_multi_component_label=suppress_label_above,
                )

    def _append_fixed_slot_layout_lines(self, lines, row_var, slot_layout_vars, token, *, base_indent=''):
        if not slot_layout_vars:
            return
        if len(slot_layout_vars) == 1:
            lines.append(f"{base_indent}{slot_layout_vars[0]} = {row_var}")
            return
        if len(slot_layout_vars) == 2:
            split_var = f"izom_propui_free_split_{token}"
            lines.append(f"{base_indent}{split_var} = {row_var}.split(factor=0.5, align=True)")
            lines.append(f"{base_indent}{slot_layout_vars[0]} = {split_var}.column(align=True)")
            lines.append(f"{base_indent}{slot_layout_vars[1]} = {split_var}.column(align=True)")
            return
        remaining_layout_var = f"izom_propui_free_remaining_layout_{token}"
        lines.append(f"{base_indent}{remaining_layout_var} = {row_var}")
        total_slots = len(slot_layout_vars)
        for slot_index, slot_layout_var in enumerate(slot_layout_vars):
            if slot_index == total_slots - 1:
                lines.append(f"{base_indent}{slot_layout_var} = {remaining_layout_var}")
                continue
            split_var = f"izom_propui_free_split_{token}_{slot_index}"
            remaining_slots = total_slots - slot_index
            lines.append(
                f"{base_indent}{split_var} = {remaining_layout_var}.split("
                f"factor={(1.0 / float(remaining_slots))!r}, align=True)"
            )
            lines.append(f"{base_indent}{slot_layout_var} = {split_var}.column(align=True)")
            lines.append(f"{base_indent}{remaining_layout_var} = {split_var}.column(align=True)")

    def _append_static_fill_row_group_lines(self, lines, group, row_var, bone_var, layout_var, *, base_indent='', row_insets=None, source_value_vars=None):
        first_index = group[0][1]
        slot_count = max(1, len(group))
        slot_layout_vars = [f"izom_propui_free_slot_layout_{first_index}_{slot_index}" for slot_index in range(slot_count)]
        uses_label_above = self._group_uses_multi_component_label_above(group)
        left_depth, right_depth = self._row_inset_depths(row_insets)

        if uses_label_above:
            label_row_var = f"{row_var}_labels"
            label_slot_layout_vars = [
                f"izom_propui_free_label_slot_layout_{first_index}_{slot_index}"
                for slot_index in range(slot_count)
            ]
            lines.append(f"{base_indent}{label_row_var} = {layout_var}.row(align=True)")
            if left_depth > 0:
                self._append_row_inset_lines(lines, label_row_var, left_depth, base_indent=base_indent, side='left')
            self._append_fixed_slot_layout_lines(
                lines,
                label_row_var,
                label_slot_layout_vars,
                f"fill_labels_{first_index}",
                base_indent=base_indent,
            )
            for slot_index, (entry, index, _condition) in enumerate(group):
                if self._entry_uses_shared_row_label_above(entry):
                    self._append_entry_label_above_lines(
                        lines,
                        entry,
                        index,
                        label_slot_layout_vars[slot_index],
                        source_value_vars=source_value_vars,
                        base_indent=base_indent,
                    )
            if right_depth > 0:
                self._append_row_inset_lines(lines, label_row_var, right_depth, base_indent=base_indent, side='right')

        lines.append(f"{base_indent}{row_var} = {layout_var}.row(align=True)")
        self._append_group_row_height_scale_lines(lines, row_var, group, base_indent=base_indent)
        if left_depth > 0:
            self._append_row_inset_lines(lines, row_var, left_depth, base_indent=base_indent, side='left')
        self._append_fixed_slot_layout_lines(
            lines,
            row_var,
            slot_layout_vars,
            f"fill_{first_index}",
            base_indent=base_indent,
        )
        for slot_index, (entry, index, _condition) in enumerate(group):
            self._append_entry_cell_lines(
                lines,
                entry,
                index,
                slot_layout_vars[slot_index],
                bone_var,
                base_indent=base_indent,
                group_size=len(group),
                source_value_vars=source_value_vars,
                suppress_multi_component_label=uses_label_above,
            )
        if right_depth > 0:
            self._append_row_inset_lines(lines, row_var, right_depth, base_indent=base_indent, side='right')

    def _append_fill_row_group_lines(self, lines, group, row_var, bone_var, layout_var, *, base_indent='', row_insets=None, source_value_vars=None):
        if all(condition is None for _entry, _index, condition in group):
            self._append_static_fill_row_group_lines(
                lines,
                group,
                row_var,
                bone_var,
                layout_var,
                base_indent=base_indent,
                row_insets=row_insets,
                source_value_vars=source_value_vars,
            )
            return

        first_index = group[0][1]
        render_entries_var = f"izom_propui_free_render_entries_{first_index}"
        slot_count_var = f"izom_propui_free_slot_count_{first_index}"
        slot_count = max(1, len(group))
        slot_layout_vars = [f"izom_propui_free_slot_layout_{first_index}_{slot_index}" for slot_index in range(slot_count)]
        slot_entry_index_vars = [f"izom_propui_free_slot_entry_index_{first_index}_{slot_index}" for slot_index in range(slot_count)]
        visible_var_by_index = {}
        left_depth, right_depth = self._row_inset_depths(row_insets)

        for _entry, index, condition in group:
            if condition is None:
                continue
            visible_var = f"izom_propui_free_visible_{index}"
            visible_var_by_index[index] = visible_var
            lines.append(f"{base_indent}{visible_var} = bool({condition})")

        lines.append(f"{base_indent}{render_entries_var} = []")
        for entry, index, condition in group:
            if condition is None:
                lines.append(f"{base_indent}{render_entries_var}.append({index})")
                continue
            visible_var = visible_var_by_index[index]
            lines.append(f"{base_indent}if {visible_var}:")
            lines.append(f"{base_indent}    {render_entries_var}.append({index})")

        lines.append(f"{base_indent}if {render_entries_var}:")
        content_indent = base_indent + '    '
        uses_label_above = self._group_uses_multi_component_label_above(group)
        lines.append(f"{content_indent}{slot_count_var} = len({render_entries_var})")
        if uses_label_above:
            label_row_var = f"{row_var}_labels"
            label_slot_layout_vars = [
                f"izom_propui_free_label_slot_layout_{first_index}_{slot_index}"
                for slot_index in range(slot_count)
            ]
            lines.append(f"{content_indent}{label_row_var} = {layout_var}.row(align=True)")
            if left_depth > 0:
                self._append_row_inset_lines(lines, label_row_var, left_depth, base_indent=content_indent, side='left')
            self._append_dynamic_slot_layout_lines(
                lines,
                label_row_var,
                label_slot_layout_vars,
                slot_count_var,
                f"fill_labels_{first_index}",
                base_indent=content_indent,
            )
            lines.append(f"{content_indent}{slot_entry_index_vars[0]} = {render_entries_var}[0]")
            self._append_fill_row_group_dispatch_lines(
                lines,
                group,
                label_slot_layout_vars[0],
                slot_entry_index_vars[0],
                bone_var,
                base_indent=content_indent,
                source_value_vars=source_value_vars,
                labels_only=True,
            )
            for slot_index in range(1, slot_count):
                lines.append(f"{content_indent}if {slot_count_var} > {slot_index}:")
                lines.append(
                    f"{content_indent}    {slot_entry_index_vars[slot_index]} = "
                    f"{render_entries_var}[{slot_index}]"
                )
                self._append_fill_row_group_dispatch_lines(
                    lines,
                    group,
                    label_slot_layout_vars[slot_index],
                    slot_entry_index_vars[slot_index],
                    bone_var,
                    base_indent=content_indent + '    ',
                    source_value_vars=source_value_vars,
                    labels_only=True,
                )
            if right_depth > 0:
                self._append_row_inset_lines(lines, label_row_var, right_depth, base_indent=content_indent, side='right')

        lines.append(f"{content_indent}{row_var} = {layout_var}.row(align=True)")
        self._append_group_row_height_scale_lines(lines, row_var, group, base_indent=content_indent)
        if left_depth > 0:
            self._append_row_inset_lines(lines, row_var, left_depth, base_indent=content_indent, side='left')
        self._append_dynamic_slot_layout_lines(
            lines,
            row_var,
            slot_layout_vars,
            slot_count_var,
            f"fill_{first_index}",
            base_indent=content_indent,
        )

        lines.append(f"{content_indent}{slot_entry_index_vars[0]} = {render_entries_var}[0]")
        self._append_fill_row_group_dispatch_lines(
            lines,
            group,
            slot_layout_vars[0],
            slot_entry_index_vars[0],
            bone_var,
            base_indent=content_indent,
            source_value_vars=source_value_vars,
            suppress_label_above=uses_label_above,
        )

        for slot_index in range(1, slot_count):
            lines.append(f"{content_indent}if {slot_count_var} > {slot_index}:")
            lines.append(
                f"{content_indent}    {slot_entry_index_vars[slot_index]} = "
                f"{render_entries_var}[{slot_index}]"
            )
            self._append_fill_row_group_dispatch_lines(
                lines,
                group,
                slot_layout_vars[slot_index],
                slot_entry_index_vars[slot_index],
                bone_var,
                base_indent=content_indent + '    ',
                source_value_vars=source_value_vars,
                suppress_label_above=uses_label_above,
            )
        if right_depth > 0:
            self._append_row_inset_lines(lines, row_var, right_depth, base_indent=content_indent, side='right')


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

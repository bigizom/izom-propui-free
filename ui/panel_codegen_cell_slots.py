# SPDX-License-Identifier: GPL-3.0-or-later


class _IzomPropUICodegenSlotCellMixin:
    def _append_placeholder_slot_lines(self, lines, slot_var, token, *, base_indent=''):
        placeholder_var = f"izom_propui_free_placeholder_{token}"
        lines.append(f"{base_indent}{placeholder_var} = {slot_var}.row(align=True)")
        lines.append(f"{base_indent}{placeholder_var}.label(text='')")

    def _append_reserved_slot_dispatch_lines(
        self,
        lines,
        group,
        slot_var,
        slot_kind_var,
        slot_entry_index_var,
        bone_var,
        token,
        *,
        base_indent='',
        source_value_vars=None,
        labels_only=False,
        suppress_label_above=False,
    ):
        lines.append(f"{base_indent}if {slot_kind_var} == 'placeholder':")
        if labels_only:
            lines.append(f"{base_indent}    pass")
        else:
            self._append_placeholder_slot_lines(
                lines,
                slot_var,
                token,
                base_indent=base_indent + '    ',
            )
        for entry, index, _condition in group:
            lines.append(f"{base_indent}elif {slot_entry_index_var} == {index}:")
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

    def _append_dynamic_slot_layout_lines(self, lines, row_var, slot_layout_vars, slot_count_var, token, *, base_indent=''):
        if not slot_layout_vars:
            return
        remaining_layout_var = f"izom_propui_free_remaining_layout_{token}"
        remaining_slots_var = f"izom_propui_free_remaining_slots_{token}"
        lines.append(f"{base_indent}{remaining_layout_var} = {row_var}")
        lines.append(f"{base_indent}{remaining_slots_var} = int({slot_count_var})")
        for slot_index, slot_layout_var in enumerate(slot_layout_vars):
            lines.append(f"{base_indent}if {slot_count_var} > {slot_index}:")
            slot_indent = base_indent + '    '
            if slot_index == len(slot_layout_vars) - 1:
                lines.append(f"{slot_indent}{slot_layout_var} = {remaining_layout_var}")
                continue
            split_var = f"izom_propui_free_split_{token}_{slot_index}"
            lines.append(f"{slot_indent}if {remaining_slots_var} > 1:")
            lines.append(
                f"{slot_indent}    {split_var} = {remaining_layout_var}.split("
                f"factor=(1.0 / float({remaining_slots_var})), align=True)"
            )
            lines.append(f"{slot_indent}    {slot_layout_var} = {split_var}.column(align=True)")
            lines.append(f"{slot_indent}    {remaining_layout_var} = {split_var}.column(align=True)")
            lines.append(f"{slot_indent}    {remaining_slots_var} -= 1")
            lines.append(f"{slot_indent}else:")
            lines.append(f"{slot_indent}    {slot_layout_var} = {remaining_layout_var}")


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

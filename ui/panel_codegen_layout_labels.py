# SPDX-License-Identifier: GPL-3.0-or-later

from .panel_codegen_layout_common import (
    izom_propui_free_shorten_ui_text,
)

class _IzomPropUICodegenLayoutLabelsMixin:
    def _append_entry_label_expr_lines(self, lines, entry, index, target_var, *, source_value_vars=None, base_indent=''):
        if self._entry_has_dynamic_prop_labels(entry):
            self._append_dynamic_prop_label_lines(
                lines,
                entry,
                index,
                target_var,
                source_value_vars=source_value_vars,
                base_indent=base_indent,
            )
        else:
            lines.append(f"{base_indent}{target_var} = {self._display_text_literal((entry.get('label') or '').strip())}")
        return target_var

    def _append_entry_label_above_lines(self, lines, entry, index, layout_var, *, source_value_vars=None, base_indent=''):
        prop_type = str(entry.get('prop_type', 'FLOAT') or 'FLOAT').strip().upper()
        owner_var = f"izom_propui_free_label_owner_{index}"
        lines.append(f"{base_indent}{owner_var} = target_owners.get({self._entry_owner_path(entry)!r})")
        lines.append(f"{base_indent}if {owner_var} is not None:")
        inner_indent = base_indent + '    '
        label_cell_var = f"izom_propui_free_label_above_cell_{index}"
        label_var = f"izom_propui_free_label_above_text_{index}"
        lines.append(f"{inner_indent}{label_cell_var} = {layout_var}.column(align=True)")
        if bool(entry.get('alert_style', False)):
            lines.append(f"{inner_indent}{label_cell_var}.alert = True")
        has_dynamic_label = self._entry_has_dynamic_prop_labels(entry)
        if has_dynamic_label:
            self._append_entry_label_expr_lines(
                lines,
                entry,
                index,
                label_var,
                source_value_vars=source_value_vars,
                base_indent=inner_indent,
            )
            lines.append(f"{inner_indent}if {label_var}:")
            lines.append(f"{inner_indent}    {label_cell_var}.label(text={label_var})")
        else:
            label_text = izom_propui_free_shorten_ui_text((entry.get('label') or '').strip(), limit=None)
            if label_text:
                lines.append(f"{inner_indent}{label_cell_var}.label(text={label_text!r})")


    def _append_single_label_above_group_lines(self, lines, entry, index, row_var, bone_var, layout_var, *, base_indent='', row_insets=None, source_value_vars=None):
        label_row_var = f"{row_var}_label"
        left_depth, right_depth = self._row_inset_depths(row_insets)
        if left_depth > 0 or right_depth > 0:
            lines.append(f"{base_indent}{label_row_var} = {layout_var}.row(align=True)")
            if left_depth > 0:
                self._append_row_inset_lines(lines, label_row_var, left_depth, base_indent=base_indent, side='left')
            label_layout_var = label_row_var
        else:
            lines.append(f"{base_indent}{label_row_var} = {layout_var}.column(align=True)")
            label_layout_var = label_row_var
        self._append_entry_label_above_lines(
            lines,
            entry,
            index,
            label_layout_var,
            source_value_vars=source_value_vars,
            base_indent=base_indent,
        )
        if right_depth > 0:
            self._append_row_inset_lines(lines, label_row_var, right_depth, base_indent=base_indent, side='right')

        lines.append(f"{base_indent}{row_var} = {layout_var}.row(align=True)")
        self._append_row_height_scale_lines(lines, row_var, entry, base_indent=base_indent)
        if left_depth > 0:
            self._append_row_inset_lines(lines, row_var, left_depth, base_indent=base_indent, side='left')
        self._append_entry_cell_lines(
            lines,
            entry,
            index,
            row_var,
            bone_var,
            base_indent=base_indent,
            group_size=1,
            source_value_vars=source_value_vars,
            suppress_multi_component_label=True,
        )
        if right_depth > 0:
            self._append_row_inset_lines(lines, row_var, right_depth, base_indent=base_indent, side='right')

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

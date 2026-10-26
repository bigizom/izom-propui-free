# SPDX-License-Identifier: GPL-3.0-or-later

from types import SimpleNamespace

from .panel_codegen_cell_common import (
    izom_propui_free_entry_slider_control_available,
    rna_idprop_quote_path,
)


class _IzomPropUICodegenEntryCellMixin:
    def _append_entry_cell_lines(
        self,
        lines,
        entry,
        index,
        row_var,
        bone_var,
        *,
        base_indent='',
        group_size=1,
        source_value_vars=None,
        suppress_multi_component_label=False,
    ):
        ctx = self._entry_cell_context(
            entry,
            index,
            row_var,
            base_indent=base_indent,
        )
        if self._append_special_entry_cell_lines(
            lines,
            ctx,
            group_size=group_size,
            source_value_vars=source_value_vars,
        ):
            return
        if not self._append_entry_cell_owner_lines(lines, ctx):
            return
        self._append_entry_cell_owner_gate_lines(lines, ctx)
        self._prepare_entry_cell_draw_state(
            lines,
            ctx,
            group_size=group_size,
            source_value_vars=source_value_vars,
        )
        self._append_entry_cell_missing_property_guard(lines, ctx)
        if self._append_entry_cell_label_above_lines(lines, ctx, suppress_multi_component_label):
            return
        if self._append_entry_cell_suppressed_inline_label_lines(lines, ctx, suppress_multi_component_label):
            return
        self._append_entry_cell_inline_lines(lines, ctx)

    def _entry_cell_context(self, entry, index, row_var, *, base_indent=''):
        return SimpleNamespace(
            entry=entry,
            index=index,
            row_var=row_var,
            base_indent=base_indent,
            inner_indent=base_indent + '    ',
            cell_var=f"izom_propui_free_cell_{index}",
            owner_var=f"izom_propui_free_owner_{index}",
            prop_type=str(entry.get('prop_type', 'FLOAT') or 'FLOAT').strip().upper(),
            value_kind=self._entry_value_kind(entry),
            internal_control='',
            owner_path='',
            prop_path_expr="''",
            prop_id=str(entry.get('prop_id', '') or '').strip(),
            control_layout_var=row_var,
            alert_style=False,
            suffix='',
            label_expr="''",
        )

    def _append_special_entry_cell_lines(
        self,
        lines,
        ctx,
        *,
        group_size=1,
        source_value_vars=None,
    ):
        if ctx.prop_type == 'TEXT':
            self._append_text_entry_cell_lines(
                lines,
                ctx.entry,
                ctx.index,
                ctx.row_var,
                base_indent=ctx.base_indent,
                source_value_vars=source_value_vars,
            )
            return True
        return False

    def _append_entry_cell_owner_lines(self, lines, ctx):
        ctx.owner_path = self._entry_owner_path(ctx.entry)
        lines.append(f"{ctx.base_indent}{ctx.owner_var} = target_owners.get({ctx.owner_path!r})")
        ctx.prop_path_expr = repr(rna_idprop_quote_path(ctx.prop_id))
        return True

    def _append_entry_cell_owner_gate_lines(self, lines, ctx):
        lines.append(f"{ctx.base_indent}if {ctx.owner_var} is not None:")
        ctx.inner_indent = ctx.base_indent + '    '

    def _prepare_entry_cell_draw_state(self, lines, ctx, *, group_size=1, source_value_vars=None):
        uses_component_draw_mode = self._entry_inline_native_control_subtype(ctx.entry) == 'NONE'
        slider_supported = izom_propui_free_entry_slider_control_available(
            ctx.entry,
            ctx.value_kind,
            uses_component_draw_mode=uses_component_draw_mode,
        )
        if ctx.value_kind == 'INT':
            slider_supported = False
        slider = slider_supported and bool(ctx.entry.get('slider', False))
        ctx.alert_style = bool(ctx.entry.get('alert_style', False))
        ctx.label_expr = self._entry_cell_label_expr(lines, ctx, source_value_vars)
        ctx.suffix = self._entry_cell_prop_suffix(lines, ctx, slider_supported, slider)

    def _entry_cell_label_expr(self, lines, ctx, source_value_vars):
        if not self._entry_has_dynamic_prop_labels(ctx.entry):
            return self._display_text_literal((ctx.entry.get('label') or '').strip())
        label_var = f"izom_propui_free_prop_label_{ctx.index}"
        self._append_entry_label_expr_lines(
            lines,
            ctx.entry,
            ctx.index,
            label_var,
            source_value_vars=source_value_vars,
            base_indent=ctx.inner_indent,
        )
        return label_var

    def _entry_cell_prop_suffix(self, lines, ctx, slider_supported, slider):
        prop_kwargs = []
        if slider:
            prop_kwargs.append("slider=True")
        elif slider_supported:
            prop_kwargs.append("slider=False")
        return ", " + ", ".join(prop_kwargs) if prop_kwargs else ""

    def _append_entry_cell_missing_property_guard(self, lines, ctx):
        if not ctx.prop_id:
            return
        lines.append(f"{ctx.inner_indent}if {ctx.prop_id!r} not in {ctx.owner_var}:")
        lines.append(f"{ctx.inner_indent}    {ctx.cell_var} = {ctx.control_layout_var}.row(align=True)")
        lines.append(f"{ctx.inner_indent}    {ctx.cell_var}.label(text={('Missing property: ' + ctx.prop_id)!r}, icon='ERROR')")
        lines.append(f"{ctx.inner_indent}else:")
        ctx.inner_indent += '    '

    def _append_entry_cell_container_lines(self, lines, ctx, layout_var, kind, *, align=True):
        lines.append(f"{ctx.inner_indent}{ctx.cell_var} = {layout_var}.{kind}(align={bool(align)!r})")
        if ctx.alert_style:
            lines.append(f"{ctx.inner_indent}{ctx.cell_var}.alert = True")

    def _append_entry_cell_value_or_choice_lines(self, lines, ctx, layout_var, label_expr, *, indexed=False):
        if indexed:
            self._append_indexed_component_prop_lines(
                lines,
                layout_var,
                ctx.owner_var,
                ctx.prop_path_expr,
                ctx.entry,
                ctx.suffix,
                base_indent=ctx.inner_indent,
            )
        else:
            self._append_draw_property_lines(
                lines,
                layout_var,
                ctx.owner_var,
                ctx.owner_path,
                ctx.prop_path_expr,
                label_expr,
                ctx.suffix,
                ctx.entry,
                ctx.prop_id,
                base_indent=ctx.inner_indent,
            )

    def _append_entry_cell_label_above_lines(self, lines, ctx, suppress_multi_component_label):
        if not self._entry_uses_label_above(ctx.entry):
            return False
        if suppress_multi_component_label:
            self._append_entry_cell_suppressed_label_above_lines(lines, ctx)
            return True
        self._append_entry_cell_container_lines(lines, ctx, ctx.control_layout_var, 'column')
        lines.append(f"{ctx.inner_indent}if {ctx.label_expr}:")
        lines.append(f"{ctx.inner_indent}    {ctx.cell_var}.label(text={ctx.label_expr})")
        self._append_entry_cell_label_above_value_lines(lines, ctx)
        return True

    def _append_entry_cell_suppressed_label_above_lines(self, lines, ctx):
        if self._entry_uses_scalar_label_above(ctx.entry):
            self._append_entry_cell_container_lines(lines, ctx, ctx.control_layout_var, 'row')
            self._append_entry_cell_value_or_choice_lines(lines, ctx, ctx.cell_var, "''")
            return
        if self._entry_uses_stacked_multi_component_layout(ctx.entry):
            self._append_entry_cell_container_lines(lines, ctx, ctx.control_layout_var, 'column')
            if self._entry_uses_stacked_component_split_label_multi_component_layout(ctx.entry):
                self._append_entry_cell_stacked_component_split_label_lines(lines, ctx)
                return
            self._append_entry_cell_value_or_choice_lines(
                lines,
                ctx,
                ctx.cell_var,
                "''",
                indexed=True,
            )
            return

        self._append_entry_cell_container_lines(lines, ctx, ctx.control_layout_var, 'row')
        self._append_entry_cell_value_or_choice_lines(
            lines,
            ctx,
            ctx.cell_var,
            "''",
            indexed=(
                not self._entry_uses_scalar_label_above(ctx.entry)
                and self._entry_draws_indexed_inline_components(ctx.entry)
            ),
        )

    def _append_entry_cell_label_above_value_lines(self, lines, ctx):
        if self._entry_uses_scalar_label_above(ctx.entry):
            self._append_entry_cell_value_or_choice_lines(lines, ctx, ctx.cell_var, "''")
        elif self._entry_uses_stacked_component_split_label_multi_component_layout(ctx.entry):
            self._append_entry_cell_stacked_component_split_label_lines(lines, ctx)
        elif self._entry_uses_stacked_multi_component_layout(ctx.entry):
            self._append_entry_cell_value_or_choice_lines(lines, ctx, ctx.cell_var, "''", indexed=True)
        elif self._entry_draws_indexed_inline_components(ctx.entry):
            inline_component_row_var = f"izom_propui_free_inline_component_row_{ctx.index}"
            lines.append(f"{ctx.inner_indent}{inline_component_row_var} = {ctx.cell_var}.row(align=True)")
            self._append_entry_cell_value_or_choice_lines(lines, ctx, inline_component_row_var, "''", indexed=True)
        else:
            inline_component_row_var = f"izom_propui_free_inline_component_row_{ctx.index}"
            lines.append(f"{ctx.inner_indent}{inline_component_row_var} = {ctx.cell_var}.row(align=True)")
            self._append_entry_cell_value_or_choice_lines(lines, ctx, inline_component_row_var, "''")

    def _append_entry_cell_suppressed_inline_label_lines(self, lines, ctx, suppress_multi_component_label):
        if not (
            suppress_multi_component_label
            and self._entry_uses_shared_row_inline_array_label(ctx.entry)
        ):
            return False
        self._append_entry_cell_container_lines(lines, ctx, ctx.control_layout_var, 'row')
        self._append_entry_cell_value_or_choice_lines(
            lines,
            ctx,
            ctx.cell_var,
            "''",
            indexed=self._entry_draws_indexed_inline_components(ctx.entry),
        )
        return True

    def _append_entry_cell_inline_lines(self, lines, ctx):
        if self._entry_uses_split_label(ctx.entry):
            self._append_entry_cell_container_lines(lines, ctx, ctx.control_layout_var, 'row', align=False)
            self._append_entry_cell_split_label_lines(lines, ctx)
            return
        self._append_entry_cell_container_lines(lines, ctx, ctx.control_layout_var, 'row')
        if self._entry_uses_detached_inline_label(ctx.entry):
            value_layout_var = self._append_compact_inline_label_layout_lines(
                lines,
                ctx.cell_var,
                ctx.index,
                ctx.label_expr,
                base_indent=ctx.inner_indent,
            )
            self._append_draw_property_lines(
                lines,
                value_layout_var,
                ctx.owner_var,
                ctx.owner_path,
                ctx.prop_path_expr,
                "''",
                ctx.suffix,
                ctx.entry,
                ctx.prop_id,
                base_indent=ctx.inner_indent,
            )
            return
        if self._entry_draws_indexed_inline_components(ctx.entry):
            value_layout_var = self._append_compact_inline_label_layout_lines(
                lines,
                ctx.cell_var,
                ctx.index,
                ctx.label_expr,
                base_indent=ctx.inner_indent,
            )
            self._append_entry_cell_value_or_choice_lines(lines, ctx, value_layout_var, ctx.label_expr, indexed=True)
            return
        self._append_entry_cell_value_or_choice_lines(lines, ctx, ctx.cell_var, ctx.label_expr)

    def _append_entry_cell_split_label_lines(self, lines, ctx):
        if self._entry_uses_stacked_component_split_label_multi_component_layout(ctx.entry):
            self._append_entry_cell_stacked_component_split_label_lines(lines, ctx)
            return
        if self._entry_uses_stacked_split_label_multi_component_layout(ctx.entry):
            self._append_entry_cell_indexed_component_main_split_lines(lines, ctx, stacked=True)
            return
        if self._entry_draws_indexed_inline_components(ctx.entry):
            self._append_entry_cell_indexed_component_main_split_lines(lines, ctx, stacked=False)
        else:
            lines.append(f"{ctx.inner_indent}{ctx.cell_var}.use_property_split = True")
            lines.append(f"{ctx.inner_indent}{ctx.cell_var}.use_property_decorate = False")
            self._append_entry_cell_value_or_choice_lines(lines, ctx, ctx.cell_var, ctx.label_expr)

    def _append_entry_cell_indexed_component_main_split_lines(self, lines, ctx, *, stacked):
        split_var = f"izom_propui_free_main_split_{ctx.index}"
        label_row_var = f"izom_propui_free_main_split_label_{ctx.index}"
        value_row_var = f"izom_propui_free_main_split_value_{ctx.index}"
        value_layout_var = f"izom_propui_free_main_split_value_col_{ctx.index}" if stacked else value_row_var
        lines.append(f"{ctx.inner_indent}{split_var} = {ctx.cell_var}.split(factor=0.4, align=True)")
        lines.append(f"{ctx.inner_indent}{label_row_var} = {split_var}.row()")
        lines.append(f"{ctx.inner_indent}{label_row_var}.alignment = 'RIGHT'")
        lines.append(f"{ctx.inner_indent}if {ctx.label_expr}:")
        lines.append(f"{ctx.inner_indent}    {label_row_var}.label(text={ctx.label_expr})")
        lines.append(f"{ctx.inner_indent}{value_row_var} = {split_var}.row(align=True)")
        lines.append(f"{ctx.inner_indent}{value_row_var}.use_property_split = False")
        lines.append(f"{ctx.inner_indent}{value_row_var}.use_property_decorate = False")
        if stacked:
            lines.append(f"{ctx.inner_indent}{value_layout_var} = {value_row_var}.column(align=True)")
            lines.append(f"{ctx.inner_indent}{value_layout_var}.use_property_split = False")
            lines.append(f"{ctx.inner_indent}{value_layout_var}.use_property_decorate = False")
        self._append_indexed_component_prop_lines(
            lines,
            value_layout_var,
            ctx.owner_var,
            ctx.prop_path_expr,
            ctx.entry,
            ctx.suffix,
            base_indent=ctx.inner_indent,
        )

    def _append_entry_cell_stacked_component_split_label_lines(self, lines, ctx):
        component_col_var = f"izom_propui_free_split_component_col_{ctx.index}"
        lines.append(f"{ctx.inner_indent}{component_col_var} = {ctx.cell_var}.column(align=True)")
        for slot_index, (component_index, component_label) in enumerate(zip(
            self._entry_component_prop_indices(ctx.entry),
            self._entry_component_labels(ctx.entry),
        )):
            row_var = f"izom_propui_free_split_component_row_{ctx.index}_{slot_index}"
            lines.append(f"{ctx.inner_indent}{row_var} = {component_col_var}.row(align=False)")
            lines.append(f"{ctx.inner_indent}{row_var}.use_property_split = True")
            lines.append(f"{ctx.inner_indent}{row_var}.use_property_decorate = False")
            lines.append(
                f"{ctx.inner_indent}{row_var}.prop("
                f"{ctx.owner_var}, {ctx.prop_path_expr}, index={component_index}, text={component_label!r}{ctx.suffix})"
            )


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

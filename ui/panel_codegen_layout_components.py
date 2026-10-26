# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.constants import IZOM_PROPUI_FREE_NATIVE_MULTI_COMPONENT_LAYOUT_IDS
from .panel_codegen_layout_common import (
    izom_propui_free_entry_array_component_labels,
    izom_propui_free_entry_array_element_type,
    izom_propui_free_entry_array_subtype,
    izom_propui_free_entry_array_visible_value,
    izom_propui_free_subtype_supports_native_control,
)

class _IzomPropUICodegenLayoutComponentsMixin:
    def _entry_all_component_labels(self, entry):
        prop_type = str(entry.get('prop_type', 'FLOAT') or 'FLOAT').strip().upper()
        value_kind = self._entry_value_kind(entry)

        if prop_type == 'ARRAY':
            element_type = izom_propui_free_entry_array_element_type(entry, 'FLOAT') if prop_type == 'ARRAY' else 'FLOAT'
            subtype = izom_propui_free_entry_array_subtype(entry, 'NONE') if prop_type == 'ARRAY' else 'NONE'
            component_count = len(tuple(izom_propui_free_entry_array_visible_value(entry, 'default') or ()))
            return tuple(izom_propui_free_entry_array_component_labels(
                entry,
                subtype,
                size=component_count,
                element_type=element_type,
            ))

        return ()



    def _entry_component_prop_indices(self, entry):
        return tuple(range(len(self._entry_all_component_labels(entry))))

    def _entry_component_labels(self, entry):
        labels = self._entry_all_component_labels(entry)
        return labels

    def _entry_inline_native_control_subtype(self, entry):
        prop_type = str(entry.get('prop_type', 'FLOAT') or 'FLOAT').strip().upper()
        value_kind = self._entry_value_kind(entry)
        if value_kind not in {'VECTOR', 'COLOR'}:
            return 'NONE'
        if self._entry_multi_component_layout(entry) not in IZOM_PROPUI_FREE_NATIVE_MULTI_COMPONENT_LAYOUT_IDS:
            return 'NONE'
        if self._entry_multi_component_draw_mode(entry) == 'COMPONENTS':
            return 'NONE'

        if prop_type == 'ARRAY':
            element_type = izom_propui_free_entry_array_element_type(entry, 'FLOAT') if prop_type == 'ARRAY' else 'FLOAT'
            if element_type != 'FLOAT':
                return 'NONE'
            fallback_subtype = 'COLOR' if value_kind == 'COLOR' else 'NONE'
            subtype = str(izom_propui_free_entry_array_subtype(entry, fallback_subtype) or fallback_subtype).strip().upper() or fallback_subtype
            return subtype if izom_propui_free_subtype_supports_native_control(subtype) else 'NONE'

        return 'NONE'

    def _entry_uses_detached_inline_label(self, entry):
        return izom_propui_free_subtype_supports_native_control(
            self._entry_inline_native_control_subtype(entry)
        )

    def _entry_draws_indexed_inline_components(self, entry):
        component_labels = self._entry_component_labels(entry)
        if len(component_labels) <= 1:
            return False
        return self._entry_inline_native_control_subtype(entry) == 'NONE'

    def _append_indexed_component_prop_lines(self, lines, layout_var, owner_var, prop_path_expr, entry, suffix, *, base_indent=''):
        for component_index, component_label in zip(
            self._entry_component_prop_indices(entry),
            self._entry_component_labels(entry),
        ):
            lines.append(
                f"{base_indent}{layout_var}.prop({owner_var}, {prop_path_expr}, index={component_index}, text={component_label!r}{suffix})"
            )

    def _append_compact_inline_label_layout_lines(self, lines, cell_var, index, label_expr, *, base_indent=''):
        label_text_var = f"izom_propui_free_inline_label_text_{index}"
        value_col_var = f"izom_propui_free_inline_value_col_{index}"
        lines.append(f"{base_indent}{label_text_var} = str({label_expr} or '')")
        lines.append(f"{base_indent}{value_col_var} = izom_propui_free_compact_label_value_layout(context, {cell_var}, {label_text_var})")
        return value_col_var


    def _entry_uses_stacked_multi_component_layout(self, entry):
        component_labels = self._entry_component_labels(entry)
        return (
            (len(component_labels) > 1)
            and self._entry_multi_component_layout(entry) in {
                'STACKED',
                'STACKED_SPLIT_LABEL',
                'STACKED_COMPONENT_SPLIT_LABEL',
            }
        )

    def _entry_uses_inline_label_multi_component_layout(self, entry):
        component_labels = self._entry_component_labels(entry)
        return (
            (len(component_labels) > 1)
            and self._entry_multi_component_layout(entry) == 'INLINE_LABEL'
        )

    def _entry_uses_multi_component_label_above(self, entry):
        return (
            (
                self._entry_uses_stacked_multi_component_layout(entry)
                and not self._entry_uses_stacked_split_label_multi_component_layout(entry)
            )
            or self._entry_uses_inline_label_multi_component_layout(entry)
        )

    def _entry_uses_label_above(self, entry):
        return self._entry_uses_scalar_label_above(entry) or self._entry_uses_multi_component_label_above(entry)

    def _entry_uses_split_label_multi_component_layout(self, entry):
        component_labels = self._entry_component_labels(entry)
        return (
            (len(component_labels) > 1)
            and self._entry_multi_component_layout(entry) in {
                'SPLIT_LABEL',
                'STACKED_SPLIT_LABEL',
                'STACKED_COMPONENT_SPLIT_LABEL',
            }
        )

    def _entry_uses_stacked_split_label_multi_component_layout(self, entry):
        component_labels = self._entry_component_labels(entry)
        return (
            (len(component_labels) > 1)
            and self._entry_multi_component_layout(entry) == 'STACKED_SPLIT_LABEL'
        )

    def _entry_uses_stacked_component_split_label_multi_component_layout(self, entry):
        component_labels = self._entry_component_labels(entry)
        return (
            (len(component_labels) > 1)
            and self._entry_multi_component_layout(entry) == 'STACKED_COMPONENT_SPLIT_LABEL'
        )

    def _entry_uses_split_label(self, entry):
        return self._entry_uses_scalar_split_label(entry) or self._entry_uses_split_label_multi_component_layout(entry)

    def _entry_uses_shared_row_inline_array_label(self, entry):
        prop_type = str(entry.get('prop_type', 'FLOAT') or 'FLOAT').strip().upper()
        component_labels = self._entry_component_labels(entry)
        return (
            prop_type == 'ARRAY'
            and self._entry_multi_component_layout(entry) == 'INLINE'
            and (len(component_labels) > 1)
        )

    def _entry_uses_shared_row_label_above(self, entry):
        return self._entry_uses_label_above(entry) or self._entry_uses_shared_row_inline_array_label(entry)


    def _group_uses_multi_component_label_above(self, group):
        return any(self._entry_uses_shared_row_label_above(entry) for entry, _index, _condition in (group or ()))


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

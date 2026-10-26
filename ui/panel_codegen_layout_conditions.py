# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .panel_codegen_layout_common import (
    IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT,
    IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_MAX,
    IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_MIN,
    IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_UNIT_SCALE,
    _izom_propui_free_runtime_display_groups,
    izom_propui_free_log_recovered,
)

class _IzomPropUICodegenLayoutConditionsMixin:
    def _group_condition_expr(self, group):
        conditions = [condition for _entry, _index, condition in group if condition is not None]
        if not conditions:
            return None
        if any(condition is None for _entry, _index, condition in group):
            return None
        return " or ".join(f"({condition})" for condition in conditions)

    def _entry_draw_groups(self, entries, cond_by_uid):
        return _izom_propui_free_runtime_display_groups(entries, cond_by_uid)



    def _entry_row_inset_amount(self, entry, field_name):
        try:
            amount = float(
                (entry or {}).get(field_name, IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT)
                or IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT
            )
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            amount = IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT
        return max(
            float(IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_MIN),
            min(float(IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_MAX), amount),
        )

    def _group_row_insets(self, group):
        if not group:
            return (0.0, 0.0)
        first_entry, _first_index, _first_condition = group[0]
        left_depth = 0.0
        if bool(first_entry.get('row_inset_left_enabled', False)):
            left_depth = self._entry_row_inset_amount(first_entry, 'row_inset_left_amount') * float(
                IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_UNIT_SCALE
            )
        return (left_depth, 0.0)

    def _row_inset_depths(self, row_insets):
        if not row_insets:
            return (0.0, 0.0)
        try:
            left_depth, right_depth = row_insets
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            return (0.0, 0.0)
        return (max(0.0, float(left_depth or 0.0)), max(0.0, float(right_depth or 0.0)))

    def _append_row_inset_lines(self, lines, row_var, depth, *, base_indent='', side='left'):
        remaining_depth = max(0.0, float(depth or 0.0))
        chunk_index = 0
        while remaining_depth > 1e-9:
            inset_chunk = min(4.0, remaining_depth)
            inset_var = f"{row_var}_{side}_inset_{chunk_index}"
            lines.append(f"{base_indent}{inset_var} = {row_var}.row(align=True)")
            lines.append(f"{base_indent}{inset_var}.scale_x = {float(inset_chunk)!r}")
            lines.append(f"{base_indent}{inset_var}.label(text='', icon='BLANK1')")
            remaining_depth -= inset_chunk
            chunk_index += 1

    def _exact_match_condition_expr(self, value_expr, expected_value, value_kind):
        normalized_kind = str(value_kind or 'NONE').strip().upper() or 'NONE'
        if normalized_kind == 'FLOAT':
            return f"(abs(float({value_expr}) - float({expected_value!r})) <= 1e-6)"
        if normalized_kind in {'VECTOR', 'COLOR'}:
            return (
                f"(lambda _a, _b: len(_a) == len(_b) and all("
                f"abs(float(x) - float(y)) <= 1e-6 for x, y in zip(_a, _b)))"
                f"(tuple({value_expr} or ()), tuple({expected_value!r} or ()))"
            )
        if normalized_kind in {'INT_ARRAY', 'BOOL_ARRAY'}:
            return f"(tuple({value_expr} or ()) == tuple({expected_value!r} or ()))"
        if normalized_kind == 'INT':
            return f"(int({value_expr}) == int({expected_value!r}))"
        return f"({value_expr} == {expected_value!r})"

    def _numeric_match_condition_expr(self, value_expr, threshold, value_kind, *, match_mode='GREATER', range_threshold=None):
        normalized_kind = str(value_kind or 'FLOAT').strip().upper() or 'FLOAT'
        mode = str(match_mode or 'GREATER').strip().upper() or 'GREATER'
        if mode not in {'EQUAL', 'GREATER', 'LESS', 'RANGE'}:
            mode = 'GREATER'
        if mode == 'EQUAL':
            return self._exact_match_condition_expr(value_expr, threshold, normalized_kind)
        if mode == 'LESS':
            return f"({value_expr} <= {threshold!r})"
        if mode == 'RANGE':
            range_value = threshold if range_threshold is None else range_threshold
            try:
                range_lo = min(threshold, range_value)
                range_hi = max(threshold, range_value)
            except TypeError:
                range_lo = threshold
                range_hi = range_value
            return f"({range_lo!r} <= ({value_expr}) <= {range_hi!r})"
        return f"({value_expr} >= {threshold!r})"


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

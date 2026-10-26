# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from ..core.diagnostics import izom_propui_free_log_recovered
from ..core.cache import izom_propui_free_cached_entry_tree_bundle
from ..core.runtime import (
    _izom_propui_free_visibility_inheritance_scope,
)


class _IzomPropUICodegenConditionsMixin:
    def _panel_tree_state(self):
        cached = getattr(self, '_izom_propui_free_panel_tree_state', None)
        if cached is None:
            cached = izom_propui_free_cached_entry_tree_bundle(self.params).get('tree_state', {})
            self._izom_propui_free_panel_tree_state = cached
        return cached

    _VISIBILITY_CONFIG = {
        'bool_mode_attr': 'bool_child_visibility',
        'number_mode_attr': 'number_child_visibility',
        'use_component_attr': 'visibility_use_component',
        'component_index_attr': 'visibility_component_index',
        'float_value_attr': 'visibility_match_float',
        'int_value_attr': 'visibility_match_int',
        'float_range_max_attr': 'visibility_range_max_float',
        'int_range_max_attr': 'visibility_range_max_int',
    }
    def _entry_direct_condition(self, expr_bone, entry, parent, config):
        own_condition = None
        parent_type = str(parent.get('value_kind', parent.get('prop_type', 'FLOAT')) or 'FLOAT').strip().upper()

        if parent_type == 'BOOL':
            parent_expr = self._entry_value_expr(parent)
            mode = entry.get(config['bool_mode_attr'], 'ALWAYS')
            if mode == 'WHEN_TRUE':
                own_condition = parent_expr
            elif mode == 'WHEN_FALSE':
                own_condition = f"(not ({parent_expr}))"
        elif parent_type == 'FLOAT':
            parent_expr = self._entry_value_expr(parent)
            mode = entry.get(config['number_mode_attr'], 'ALWAYS')
            value = float(entry.get(config['float_value_attr'], 0.0))
            if mode == 'EQUAL':
                own_condition = f"(({parent_expr}) == {value!r})"
            elif mode == 'GREATER':
                own_condition = f"(({parent_expr}) >= {value!r})"
            elif mode == 'LESS':
                own_condition = f"(({parent_expr}) <= {value!r})"
            elif mode == 'RANGE':
                range_other = float(entry.get(config['float_range_max_attr'], value))
                range_lo = min(value, range_other)
                range_hi = max(value, range_other)
                own_condition = f"({range_lo!r} <= ({parent_expr}) <= {range_hi!r})"
        elif parent_type == 'INT':
            parent_expr = self._entry_value_expr(parent)
            mode = entry.get(config['number_mode_attr'], 'ALWAYS')
            value = int(entry.get(config['int_value_attr'], 0))
            if mode == 'EQUAL':
                own_condition = f"(({parent_expr}) == {value!r})"
            elif mode == 'GREATER':
                own_condition = f"(({parent_expr}) >= {value!r})"
            elif mode == 'LESS':
                own_condition = f"(({parent_expr}) <= {value!r})"
            elif mode == 'RANGE':
                range_other = int(entry.get(config['int_range_max_attr'], value))
                range_lo = min(value, range_other)
                range_hi = max(value, range_other)
                own_condition = f"({range_lo!r} <= ({parent_expr}) <= {range_hi!r})"
        elif parent_type in {'COLOR', 'VECTOR', 'INT_ARRAY', 'BOOL_ARRAY'}:
            mode = str(entry.get(config['number_mode_attr'], 'ALWAYS') or 'ALWAYS').strip().upper()
            if bool(entry.get(config.get('use_component_attr', ''), False)):
                try:
                    component_slot = max(1, int(entry.get(config.get('component_index_attr', ''), 1) or 1))
                except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                    izom_propui_free_log_recovered(
                        category='UI',
                        exception=exc,
                    )
                    component_slot = 1
                component_index = component_slot - 1
                component_kind = 'BOOL' if parent_type == 'BOOL_ARRAY' else ('INT_ARRAY' if parent_type == 'INT_ARRAY' else parent_type)
                parent_subtype = self._entry_inline_native_control_subtype(parent) if parent_type in {'COLOR', 'VECTOR'} else 'NONE'
                if component_kind == 'BOOL':
                    parent_expr = self._bool_component_expr(
                        self._entry_value_expr(parent),
                        component_index,
                    )
                    bool_mode = entry.get(config['bool_mode_attr'], 'ALWAYS')
                    if bool_mode == 'WHEN_TRUE':
                        own_condition = parent_expr
                    elif bool_mode == 'WHEN_FALSE':
                        own_condition = f"(not ({parent_expr}))"
                else:
                    parent_expr = self._numeric_component_expr(
                        self._entry_value_expr(parent),
                        component_index,
                        component_kind,
                        visible_color_subtype=parent_subtype,
                    )
                if component_kind == 'INT_ARRAY':
                    value = int(entry.get(config['int_value_attr'], 0))
                    if mode == 'EQUAL':
                        own_condition = f"(({parent_expr}) == {value!r})"
                    elif mode == 'GREATER':
                        own_condition = f"(({parent_expr}) >= {value!r})"
                    elif mode == 'LESS':
                        own_condition = f"(({parent_expr}) <= {value!r})"
                    elif mode == 'RANGE':
                        range_other = int(entry.get(config['int_range_max_attr'], value))
                        range_lo = min(value, range_other)
                        range_hi = max(value, range_other)
                        own_condition = f"({range_lo!r} <= ({parent_expr}) <= {range_hi!r})"
                elif component_kind != 'BOOL':
                    value = float(entry.get(config['float_value_attr'], 0.0))
                    if mode == 'EQUAL':
                        own_condition = f"(({parent_expr}) == {value!r})"
                    elif mode == 'GREATER':
                        own_condition = f"(({parent_expr}) >= {value!r})"
                    elif mode == 'LESS':
                        own_condition = f"(({parent_expr}) <= {value!r})"
                    elif mode == 'RANGE':
                        range_other = float(entry.get(config['float_range_max_attr'], value))
                        range_lo = min(value, range_other)
                        range_hi = max(value, range_other)
                        own_condition = f"({range_lo!r} <= ({parent_expr}) <= {range_hi!r})"
            elif mode != 'ALWAYS':
                parent_expr = self._entry_value_expr(parent)
                own_condition = self._exact_match_condition_expr(
                    parent_expr,
                    self._entry_exact_match_compare_value(entry, config, parent_type, reference_entry=parent),
                    parent_type,
                )
        elif parent_type == 'BOOL_ARRAY':
            parent_expr = self._entry_value_expr(parent)
            mode = str(entry.get(config['number_mode_attr'], 'ALWAYS') or 'ALWAYS').strip().upper()
            if mode != 'ALWAYS':
                own_condition = self._exact_match_condition_expr(
                    parent_expr,
                    self._entry_exact_match_compare_value(entry, config, parent_type, reference_entry=parent),
                    parent_type,
                )

        return own_condition

    def _entry_direct_visibility_condition(self, expr_bone, entry, parent):
        return self._entry_direct_condition(expr_bone, entry, parent, self._VISIBILITY_CONFIG)

    def _build_visibility_conditions(self, panel, entries):
        layout_by_uid = {
            str(entry.get('uid', '') or '').strip(): entry
            for entry in entries
            if str(entry.get('uid', '') or '').strip()
        }
        state = self._panel_tree_state()
        by_uid = {
            str(entry.get('uid', '') or '').strip(): entry
            for entry in state.get('snapshots', [])
            if str(entry.get('uid', '') or '').strip()
        }
        by_uid.update(layout_by_uid)
        cond_by_uid = {}

        for entry in entries:
            entry_uid = str(entry.get('uid', '') or '').strip()
            if not entry_uid:
                continue

            scope = _izom_propui_free_visibility_inheritance_scope(
                self.params,
                entry,
                state=state,
            )
            current_entry = entry
            conditions = []

            for ancestor in scope.get('applied_ancestors', []) or []:
                ancestor_uid = str(ancestor.get('uid', '') or '').strip()
                parent = by_uid.get(ancestor_uid, ancestor)
                condition = self._entry_direct_visibility_condition(None, current_entry, parent)
                if condition is not None:
                    conditions.append(f"({condition})")
                current_entry = parent

            cond_by_uid[entry_uid] = " and ".join(conditions) if conditions else None

        return cond_by_uid

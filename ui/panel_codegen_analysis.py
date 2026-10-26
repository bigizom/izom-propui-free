# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import izom_propui_free_log_recovered
from ..core.constants import (
    IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT,
    IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_MAX,
    IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_MIN,
)
from ..core.text import (
    izom_propui_free_shorten_ui_text,
)
from ..core.value_labels import (
    _izom_propui_free_build_dynamic_label_spec,
    _izom_propui_free_is_numeric_type,
)
from ..core.value_access import (
    izom_propui_free_entry_array_element_type,
    izom_propui_free_entry_array_field_name,
    izom_propui_free_entry_array_visible_value,
    izom_propui_free_entry_value_kind,
)

_IZOM_PROPUI_FREE_CODEGEN_ANALYSIS_VALUE_ERRORS = (
    AttributeError,
    TypeError,
    ValueError,
    SyntaxError,
)


class _IzomPropUICodegenAnalysisMixin:
    def _entry_owner_path(self, entry):
        return str(getattr(self, 'target_owner_path', '') or '').strip()

    def _entry_value_kind(self, entry):
        prop_type = str(entry.get('prop_type', 'FLOAT') or 'FLOAT').strip().upper() or 'FLOAT'
        return str(izom_propui_free_entry_value_kind(entry, prop_type) or prop_type).strip().upper() or prop_type

    def _entry_default_value(self, entry):
        prop_type = str(entry.get('prop_type', 'FLOAT') or 'FLOAT').strip().upper()
        value_kind = self._entry_value_kind(entry)
        if value_kind == 'BOOL':
            return bool(entry.get('default_bool', False))
        if value_kind == 'INT':
            return int(entry.get('default_int', 0))
        if value_kind == 'FLOAT':
            return float(entry.get('default_float', 0.0))
        if value_kind in {'COLOR', 'VECTOR', 'INT_ARRAY', 'BOOL_ARRAY'}:
            if prop_type == 'ARRAY':
                visible_value = tuple(izom_propui_free_entry_array_visible_value(entry, 'default'))
                if value_kind in {'COLOR', 'VECTOR'}:
                    return tuple(float(component) for component in visible_value)
                if value_kind == 'INT_ARRAY':
                    return tuple(int(component) for component in visible_value)
                return tuple(bool(component) for component in visible_value)
            if value_kind == 'INT_ARRAY':
                return tuple(int(component) for component in (entry.get('default_int_array', ()) or ()))
            if value_kind == 'BOOL_ARRAY':
                return tuple(bool(component) for component in (entry.get('default_bool_array', ()) or ()))
            return tuple(float(component) for component in (entry.get('default_float_array', (1.0, 1.0, 1.0, 1.0)) or (1.0, 1.0, 1.0, 1.0)))
        return ''

    def _entry_row_height_scale(self, entry):
        try:
            value = float((entry or {}).get('row_height_scale', IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT) or IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT)
        except _IZOM_PROPUI_FREE_CODEGEN_ANALYSIS_VALUE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            value = IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT
        return max(
            IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_MIN,
            min(IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_MAX, value),
        )

    def _append_row_height_scale_lines(self, lines, row_var, entry, *, base_indent=''):
        row_height_scale = self._entry_row_height_scale(entry)
        if abs(row_height_scale - IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT) > 1e-6:
            lines.append(f"{base_indent}{row_var}.scale_y = {row_height_scale!r}")

    def _group_supports_row_height_scale(self, group):
        return bool(group)

    def _append_group_row_height_scale_lines(self, lines, row_var, group, *, base_indent=''):
        if not self._group_supports_row_height_scale(group):
            return
        first_entry = (group or (({}, 0, None),))[0][0]
        self._append_row_height_scale_lines(lines, row_var, first_entry, base_indent=base_indent)

    def _entry_exact_match_compare_value(self, entry, config, value_kind, reference_entry=None):
        normalized_kind = str(value_kind or 'NONE').strip().upper() or 'NONE'
        if normalized_kind in {'COLOR', 'VECTOR', 'INT_ARRAY', 'BOOL_ARRAY'}:
            field_name = config['float_value_attr'].replace('_float', '_float_array')
            if normalized_kind == 'INT_ARRAY':
                field_name = config['float_value_attr'].replace('_float', '_int_array')
            elif normalized_kind == 'BOOL_ARRAY':
                field_name = config['float_value_attr'].replace('_float', '_bool_array')
            reference = reference_entry if isinstance(reference_entry, dict) else entry
            if str(reference.get('prop_type', 'FLOAT') or 'FLOAT').strip().upper() == 'ARRAY':
                reference_element_type = izom_propui_free_entry_array_element_type(reference, 'FLOAT')
                field_name = izom_propui_free_entry_array_field_name(config['float_value_attr'].replace('_float', ''), reference_element_type)
                visible_value = tuple(
                    izom_propui_free_entry_array_visible_value(
                        dict(reference, **{field_name: entry.get(field_name, ())}),
                        field_name,
                        default=entry.get(field_name, ()),
                    )
                )
                if normalized_kind in {'COLOR', 'VECTOR'}:
                    return tuple(float(component) for component in visible_value)
                if normalized_kind == 'INT_ARRAY':
                    return tuple(int(component) for component in visible_value)
                return tuple(bool(component) for component in visible_value)
            if normalized_kind == 'INT_ARRAY':
                return tuple(int(component) for component in (entry.get(field_name, ()) or ()))
            if normalized_kind == 'BOOL_ARRAY':
                return tuple(bool(component) for component in (entry.get(field_name, ()) or ()))
            return tuple(float(component) for component in (entry.get(field_name, (1.0, 1.0, 1.0, 1.0)) or (1.0, 1.0, 1.0, 1.0)))
        field_name = config['float_value_attr'].replace('_float', '_text')
        return str(entry.get(field_name, '') or '')

    def _entry_value_expr(self, entry):
        prop_type = str(entry.get('prop_type', 'FLOAT') or 'FLOAT').strip().upper()
        if prop_type == 'TEXT':
            return "None"

        default_value = self._entry_default_value(entry)

        prop_id = str(entry.get('prop_id', '') or '').strip()
        owner_path = self._entry_owner_path(entry)
        return f"(target_owners.get({owner_path!r}, {{}}).get({prop_id!r}, {default_value!r}))"

    def _numeric_component_expr(self, value_expr, component_index, numeric_kind, *, visible_color_subtype='NONE'):
        normalized_kind = str(numeric_kind or 'FLOAT').strip().upper() or 'FLOAT'
        if normalized_kind in {'INT', 'INT_ARRAY'}:
            cast_name = 'int'
            default_value = 0
        else:
            cast_name = 'float'
            default_value = 0.0

        try:
            resolved_index = max(0, int(component_index))
        except _IZOM_PROPUI_FREE_CODEGEN_ANALYSIS_VALUE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            resolved_index = 0

        component_expr = (
            f"(lambda _value: (lambda _seq: ({cast_name}(_seq[{resolved_index}]) "
            f"if len(_seq) > {resolved_index} else {default_value!r}))"
            f"(tuple(_value) if _value is not None else ()))({value_expr})"
        )
        normalized_subtype = str(visible_color_subtype or 'NONE').strip().upper() or 'NONE'
        if normalized_kind == 'COLOR' and normalized_subtype == 'COLOR':
            return (
                f"(lambda _channel: (12.92 * _channel if _channel <= 0.0031308 else "
                f"(1.055 * pow(_channel, (1.0 / 2.4)) - 0.055)))"
                f"(max(0.0, float({component_expr})))"
            )
        return component_expr

    def _bool_component_expr(self, value_expr, component_index):
        try:
            resolved_index = max(0, int(component_index))
        except _IZOM_PROPUI_FREE_CODEGEN_ANALYSIS_VALUE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            resolved_index = 0
        return (
            f"(lambda _value: (lambda _seq: (bool(_seq[{resolved_index}]) "
            f"if len(_seq) > {resolved_index} else False))"
            f"(tuple(_value) if _value is not None else ()))({value_expr})"
        )

    def _display_text_literal(self, value):
        return repr(izom_propui_free_shorten_ui_text(value, limit=None))

    def _dynamic_label_spec(self, entry):
        prop_id = str(entry.get('prop_id', '') or '').strip()
        cache = getattr(self, '_izom_propui_free_dynamic_label_spec_cache', None)
        if cache is None:
            cache = {}
            self._izom_propui_free_dynamic_label_spec_cache = cache
        cache_key = str(entry.get('uid', '') or '').strip() or prop_id or str(id(entry))
        if cache_key not in cache:
            cache[cache_key] = _izom_propui_free_build_dynamic_label_spec(entry, prop_id)
        return cache[cache_key]

    def _entry_has_dynamic_prop_labels(self, entry):
        return bool(self._dynamic_label_spec(entry).get('has_dynamic_label'))

    def _rule_kind(self, rule):
        return str(rule.get('rule_kind', 'LABEL') or 'LABEL').strip().upper()

    def _rule_has_display_action(self, rule):
        if self._rule_kind(rule) == 'FALLBACK':
            return True
        if str(rule.get('label', '') or '').strip():
            return True
        return False

    def _effective_value_bucket_items(self, spec):
        return [
            item for item in (spec.get('value_buckets', []) or [])
            if self._rule_has_display_action(item)
        ]

    def _entry_codegen_analysis(self, entry):
        cache = getattr(self, '_izom_propui_free_entry_codegen_analysis_cache', None)
        if cache is None:
            cache = {}
            self._izom_propui_free_entry_codegen_analysis_cache = cache

        cache_key = id(entry)
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        prop_type = str(entry.get('prop_type', '') or '')
        needs_current_bool = False
        needs_current_value = False

        if prop_type != 'TEXT':
            spec = self._dynamic_label_spec(entry)
            value_kind = str(spec.get('value_kind', spec.get('prop_type', 'FLOAT')) or 'FLOAT').strip().upper()
            if value_kind == 'BOOL':
                needs_current_bool = bool(spec.get('bool_states'))
            elif _izom_propui_free_is_numeric_type(value_kind) or value_kind in {'COLOR', 'VECTOR', 'INT_ARRAY', 'BOOL_ARRAY'}:
                effective_buckets = self._effective_value_bucket_items(spec)
                needs_current_value = bool(effective_buckets)

        cached = {
            'source_reads': (),
            'needs_source_reads': False,
            'needs_current_bool': needs_current_bool,
            'needs_current_value': needs_current_value,
        }
        cache[cache_key] = cached
        return cached

    def _group_codegen_analysis(self, group):
        cache = getattr(self, '_izom_propui_free_group_codegen_analysis_cache', None)
        if cache is None:
            cache = {}
            self._izom_propui_free_group_codegen_analysis_cache = cache

        cache_key = tuple((id(entry), index) for entry, index, _condition in (group or []))
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        source_reads = {}
        for entry, _index, _condition in group or []:
            entry_analysis = self._entry_codegen_analysis(entry)
            for source_spec in entry_analysis.get('source_reads', ()) or ():
                if source_spec['key'] not in source_reads:
                    source_reads[source_spec['key']] = source_spec

        cached = {
            'source_reads': tuple(source_reads.values()),
            'needs_source_reads': bool(source_reads),
        }
        cache[cache_key] = cached
        return cached

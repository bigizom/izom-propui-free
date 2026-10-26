# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
import ast

from ..core.diagnostics import izom_propui_free_log_recovered
from ..core.text import (
    izom_propui_free_text_block_has_output,
    izom_propui_free_text_block_state,
)
from ..core.value_labels import (
    _izom_propui_free_is_numeric_type,
    _izom_propui_free_normalize_bool_state,
)


class _IzomPropUICodegenRuleTextMixin:
    def _append_group_source_read_lines(self, lines, group, token, *, base_indent='', bone_var=None):
        analysis = self._group_codegen_analysis(group)
        source_reads = analysis.get('source_reads', ()) or ()
        if not source_reads:
            return {}

        source_value_vars = {}
        for read_index, source_spec in enumerate(source_reads):
            value_var = f"izom_propui_free_source_value_{token}_{read_index}"
            default_value = source_spec['default_value']
            source_entry = source_spec.get('source_entry', {})
            read_expr = self._entry_value_expr(source_entry)
            if source_spec['source_type'] == 'BOOL':
                if source_spec.get('use_source_component'):
                    lines.append(
                        f"{base_indent}{value_var} = {self._bool_component_expr(read_expr, source_spec.get('source_component_index', 0))}"
                    )
                else:
                    lines.append(f"{base_indent}{value_var} = bool({read_expr})")
            elif source_spec.get('use_source_component') and _izom_propui_free_is_numeric_type(source_spec['source_type']):
                lines.append(
                    f"{base_indent}{value_var} = {self._numeric_component_expr(read_expr, source_spec.get('source_component_index', 0), source_spec['source_type'])}"
                )
            else:
                lines.append(f"{base_indent}{value_var} = {read_expr}")
            source_value_vars[source_spec['key']] = value_var

        return source_value_vars

    def _append_ordered_rule_iteration_lines(
        self,
        lines,
        rules,
        index,
        *,
        text_mode=False,
        base_indent='',
        source_value_vars=None,
        skip_fallback=False,
        emit_match_action,
    ):
        prefix = 'izom_propui_free_text_rule_matched' if text_mode else 'izom_propui_free_rule_matched'
        matched_var = f"{prefix}_{str(index).replace('-', '_')}"
        # Pre-filter valid rules
        valid_rules = []
        for rule in (rules or []):
            source_spec = self._rule_source_read_spec(rule, text_mode=text_mode)
            if source_spec is None:
                continue
            if skip_fallback and self._rule_kind(rule) == 'FALLBACK':
                continue
            valid_rules.append((rule, source_spec))
        if not valid_rules:
            return
        use_matched_var = len(valid_rules) > 1
        if use_matched_var:
            lines.append(f"{base_indent}{matched_var} = False")
        for rule_index, (rule, source_spec) in enumerate(valid_rules):
            rule_kind = self._rule_kind(rule)
            conditions = []
            source_type = source_spec['source_type']
            if source_type == 'BOOL':
                source_expr = None
                if source_value_vars:
                    source_expr = source_value_vars.get(source_spec['key'])
                if not source_expr:
                    source_read_expr = self._entry_value_expr(source_spec.get('source_entry', {}))
                    if source_spec.get('use_source_component'):
                        source_expr = self._bool_component_expr(source_read_expr, source_spec.get('source_component_index', 0))
                    else:
                        source_expr = f"bool({source_read_expr})"
                if _izom_propui_free_normalize_bool_state(rule.get('source_bool_state', 'WHEN_TRUE')) == 'WHEN_FALSE':
                    conditions.append(f"not ({source_expr})")
                else:
                    conditions.append(f"({source_expr})")
                condition_expr = " and ".join(conditions)
                if not condition_expr:
                    continue
                guard_expr = f"(not {matched_var}) and " if use_matched_var else ""
                lines.append(f"{base_indent}if {guard_expr}({condition_expr}):")
                emit_match_action(lines, rule, rule_kind, base_indent + '    ')
                if use_matched_var:
                    lines.append(f"{base_indent}    {matched_var} = True")
                continue

            threshold = rule.get('threshold')
            source_value_var = source_value_vars.get(source_spec['key']) if source_value_vars else None
            if source_value_var is None:
                source_value_var = f"izom_propui_free_rule_source_value_{index}_{rule_index}"
                source_read_expr = self._entry_value_expr(source_spec.get('source_entry', {}))
                if source_spec.get('use_source_component') and _izom_propui_free_is_numeric_type(source_type):
                    lines.append(
                        f"{base_indent}{source_value_var} = {self._numeric_component_expr(source_read_expr, source_spec.get('source_component_index', 0), source_type)}"
                    )
                else:
                    lines.append(f"{base_indent}{source_value_var} = {source_read_expr}")
            if _izom_propui_free_is_numeric_type(source_type):
                if threshold is None:
                    continue
                conditions.append(self._numeric_match_condition_expr(
                    source_value_var,
                    threshold,
                    source_type,
                    match_mode=rule.get('match_mode', 'GREATER'),
                    range_threshold=rule.get('range_threshold'),
                ))
            else:
                match_value = rule.get('match_value')
                if match_value is None:
                    continue
                conditions.append(self._exact_match_condition_expr(source_value_var, match_value, source_type))
            condition_expr = " and ".join(conditions)
            guard_expr = f"(not {matched_var}) and " if use_matched_var else ""
            lines.append(f"{base_indent}if {guard_expr}({condition_expr}):")
            emit_match_action(lines, rule, rule_kind, base_indent + '    ')
            if use_matched_var:
                lines.append(f"{base_indent}    {matched_var} = True")

    def _text_state_vars(self, text_var):
        return {
            'text': text_var,
            'alignment': f"{text_var}_alignment",
            'role': f"{text_var}_role",
            'alert': f"{text_var}_alert",
            'icon_before': f"{text_var}_icon_before",
            'icon_before_hug_text': f"{text_var}_icon_before_hug_text",
            'icon_after': f"{text_var}_icon_after",
            'icon_after_hug_text': f"{text_var}_icon_after_hug_text",
        }

    def _append_text_state_assignment_lines(self, lines, item, text_var, *, base_indent=''):
        state_vars = self._text_state_vars(text_var)
        state = izom_propui_free_text_block_state(item)
        lines.append(f"{base_indent}{state_vars['text']} = {self._display_text_literal(state.get('display_text', ''))}")
        lines.append(f"{base_indent}{state_vars['alignment']} = {state.get('text_alignment', 'LEFT')!r}")
        lines.append(f"{base_indent}{state_vars['role']} = {state.get('text_role', 'TEXT')!r}")
        lines.append(f"{base_indent}{state_vars['alert']} = {bool(state.get('text_alert', False))!r}")
        lines.append(f"{base_indent}{state_vars['icon_before']} = {state.get('text_icon', 'NONE')!r}")
        lines.append(f"{base_indent}{state_vars['icon_before_hug_text']} = {bool(state.get('text_icon_hug_text', True))!r}")
        lines.append(f"{base_indent}{state_vars['icon_after']} = {state.get('text_icon_after', 'NONE')!r}")
        lines.append(f"{base_indent}{state_vars['icon_after_hug_text']} = {bool(state.get('text_icon_after_hug_text', True))!r}")
        return state_vars

    def _append_text_state_backup_lines(self, lines, state_vars, *, base_indent=''):
        backup_vars = {}
        for key, var_name in state_vars.items():
            backup_name = f"{var_name}_base"
            lines.append(f"{base_indent}{backup_name} = {var_name}")
            backup_vars[key] = backup_name
        return backup_vars

    def _append_text_state_restore_lines(self, lines, state_vars, backup_vars, *, base_indent=''):
        for key, var_name in state_vars.items():
            lines.append(f"{base_indent}{var_name} = {backup_vars[key]}")

    def _append_text_label_cluster_lines(
        self,
        lines,
        label_row_var,
        label_cluster_var,
        *,
        alignment_expr,
        icon_before_expr,
        icon_before_hug_expr,
        icon_after_expr,
        icon_after_hug_expr,
        text_lines,
        dynamic_icons=False,
        base_indent='',
    ):
        icon_detach_alignment_expr = f"({alignment_expr} == 'CENTER')"
        static_icon_detach_allowed = str(alignment_expr).strip().strip("'\"").upper() == 'CENTER'
        if dynamic_icons:
            lines.append(f"{base_indent}if {icon_before_expr} != 'NONE' and {icon_detach_alignment_expr} and not {icon_before_hug_expr}:")
            lines.append(f"{base_indent}    {label_row_var}.label(text='', icon={icon_before_expr})")
        elif icon_before_expr != 'NONE' and static_icon_detach_allowed and not bool(icon_before_hug_expr):
            lines.append(f"{base_indent}{label_row_var}.label(text='', icon={icon_before_expr!r})")

        lines.append(f"{base_indent}{label_cluster_var} = {label_row_var}.row(align=True)")
        lines.append(f"{base_indent}{label_cluster_var}.alignment = {alignment_expr}")

        if dynamic_icons:
            lines.append(f"{base_indent}if {icon_before_expr} != 'NONE' and ({icon_before_hug_expr} or not {icon_detach_alignment_expr}):")
            lines.append(f"{base_indent}    {label_cluster_var}.label(text='', icon={icon_before_expr})")
        elif icon_before_expr != 'NONE' and (bool(icon_before_hug_expr) or not static_icon_detach_allowed):
            lines.append(f"{base_indent}{label_cluster_var}.label(text='', icon={icon_before_expr!r})")

        lines.extend(text_lines)

        if dynamic_icons:
            lines.append(f"{base_indent}if {icon_after_expr} != 'NONE' and ({icon_after_hug_expr} or not {icon_detach_alignment_expr}):")
            lines.append(f"{base_indent}    {label_cluster_var}.label(text='', icon={icon_after_expr})")
            lines.append(f"{base_indent}if {icon_after_expr} != 'NONE' and {icon_detach_alignment_expr} and not {icon_after_hug_expr}:")
            lines.append(f"{base_indent}    {label_row_var}.label(text='', icon={icon_after_expr})")
        else:
            if icon_after_expr != 'NONE' and (bool(icon_after_hug_expr) or not static_icon_detach_allowed):
                lines.append(f"{base_indent}{label_cluster_var}.label(text='', icon={icon_after_expr!r})")
            if icon_after_expr != 'NONE' and static_icon_detach_allowed and not bool(icon_after_hug_expr):
                lines.append(f"{base_indent}{label_row_var}.label(text='', icon={icon_after_expr!r})")

    def _append_static_text_block_render_lines(self, lines, layout_var, token, item, *, text_expr=None, base_indent=''):
        state = izom_propui_free_text_block_state(item)
        has_text_expr = bool(str(text_expr or '').strip())
        if not izom_propui_free_text_block_has_output(state) and not has_text_expr:
            return

        text_role = str(state.get('text_role', 'TEXT') or 'TEXT').strip().upper() or 'TEXT'
        icon_before = str(state.get('text_icon', 'NONE') or 'NONE').strip().upper() or 'NONE'
        icon_before_hug_text = bool(state.get('text_icon_hug_text', True))
        icon_after = str(state.get('text_icon_after', 'NONE') or 'NONE').strip().upper() or 'NONE'
        icon_after_hug_text = bool(state.get('text_icon_after_hug_text', True))
        display_text = self._display_text_literal(state.get('display_text', ''))
        rendered_text_expr = str(text_expr or '').strip() or display_text
        text_alert = bool(state.get('text_alert', False))
        literal_text_expr = None
        if has_text_expr:
            try:
                literal_value = ast.literal_eval(rendered_text_expr)
            except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
                )
                literal_value = None
            if isinstance(literal_value, str):
                literal_text_expr = literal_value

        if text_role == 'DIVIDER':
            lines.append(f"{base_indent}{layout_var}.separator(type='LINE')")
            return
        if text_role == 'SPACER':
            lines.append(f"{base_indent}{layout_var}.label(text='')")
            return
        if text_role != 'TEXT':
            return

        block_var = f"izom_propui_free_text_block_{token}"

        lines.append(f"{base_indent}{block_var} = {layout_var}.column(align=True)")
        if text_alert:
            lines.append(f"{base_indent}{block_var}.alert = True")

        has_literal_text = literal_text_expr is not None and bool(str(literal_text_expr or '').strip())
        has_dynamic_text = has_text_expr and literal_text_expr is None
        if has_dynamic_text or has_literal_text or str(state.get('display_text', '') or '').strip() or icon_before != 'NONE' or icon_after != 'NONE':
            label_row_var = f"{block_var}_label"
            label_cluster_var = f"{label_row_var}_cluster"
            lines.append(f"{base_indent}{label_row_var} = {block_var}.row(align=True)")
            alignment = str(state.get('text_alignment', 'LEFT') or 'LEFT').strip().upper() or 'LEFT'
            text_lines = []
            if literal_text_expr is not None:
                if has_literal_text:
                    text_lines.append(f"{base_indent}{label_cluster_var}.label(text={literal_text_expr!r})")
            elif has_text_expr:
                text_lines.append(f"{base_indent}if {rendered_text_expr}:")
                text_lines.append(f"{base_indent}    {label_cluster_var}.label(text={rendered_text_expr})")
            elif str(state.get('display_text', '') or '').strip():
                text_lines.append(f"{base_indent}{label_cluster_var}.label(text={rendered_text_expr})")
            self._append_text_label_cluster_lines(
                lines,
                label_row_var,
                label_cluster_var,
                alignment_expr=repr(alignment),
                icon_before_expr=icon_before,
                icon_before_hug_expr=icon_before_hug_text,
                icon_after_expr=icon_after,
                icon_after_hug_expr=icon_after_hug_text,
                text_lines=text_lines,
                base_indent=base_indent,
            )

    def _append_text_block_render_lines(self, lines, layout_var, token, state_vars, *, base_indent=''):
        output_condition = (
            f"({state_vars['role']} in {{'DIVIDER', 'SPACER'}} "
            f"or ({state_vars['role']} == 'TEXT' and ({state_vars['text']} or {state_vars['icon_before']} != 'NONE' or {state_vars['icon_after']} != 'NONE')) "
            f")"
        )
        block_var = f"izom_propui_free_text_block_{token}"
        label_row_var = f"{block_var}_label"
        label_cluster_var = f"{label_row_var}_cluster"
        lines.append(f"{base_indent}if {output_condition}:")
        lines.append(f"{base_indent}    {block_var} = {layout_var}.column(align=True)")
        lines.append(f"{base_indent}    {block_var}.alert = bool({state_vars['alert']})")
        text_row_condition = (
            f"({state_vars['role']} == 'TEXT' and "
            f"({state_vars['text']} or {state_vars['icon_before']} != 'NONE' or {state_vars['icon_after']} != 'NONE'))"
        )
        lines.append(f"{base_indent}    if {state_vars['role']} == 'DIVIDER':")
        lines.append(f"{base_indent}        {block_var}.separator(type='LINE')")
        lines.append(f"{base_indent}    elif {state_vars['role']} == 'SPACER':")
        lines.append(f"{base_indent}        {block_var}.label(text='')")
        lines.append(f"{base_indent}    elif {text_row_condition}:")
        lines.append(f"{base_indent}        {label_row_var} = {block_var}.row(align=True)")
        self._append_text_label_cluster_lines(
            lines,
            label_row_var,
            label_cluster_var,
            alignment_expr=state_vars['alignment'],
            icon_before_expr=state_vars['icon_before'],
            icon_before_hug_expr=state_vars['icon_before_hug_text'],
            icon_after_expr=state_vars['icon_after'],
            icon_after_hug_expr=state_vars['icon_after_hug_text'],
            text_lines=[f"{base_indent}        {label_cluster_var}.label(text={state_vars['text']})"],
            dynamic_icons=True,
            base_indent=base_indent + '        ',
        )

    def _append_dynamic_prop_label_lines(
        self,
        lines,
        entry,
        index,
        target_var,
        *,
        bone_var=None,
        source_value_vars=None,
        base_indent='',
    ):
        spec = self._dynamic_label_spec(entry)
        entry_analysis = self._entry_codegen_analysis(entry)
        value_kind = str(spec.get('value_kind', spec.get('prop_type', 'FLOAT')) or 'FLOAT').strip().upper()
        current_value_expr = self._entry_value_expr(entry)
        base_label_expr = self._display_text_literal(spec.get('base_label', ''))
        lines.append(f"{base_indent}{target_var} = {self._display_text_literal(spec.get('base_label', ''))}")

        value_expr = None
        if value_kind == 'BOOL' and entry_analysis.get('needs_current_bool'):
            value_expr = f"izom_propui_free_prop_bool_value_{index}"
            lines.append(f"{base_indent}{value_expr} = bool({current_value_expr})")
        if value_kind == 'BOOL' and spec.get('bool_states'):
            resolved_state_labels = spec['bool_states']
            lines.append(f"{base_indent}{target_var} = {self._display_text_literal(resolved_state_labels[False]['label'])}")
            lines.append(f"{base_indent}if {value_expr}:")
            lines.append(f"{base_indent}    {target_var} = {self._display_text_literal(resolved_state_labels[True]['label'])}")
        elif (_izom_propui_free_is_numeric_type(value_kind) or value_kind in {'COLOR', 'VECTOR', 'INT_ARRAY', 'BOOL_ARRAY'}) and spec.get('value_buckets'):
            value_labels = self._effective_value_bucket_items(spec)
            if value_labels:
                value_var = f"izom_propui_free_prop_label_value_{index}"
                matched_bucket_var = f"izom_propui_free_value_label_bucket_matched_{index}"
                lines.append(f"{base_indent}{value_var} = {current_value_expr}")
                lines.append(f"{base_indent}{matched_bucket_var} = False")
                for bucket_index, item in enumerate(value_labels):
                    bucket_indent = base_indent + '    '
                    item_kind = str(item.get('value_kind', value_kind) or value_kind).strip().upper()
                    item_value_expr = value_var
                    if bool(item.get('use_component', False)) and item_kind == 'BOOL':
                        item_value_expr = self._bool_component_expr(
                            value_var,
                            item.get('component_index', 0),
                        )
                    elif bool(item.get('use_component', False)) and _izom_propui_free_is_numeric_type(item_kind):
                        item_value_expr = self._numeric_component_expr(
                            value_var,
                            item.get('component_index', 0),
                            item.get('source_value_kind', value_kind),
                        )
                    if _izom_propui_free_is_numeric_type(item_kind):
                        condition_expr = self._numeric_match_condition_expr(
                            item_value_expr,
                            item['threshold'],
                            item_kind,
                            match_mode=item.get('match_mode', 'GREATER'),
                            range_threshold=item.get('range_threshold'),
                        )
                        lines.append(f"{base_indent}if (not {matched_bucket_var}) and ({condition_expr}):")
                    elif item_kind == 'BOOL':
                        if _izom_propui_free_normalize_bool_state(item.get('source_bool_state', 'WHEN_TRUE')) == 'WHEN_FALSE':
                            lines.append(f"{base_indent}if (not {matched_bucket_var}) and (not ({item_value_expr})):")
                        else:
                            lines.append(f"{base_indent}if (not {matched_bucket_var}) and ({item_value_expr}):")
                    else:
                        lines.append(
                            f"{base_indent}if (not {matched_bucket_var}) and ({self._exact_match_condition_expr(item_value_expr, item.get('match_value'), item_kind)}):"
                        )
                    if self._rule_kind(item) == 'FALLBACK':
                        lines.append(f"{bucket_indent}{target_var} = {base_label_expr}")
                    else:
                        base_bucket_label = str(item.get('label', '') or '').strip()
                        if base_bucket_label:
                            lines.append(f"{bucket_indent}{target_var} = {self._display_text_literal(base_bucket_label)}")
                    lines.append(f"{bucket_indent}{matched_bucket_var} = True")

# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .draw_common_base import (
    izom_propui_free_entry_array_element_type,
    izom_propui_free_entry_array_subtype,
    izom_propui_free_log_recovered,
)
from ..core.float_arrays import (
    izom_propui_free_array_value_kind,
    izom_propui_free_normalize_array_element_type,
    izom_propui_free_normalize_array_size,
    izom_propui_free_normalize_float_array_subtype,
)
from ..core.value_access_common import (
    izom_propui_free_entry_array_component_labels,
    izom_propui_free_is_exact_match_value_kind,
)
from ..core.value_access_entries import (
    izom_propui_free_entry_array_field_name,
    izom_propui_free_entry_array_size,
    izom_propui_free_entry_component_meta,
)
from .helper_field_clamp_common import _izom_propui_free_editor_float_settings
from .helper_field_clamp_numeric import _izom_propui_free_draw_editor_float_prop
from .model_proxies_color import _izom_propui_free_float_array_color_proxy_name
from .model_proxies_components import _izom_propui_free_array_component_proxy_name



def _izom_propui_free_exact_match_array_meta(reference_entry, value_kind):
    normalized_kind = str(value_kind or 'NONE').strip().upper() or 'NONE'
    if reference_entry is not None and normalized_kind in {'COLOR', 'VECTOR', 'INT_ARRAY', 'BOOL_ARRAY'}:
        component_meta = izom_propui_free_entry_component_meta(reference_entry, normalized_kind)
        if int(component_meta.get('size', 0) or 0) > 0:
            return {
                'element_type': component_meta.get('element_type', 'FLOAT'),
                'subtype': component_meta.get('subtype', 'NONE'),
                'size': int(component_meta.get('size', 4) or 4),
                'value_kind': normalized_kind,
            }
    if reference_entry is not None:
        ref_prop_type = (
            str(reference_entry.get('prop_type', 'FLOAT') or 'FLOAT').strip().upper()
            if isinstance(reference_entry, dict)
            else str(getattr(reference_entry, 'prop_type', 'FLOAT') or 'FLOAT').strip().upper()
        )
        if ref_prop_type == 'ARRAY':
            element_type = izom_propui_free_entry_array_element_type(reference_entry, 'FLOAT')
            subtype = izom_propui_free_entry_array_subtype(reference_entry, 'NONE')
            size = izom_propui_free_entry_array_size(reference_entry, 4)
            return {
                'element_type': element_type,
                'subtype': subtype,
                'size': size,
                'value_kind': izom_propui_free_array_value_kind(element_type, subtype),
            }
    if normalized_kind == 'COLOR':
        return {
            'element_type': 'FLOAT',
            'subtype': 'COLOR',
            'size': 4,
            'value_kind': 'COLOR',
        }
    if normalized_kind == 'VECTOR':
        return {
            'element_type': 'FLOAT',
            'subtype': 'NONE',
            'size': 3,
            'value_kind': 'VECTOR',
        }
    if normalized_kind == 'INT_ARRAY':
        return {
            'element_type': 'INT',
            'subtype': 'NONE',
            'size': 4,
            'value_kind': 'INT_ARRAY',
        }
    if normalized_kind == 'BOOL_ARRAY':
        return {
            'element_type': 'BOOL',
            'subtype': 'NONE',
            'size': 4,
            'value_kind': 'BOOL_ARRAY',
        }
    return {
        'element_type': 'FLOAT',
        'subtype': 'NONE',
        'size': 4,
        'value_kind': normalized_kind,
    }


def _izom_propui_free_draw_array_prop(
    layout,
    item,
    prop_name,
    *,
    element_type='FLOAT',
    subtype='NONE',
    size=None,
    text_label="Value",
    color_picker_scope='',
    entry_uid='',
    value_label_uid='',
    target_mode='SELF',
    params=None,
    label_source=None,
):
    normalized_type = izom_propui_free_normalize_array_element_type(element_type, 'FLOAT')
    normalized_subtype = izom_propui_free_normalize_float_array_subtype(subtype, 'NONE')
    resolved_size = izom_propui_free_normalize_array_size(size, normalized_subtype, normalized_type, default=size)
    value_kind = izom_propui_free_array_value_kind(normalized_type, normalized_subtype)
    if normalized_type == 'FLOAT':
        if value_kind == 'COLOR':
            if resolved_size == 3:
                color_proxy_name = _izom_propui_free_float_array_color_proxy_name(prop_name, 3)
                if hasattr(item, color_proxy_name):
                    layout.prop(item, color_proxy_name, text=text_label)
                    return
            elif resolved_size >= 4:
                direct_color_name = f"{str(prop_name)}_color"
                if hasattr(item, direct_color_name):
                    if resolved_size == 4:
                        layout.prop(item, direct_color_name, text=text_label)
                        return
                    component_labels = izom_propui_free_entry_array_component_labels(
                        label_source or item,
                        normalized_subtype,
                        size=resolved_size,
                        element_type=normalized_type,
                    )
                    column = layout.column(align=True)
                    column.prop(item, direct_color_name, text=text_label)
                    for component_index in range(4, resolved_size):
                        component_proxy_name = _izom_propui_free_array_component_proxy_name(prop_name, normalized_type, component_index)
                        try:
                            decimals, _step = _izom_propui_free_editor_float_settings(params)
                            component_proxy_name = _izom_propui_free_array_component_proxy_name(prop_name, normalized_type, component_index, decimals)
                        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                            izom_propui_free_log_recovered(
                                category='UI',
                                exception=exc,
        )
                        column.prop(
                            item,
                            component_proxy_name,
                            text=component_labels[component_index],
                        )
                    return

                color_proxy_name = _izom_propui_free_float_array_color_proxy_name(prop_name, 4)
                if hasattr(item, color_proxy_name):
                    if resolved_size == 4:
                        layout.prop(item, color_proxy_name, text=text_label)
                        return
                    component_labels = izom_propui_free_entry_array_component_labels(
                        label_source or item,
                        normalized_subtype,
                        size=resolved_size,
                        element_type=normalized_type,
                    )
                    column = layout.column(align=True)
                    column.prop(item, color_proxy_name, text=text_label)
                    for component_index in range(4, resolved_size):
                        component_proxy_name = _izom_propui_free_array_component_proxy_name(prop_name, normalized_type, component_index)
                        try:
                            decimals, _step = _izom_propui_free_editor_float_settings(params)
                            component_proxy_name = _izom_propui_free_array_component_proxy_name(prop_name, normalized_type, component_index, decimals)
                        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                            izom_propui_free_log_recovered(
                                category='UI',
                                exception=exc,
        )
                        column.prop(
                            item,
                            component_proxy_name,
                            text=component_labels[component_index],
                        )
                    return

    component_labels = izom_propui_free_entry_array_component_labels(
        label_source or item,
        normalized_subtype,
        size=resolved_size,
        element_type=normalized_type,
    )
    column = layout.column(align=True)
    if text_label:
        column.label(text=text_label)

    if resolved_size <= 4 and normalized_type != 'BOOL':
        row = column.row(align=True)
        for component_index in range(resolved_size):
            component_proxy_name = _izom_propui_free_array_component_proxy_name(prop_name, normalized_type, component_index)
            if normalized_type == 'FLOAT':
                try:
                    decimals, _step = _izom_propui_free_editor_float_settings(params)
                    component_proxy_name = _izom_propui_free_array_component_proxy_name(prop_name, normalized_type, component_index, decimals)
                except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                    izom_propui_free_log_recovered(
                        category='UI',
                        exception=exc,
        )
            row.prop(
                item,
                component_proxy_name,
                text=component_labels[component_index],
            )
        return

    for component_index in range(resolved_size):
        component_proxy_name = _izom_propui_free_array_component_proxy_name(prop_name, normalized_type, component_index)
        if normalized_type == 'FLOAT':
            try:
                decimals, _step = _izom_propui_free_editor_float_settings(params)
                component_proxy_name = _izom_propui_free_array_component_proxy_name(prop_name, normalized_type, component_index, decimals)
            except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
                izom_propui_free_log_recovered(
                    category='UI',
                    exception=exc,
        )
        column.prop(
            item,
            component_proxy_name,
            text=component_labels[component_index],
        )


def _izom_propui_free_draw_value_match_prop(
    layout,
    item,
    value_kind,
    params,
    *,
    text_label="From Value",
    field_root='value',
    reference_entry=None,
    color_picker_scope='',
    entry_uid='',
    value_label_uid='',
    target_mode='SELF',
):
    normalized_kind = str(value_kind or 'NONE').strip().upper() or 'NONE'
    int_attr = f"{field_root}_int"
    float_attr = f"{field_root}_float"
    range_int_attr = f"{field_root}_range_int"
    range_float_attr = f"{field_root}_range_float"
    text_attr = f"{field_root}_text"

    def draw_int_value(attr_name, label):
        layout.prop(item, attr_name, text=label)

    if normalized_kind in {'INT', 'FLOAT'}:
        mode = str(getattr(item, 'match_mode', 'GREATER') or 'GREATER').strip().upper()
        if mode not in {'EQUAL', 'GREATER', 'LESS', 'RANGE'}:
            mode = 'GREATER'
        layout.prop(item, "match_mode", text="Match")
        if mode == 'EQUAL':
            primary_label = "Value"
        elif mode == 'LESS':
            primary_label = "At Most"
        elif mode == 'RANGE':
            primary_label = "From"
        else:
            primary_label = "At Least"

        if normalized_kind == 'INT':
            draw_int_value(int_attr, primary_label)
            if mode == 'RANGE':
                draw_int_value(range_int_attr, "To")
            return

        _izom_propui_free_draw_editor_float_prop(layout, item, float_attr, params, text=primary_label)
        if mode == 'RANGE':
            _izom_propui_free_draw_editor_float_prop(layout, item, range_float_attr, params, text="To")
        return

    if normalized_kind == 'BOOL':
        layout.prop(item, "source_bool_state", text=text_label)
        return
    if normalized_kind in {'COLOR', 'VECTOR', 'INT_ARRAY', 'BOOL_ARRAY'}:
        meta = _izom_propui_free_exact_match_array_meta(reference_entry, normalized_kind)
        field_name = izom_propui_free_entry_array_field_name(field_root, meta['element_type'])
        _izom_propui_free_draw_array_prop(
            layout,
            item,
            field_name,
            element_type=meta['element_type'],
            subtype=meta['subtype'],
            size=meta['size'],
            text_label="From Color" if meta['value_kind'] == 'COLOR' else text_label,
            color_picker_scope=color_picker_scope,
            entry_uid=entry_uid,
            value_label_uid=value_label_uid,
            target_mode=target_mode,
            params=params,
            label_source=reference_entry,
        )
        return
    if izom_propui_free_is_exact_match_value_kind(normalized_kind):
        layout.prop(item, text_attr, text=text_label)

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

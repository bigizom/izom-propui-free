# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from ..core.diagnostics import izom_propui_free_log_recovered
from ..core.context import izom_propui_free_context_params


IZOM_PROPUI_FREE_CONFIRM_ACTION_ITEMS = (
    ('ASK', 'Ask Every Time', 'Show the normal confirmation popup'),
    ('CONFIRM', 'Confirm Automatically', 'Run this confirmation action without asking'),
    ('CANCEL', 'Cancel Automatically', 'Cancel this confirmation action without asking'),
)

IZOM_PROPUI_FREE_CONFIRM_GENERATE_CURRENT_ITEMS = (
    ('ASK', 'Ask When Needed', 'Ask when Generate Current would overwrite the current generated UI'),
    ('OVERWRITE', 'Overwrite', 'Overwrite the current generated UI without asking'),
)

IZOM_PROPUI_FREE_CONFIRM_GENERATE_NATIVE_CONFLICT_ITEMS = (
    ('ASK', 'Ask When Needed', 'Ask when Generate would touch conflicting native custom properties'),
    ('OVERWRITE', 'Overwrite Conflicts', 'Overwrite only the conflicting native custom properties without asking'),
    ('SKIP', 'Keep Native Values', 'Keep only the conflicting native custom properties without asking'),
)

IZOM_PROPUI_FREE_CONFIRM_PARENT_DELETE_ITEMS = (
    ('ASK', 'Ask When Needed', 'Ask when deleting a parent entry with children'),
    ('DELETE', 'Delete Parent Only', 'Delete the parent and promote its children without asking'),
    ('DELETE_HIERARCHY', 'Delete Hierarchy', 'Delete the parent and its child hierarchy without asking'),
)

IZOM_PROPUI_FREE_CONFIRM_GENERATE_EMPTY_LAYOUT_ITEMS = (
    ('ASK', 'Ask When Needed', 'Ask when entries exist but none are placed in the Generated Layout'),
    ('CANCEL', 'Cancel', 'Skip generation entirely when no entries are placed in the Generated Layout'),
)

_IZOM_PROPUI_FREE_CONFIRM_ACTION_FIELD_NAMES = (
    'izom_propui_free_confirmation_clear_entry_list',
    'izom_propui_free_confirmation_full_factory_reset',
    'izom_propui_free_confirmation_clear_generated_layout',
    'izom_propui_free_confirmation_clear_dynamic_labels',
)
IZOM_PROPUI_FREE_CONFIRM_ACTION_FIELD_NAMES = _IZOM_PROPUI_FREE_CONFIRM_ACTION_FIELD_NAMES

_IZOM_PROPUI_FREE_CONFIRM_ITEM_MAP = {
    **{field_name: IZOM_PROPUI_FREE_CONFIRM_ACTION_ITEMS for field_name in _IZOM_PROPUI_FREE_CONFIRM_ACTION_FIELD_NAMES},
    'izom_propui_free_confirmation_generate_current_conflict': IZOM_PROPUI_FREE_CONFIRM_GENERATE_CURRENT_ITEMS,
    'izom_propui_free_confirmation_generate_native_conflict': IZOM_PROPUI_FREE_CONFIRM_GENERATE_NATIVE_CONFLICT_ITEMS,
    'izom_propui_free_confirmation_parent_delete': IZOM_PROPUI_FREE_CONFIRM_PARENT_DELETE_ITEMS,
    'izom_propui_free_confirmation_generate_empty_layout': IZOM_PROPUI_FREE_CONFIRM_GENERATE_EMPTY_LAYOUT_ITEMS,
}

IZOM_PROPUI_FREE_CONFIRMATION_GROUP_SPECS = (
    (
        'Generate',
        (
            'izom_propui_free_confirmation_generate_current_conflict',
            'izom_propui_free_confirmation_generate_native_conflict',
            'izom_propui_free_confirmation_generate_empty_layout',
        ),
    ),
    (
        'Entries & Layout',
        (
            'izom_propui_free_confirmation_clear_entry_list',
            'izom_propui_free_confirmation_clear_generated_layout',
            'izom_propui_free_confirmation_clear_dynamic_labels',
            'izom_propui_free_confirmation_parent_delete',
        ),
    ),
    (
        'Defaults & Reset',
        (
            'izom_propui_free_confirmation_full_factory_reset',
        ),
    ),
)

IZOM_PROPUI_FREE_CONFIRMATION_FIELD_NAMES = tuple(
    field_name
    for _group_label, field_names in IZOM_PROPUI_FREE_CONFIRMATION_GROUP_SPECS
    for field_name in field_names
)


def izom_propui_free_confirmation_value(params, prop_name, default='ASK'):
    items = _IZOM_PROPUI_FREE_CONFIRM_ITEM_MAP.get(str(prop_name or '').strip(), ())
    allowed = {item[0] for item in items}
    value = str(getattr(params, prop_name, default) if params is not None else default or 'ASK').strip().upper()
    if value in allowed:
        return value
    return default if default in allowed else 'ASK'


def izom_propui_free_confirm_or_execute(operator, context, event, *, prop_name):
    params = izom_propui_free_context_params(context)
    behavior = izom_propui_free_confirmation_value(params, prop_name, default='ASK')
    if behavior == 'CONFIRM':
        return operator.execute(context)
    if behavior == 'CANCEL':
        try:
            operator.report({'INFO'}, f"Skipped {getattr(operator, 'bl_label', 'confirmed action')}")
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
        )
        return {'CANCELLED'}
    return context.window_manager.invoke_confirm(operator, event)

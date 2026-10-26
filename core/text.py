# SPDX-License-Identifier: GPL-3.0-or-later

from .diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .diagnostics import izom_propui_free_log_recovered
from .constants import (
    IZOM_PROPUI_FREE_MAX_GENERATED_UI_TEXT,
    IZOM_PROPUI_FREE_MAX_LABEL_INPUT_TEXT,
    IZOM_PROPUI_FREE_MAX_PROP_ID_TEXT,
    IZOM_PROPUI_FREE_MAX_TOOLTIP_INPUT_TEXT,
    IZOM_PROPUI_FREE_MAX_TOOLTIP_TEXT,
    IZOM_PROPUI_FREE_TEXT_ALIGNMENT_ITEMS,
    IZOM_PROPUI_FREE_TEXT_ROLE_ITEMS,
    izom_propui_free_blender_icon_ids,
)


_IZOM_PROPUI_FREE_TEXT_ALIGNMENT_IDS = frozenset(item[0] for item in IZOM_PROPUI_FREE_TEXT_ALIGNMENT_ITEMS)
_IZOM_PROPUI_FREE_TEXT_ROLE_IDS = frozenset(item[0] for item in IZOM_PROPUI_FREE_TEXT_ROLE_ITEMS)


def _izom_propui_free_normalize_display_text(text, *, single_line=True):
    cleaned = '' if text is None else str(text)
    if '\r' not in cleaned:
        if single_line and '\n' not in cleaned:
            return cleaned.strip()
    else:
        cleaned = cleaned.replace('\r\n', '\n').replace('\r', '\n')
    if single_line:
        parts = [part.strip() for part in cleaned.split('\n') if part.strip()]
        cleaned = ' '.join(parts) if parts else cleaned.strip()
    return cleaned


def izom_propui_free_shorten_ui_text(text, limit=IZOM_PROPUI_FREE_MAX_GENERATED_UI_TEXT, *, single_line=True):
    cleaned = _izom_propui_free_normalize_display_text(text, single_line=single_line)
    if limit is None or limit < 1 or len(cleaned) <= limit:
        return cleaned
    if limit <= 3:
        return cleaned[:max(1, limit)]
    return cleaned[:max(1, limit - 3)].rstrip() + '...'

def _izom_propui_free_limit_tooltip_text(text, limit=IZOM_PROPUI_FREE_MAX_TOOLTIP_TEXT):
    cleaned = _izom_propui_free_normalize_display_text(text, single_line=False)
    if limit is None or limit < 1 or len(cleaned) <= limit:
        return cleaned
    if limit <= 3:
        return cleaned[:max(1, limit)]
    return cleaned[:max(1, limit - 3)].rstrip() + '...'


def _izom_propui_free_limit_text_chars(text, limit, *, single_line=False):
    cleaned = _izom_propui_free_normalize_display_text(text, single_line=single_line)
    if limit is None or limit < 1 or len(cleaned) <= int(limit):
        return cleaned
    return cleaned[:int(limit)]


def _izom_propui_free_limit_label_input_text(text):
    return _izom_propui_free_limit_text_chars(text, IZOM_PROPUI_FREE_MAX_LABEL_INPUT_TEXT, single_line=True)


def _izom_propui_free_limit_tooltip_input_text(text):
    return _izom_propui_free_limit_text_chars(text, IZOM_PROPUI_FREE_MAX_TOOLTIP_INPUT_TEXT, single_line=False)


def _izom_propui_free_limit_prop_id_input_text(text):
    cleaned = _izom_propui_free_limit_text_chars(text, IZOM_PROPUI_FREE_MAX_PROP_ID_TEXT, single_line=True)
    return cleaned.strip()


def _izom_propui_free_text_value(item, attr_name, default=None):
    if isinstance(item, dict):
        return item.get(attr_name, default)
    return getattr(item, attr_name, default)


def izom_propui_free_editor_label(item):
    return _izom_propui_free_normalize_display_text(
        _izom_propui_free_text_value(item, 'editor_label', ''),
        single_line=True,
    ).strip()


def izom_propui_free_display_alignment(value, default='LEFT'):
    normalized = str(value or default).strip().upper() or default
    return normalized if normalized in _IZOM_PROPUI_FREE_TEXT_ALIGNMENT_IDS else default


def izom_propui_free_text_role(value, default='TEXT'):
    normalized = str(value or default).strip().upper() or default
    return normalized if normalized in _IZOM_PROPUI_FREE_TEXT_ROLE_IDS else default


def izom_propui_free_display_icon(value, default='NONE'):
    valid = izom_propui_free_blender_icon_ids()
    normalized = str(value or default).strip().upper() or default
    return normalized if normalized in valid else default


def izom_propui_free_display_icon_pair(before_value='NONE', after_value='NONE'):
    return (
        izom_propui_free_display_icon(before_value, 'NONE'),
        izom_propui_free_display_icon(after_value, 'NONE'),
    )


def izom_propui_free_text_block_state(item):
    text = _izom_propui_free_normalize_display_text(_izom_propui_free_text_value(item, 'label', ''), single_line=True).strip()
    icon_before, icon_after = izom_propui_free_display_icon_pair(
        _izom_propui_free_text_value(item, 'text_icon', 'NONE'),
        _izom_propui_free_text_value(item, 'text_icon_after', 'NONE'),
    )
    text_role = izom_propui_free_text_role(
        _izom_propui_free_text_value(item, 'text_role', 'TEXT'),
        'TEXT',
    )
    return {
        'display_text': text,
        'text_alignment': izom_propui_free_display_alignment(_izom_propui_free_text_value(item, 'text_alignment', 'LEFT'), 'LEFT'),
        'text_role': text_role,
        'text_alert': bool(_izom_propui_free_text_value(item, 'text_alert', False)),
        'text_icon': icon_before,
        'text_icon_hug_text': bool(_izom_propui_free_text_value(item, 'text_icon_hug_text', True)),
        'text_icon_after': icon_after,
        'text_icon_after_hug_text': bool(_izom_propui_free_text_value(item, 'text_icon_after_hug_text', True)),
    }


def izom_propui_free_text_block_has_output(state):
    if not isinstance(state, dict):
        return False
    text_role = str(state.get('text_role', 'TEXT') or 'TEXT').strip().upper()
    return any((
        text_role in {'DIVIDER', 'SPACER'},
        text_role == 'TEXT' and bool(_izom_propui_free_normalize_display_text(state.get('display_text', ''), single_line=True).strip()),
        text_role == 'TEXT' and str(state.get('text_icon', 'NONE') or 'NONE').strip().upper() != 'NONE',
        text_role == 'TEXT' and str(state.get('text_icon_after', 'NONE') or 'NONE').strip().upper() != 'NONE',
    ))


def izom_propui_free_text_display_name(item, default='[Text]'):
    editor_label = izom_propui_free_editor_label(item)
    if editor_label:
        return editor_label

    state = izom_propui_free_text_block_state(item)
    label = state.get('display_text', '')
    text_role = str(state.get('text_role', 'TEXT') or 'TEXT').strip().upper()
    if label and text_role == 'TEXT':
        return label

    details = []
    if text_role == 'DIVIDER':
        details.append("Divider")
    elif text_role == 'SPACER':
        details.append("Spacer")
    if text_role == 'TEXT' and state.get('text_alert'):
        details.append("Alert")
    if not details:
        if text_role == 'DIVIDER':
            return "[Divider]"
        if text_role == 'SPACER':
            return "[Spacer]"
        return default
    return f"[{' | '.join(details)}]"


def izom_propui_free_entry_display_name(item, *, fallback_index=1, default='Entry'):
    if item is None:
        return '[Missing Entry]'
    editor_label = izom_propui_free_editor_label(item)
    if editor_label:
        return editor_label
    prop_type = str(_izom_propui_free_text_value(item, 'prop_type', 'FLOAT') or 'FLOAT').strip().upper()
    if prop_type == 'TEXT':
        return izom_propui_free_text_display_name(item)
    label = _izom_propui_free_normalize_display_text(_izom_propui_free_text_value(item, 'label', ''), single_line=True).strip()
    prop_id = str(_izom_propui_free_text_value(item, 'prop_id', '') or '').strip()
    uid = str(_izom_propui_free_text_value(item, 'uid', '') or '').strip()
    try:
        index = int(fallback_index or 1)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        index = 1
    return label or prop_id or uid or f"{default} {max(1, index)}"

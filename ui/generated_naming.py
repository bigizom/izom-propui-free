# SPDX-License-Identifier: GPL-3.0-or-later

import hashlib
import json

from .generated_state import (
    IZOM_PROPUI_FREE_GENERATED_SCRIPT_NAME_LIMIT,
    IZOM_PROPUI_FREE_GENERATED_SCRIPT_PER_UI_PREFIX,
    IZOM_PROPUI_FREE_GENERATED_SCRIPT_REGISTRY_PREFIX,
)


def _izom_propui_free_slug(text, *, fallback='ui'):
    value = str(text or '').strip().lower()
    chars = []
    previous_sep = False
    for char in value:
        if char.isalnum():
            chars.append(char)
            previous_sep = False
        elif not previous_sep:
            chars.append('_')
            previous_sep = True
    slug = ''.join(chars).strip('_')
    return slug or fallback


def _izom_propui_free_normalize_generated_script_name_override(value):
    text = str(value or '').strip()
    if not text:
        return ''
    text = text.replace('\\', '/').rsplit('/', 1)[-1].strip()
    if not text or text in {'.', '..'}:
        return ''
    if not text.lower().endswith('.py'):
        text = f"{text}.py"
    if text.lower() == '.py':
        return ''
    if len(text) <= IZOM_PROPUI_FREE_GENERATED_SCRIPT_NAME_LIMIT:
        return text
    base = text[:-3]
    digest = hashlib.sha1(text.encode('utf-8')).hexdigest()[:8]
    suffix = f"_{digest}.py"
    available = IZOM_PROPUI_FREE_GENERATED_SCRIPT_NAME_LIMIT - len(suffix)
    if available <= 0:
        return f"{digest}.py"[:IZOM_PROPUI_FREE_GENERATED_SCRIPT_NAME_LIMIT]
    return f"{base[:available].rstrip(' ._-') or 'generated_ui'}{suffix}"


def _izom_propui_free_generated_script_name_for_slot(slot):
    uid = str((slot or {}).get('uid', '') or '').strip()
    stored = _izom_propui_free_normalize_generated_script_name_override((slot or {}).get('script_name', ''))
    if stored:
        return stored
    script_prefix = IZOM_PROPUI_FREE_GENERATED_SCRIPT_PER_UI_PREFIX
    tab = _izom_propui_free_slug((slot or {}).get('tab', ''), fallback='tab')
    title = _izom_propui_free_slug((slot or {}).get('title', ''), fallback='panel')
    suffix = (uid[:8] if uid else hashlib.sha1(f"{tab}:{title}".encode('utf-8')).hexdigest()[:8])
    payload_limit = IZOM_PROPUI_FREE_GENERATED_SCRIPT_NAME_LIMIT - len(script_prefix) - len(suffix) - len('_.py')
    payload = f"{tab}_{title}"
    if len(payload) > max(0, payload_limit):
        payload = payload[: max(0, payload_limit)].rstrip('_')
    return f"{script_prefix}{payload}_{suffix}.py"


def _izom_propui_free_generated_script_name_suffix(slot, index):
    uid = str((slot or {}).get('uid', '') or '').strip()
    if uid:
        return uid[:8]
    fingerprint_source = json.dumps({'index': int(index or 0), 'slot': slot or {}}, sort_keys=True, default=str)
    return hashlib.sha1(fingerprint_source.encode('utf-8')).hexdigest()[:8]


def _izom_propui_free_generated_script_name_with_suffix(text_name, suffix):
    normalized = _izom_propui_free_normalize_generated_script_name_override(text_name)
    if not normalized:
        normalized = _izom_propui_free_normalize_generated_script_name_override('generated_ui.py')
    suffix_text = f"_{_izom_propui_free_slug(suffix, fallback='slot')}.py"
    available = IZOM_PROPUI_FREE_GENERATED_SCRIPT_NAME_LIMIT - len(suffix_text)
    base = normalized[:-3] if normalized.lower().endswith('.py') else normalized
    return f"{base[:max(0, available)].rstrip(' ._-') or 'generated_ui'}{suffix_text}"


def _izom_propui_free_with_unique_per_ui_script_names(slots):
    items = [dict(slot or {}) for slot in (slots or []) if isinstance(slot, dict)]
    base_names = [_izom_propui_free_generated_script_name_for_slot(item) for item in items]

    used_names = set()
    resolved = []
    for index, item in enumerate(items):
        item = dict(item)
        base_name = base_names[index]
        candidate = base_name
        candidate_key = candidate.casefold()
        if candidate_key in used_names:
            suffix = _izom_propui_free_generated_script_name_suffix(item, index)
            candidate = _izom_propui_free_generated_script_name_with_suffix(base_name, suffix)
            candidate_key = candidate.casefold()
            suffix_index = 2
            while candidate_key in used_names:
                candidate = _izom_propui_free_generated_script_name_with_suffix(base_name, f"{suffix}_{suffix_index}")
                candidate_key = candidate.casefold()
                suffix_index += 1
        used_names.add(candidate_key)
        item['script_name'] = candidate
        resolved.append(item)
    return resolved


def _izom_propui_free_generated_registry_key_for_slot(slot):
    uid = str((slot or {}).get('uid', '') or '').strip()
    if uid:
        return IZOM_PROPUI_FREE_GENERATED_SCRIPT_REGISTRY_PREFIX + uid
    fingerprint_source = json.dumps(slot or {}, sort_keys=True, default=str)
    return IZOM_PROPUI_FREE_GENERATED_SCRIPT_REGISTRY_PREFIX + hashlib.sha1(fingerprint_source.encode('utf-8')).hexdigest()

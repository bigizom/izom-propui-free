# SPDX-License-Identifier: GPL-3.0-or-later

from .diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from .diagnostics import izom_propui_free_log_recovered
import json
import os
import tempfile


def _izom_propui_free_load_last_synced_id_map(params):
    raw = str(getattr(params, 'izom_propui_free_last_synced_prop_ids_json', '') or '').strip()
    if not raw:
        return {}

    try:
        values = json.loads(raw)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        return {}

    if not isinstance(values, dict):
        return {}

    mapping = {}
    for key, prop_ids in values.items():
        owner_path = str(key or '').strip()
        if not owner_path or not isinstance(prop_ids, list):
            continue
        cleaned = {
            str(prop_id or '').strip()
            for prop_id in prop_ids
            if str(prop_id or '').strip()
        }
        if cleaned:
            mapping[owner_path] = cleaned
    return mapping


def _izom_propui_free_store_last_synced_id_map(params, mapping):
    cleaned_mapping = {}
    for key, prop_ids in (mapping or {}).items():
        owner_path = str(key or '').strip()
        if not owner_path:
            continue
        cleaned = sorted({
            str(prop_id or '').strip()
            for prop_id in (prop_ids or [])
            if str(prop_id or '').strip()
        })
        if cleaned:
            cleaned_mapping[owner_path] = cleaned
    try:
        params.izom_propui_free_last_synced_prop_ids_json = json.dumps(cleaned_mapping, sort_keys=True)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='Core',
            exception=exc,
        )
        params.izom_propui_free_last_synced_prop_ids_json = '{}'


def _izom_propui_free_last_synced_owner_paths(params):
    return sorted(_izom_propui_free_load_last_synced_id_map(params))

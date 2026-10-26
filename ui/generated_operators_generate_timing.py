# SPDX-License-Identifier: GPL-3.0-or-later

import time

from ..core.diagnostics import (
    IZOM_PROPUI_FREE_RECOVERABLE_ERRORS,
    izom_propui_free_log_debug,
    izom_propui_free_log_recovered,
)

_IZOM_PROPUI_FREE_LAST_GENERATE_PHASE_TIMINGS = {
    'total_ms': 0.0,
    'phases': [],
}

def _izom_propui_free_clear_generate_timing_cache():
    _IZOM_PROPUI_FREE_LAST_GENERATE_PHASE_TIMINGS['total_ms'] = 0.0
    _IZOM_PROPUI_FREE_LAST_GENERATE_PHASE_TIMINGS['phases'] = []

def izom_propui_free_last_generate_phase_timings():
    return {
        'total_ms': float(_IZOM_PROPUI_FREE_LAST_GENERATE_PHASE_TIMINGS.get('total_ms', 0.0) or 0.0),
        'phases': [dict(item) for item in _IZOM_PROPUI_FREE_LAST_GENERATE_PHASE_TIMINGS.get('phases', [])],
    }


def _izom_propui_free_generate_timing_reset(operator):
    try:
        operator._izom_propui_free_generate_timings = []
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(category='UI', exception=exc)


def _izom_propui_free_generate_timing_mark(operator, label, start_time):
    try:
        elapsed_ms = max(0.0, (time.perf_counter() - float(start_time)) * 1000.0)
        timings = getattr(operator, '_izom_propui_free_generate_timings', None)
        if not isinstance(timings, list):
            timings = []
            operator._izom_propui_free_generate_timings = timings
        timings.append((str(label or ''), elapsed_ms))
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(category='UI', exception=exc)


def _izom_propui_free_generate_timing_log(operator, total_start_time):
    global _IZOM_PROPUI_FREE_LAST_GENERATE_PHASE_TIMINGS
    try:
        total_ms = max(0.0, (time.perf_counter() - float(total_start_time)) * 1000.0)
        timings = list(getattr(operator, '_izom_propui_free_generate_timings', []) or [])
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(category='UI', exception=exc)
        return
    _IZOM_PROPUI_FREE_LAST_GENERATE_PHASE_TIMINGS = {
        'total_ms': total_ms,
        'phases': [
            {
                'label': str(label or ''),
                'elapsed_ms': float(elapsed_ms or 0.0),
            }
            for label, elapsed_ms in timings
        ],
    }
    details = '\n'.join(
        [f"total: {total_ms:.3f} ms"]
        + [f"{label}: {elapsed_ms:.3f} ms" for label, elapsed_ms in timings]
    )
    izom_propui_free_log_debug("Generate phase timings", category='Generated UI', details=details)



from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

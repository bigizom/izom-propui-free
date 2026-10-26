# SPDX-License-Identifier: GPL-3.0-or-later

import traceback
import time
from datetime import datetime


# Shared "recoverable" exception set used by the addon's defensive try/except
# guards around Blender RNA / idprop / data access. Centralized here so the
# tuple cannot drift between modules.
IZOM_PROPUI_FREE_RECOVERABLE_ERRORS = (
    RuntimeError,
    ValueError,
    TypeError,
    AttributeError,
    SyntaxError,
    ReferenceError,
    LookupError,
    OSError,
    ImportError,
)


_IZOM_PROPUI_FREE_DIAGNOSTIC_LIMIT = 80
_IZOM_PROPUI_FREE_DIAGNOSTIC_THROTTLE_SECONDS = 3.0
_IZOM_PROPUI_FREE_DIAGNOSTIC_THROTTLE_LIMIT = 512
_IZOM_PROPUI_FREE_LEVEL_WEIGHT = {
    'DEBUG': 10,
    'INFO': 20,
    'WARNING': 30,
    'ERROR': 40,
}
_IZOM_PROPUI_FREE_DIAGNOSTICS = []
_IZOM_PROPUI_FREE_DIAGNOSTIC_THROTTLE = {}


def _izom_propui_free_level(value):
    level = str(value or 'INFO').strip().upper()
    return level if level in _IZOM_PROPUI_FREE_LEVEL_WEIGHT else 'INFO'


def izom_propui_free_debug_enabled(context=None):
    try:
        import bpy
    except ImportError:
        return False
    try:
        package = str(__package__ or '').rpartition('.')[0] or 'izom_propui_free'
        prefs = bpy.context.preferences.addons[package].preferences
    except (AttributeError, KeyError, TypeError):
        try:
            prefs = context.preferences.addons[package].preferences if context is not None else None
        except (AttributeError, KeyError, TypeError):
            prefs = None
    return bool(getattr(prefs, 'izom_propui_free_verbose_console_diagnostics', False)) if prefs is not None else False


def izom_propui_free_log(level, message, *, category='General', exception=None, details=None, debug_only=False):
    normalized_level = _izom_propui_free_level(level)
    if debug_only and not izom_propui_free_debug_enabled():
        return None

    message_text = str(message or '').strip()
    if not message_text:
        message_text = 'No diagnostic message was provided'
    category_text = str(category or 'General').strip() or 'General'
    exception_text = ''
    traceback_text = ''
    if exception is not None:
        exception_text = f"{type(exception).__name__}: {exception}"
        if izom_propui_free_debug_enabled() or _IZOM_PROPUI_FREE_LEVEL_WEIGHT[normalized_level] >= _IZOM_PROPUI_FREE_LEVEL_WEIGHT['WARNING']:
            traceback_text = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__)).strip()

    suppressed_count = 0
    should_throttle = (
        _IZOM_PROPUI_FREE_LEVEL_WEIGHT[normalized_level] >= _IZOM_PROPUI_FREE_LEVEL_WEIGHT['WARNING']
        or exception is not None
    )
    if should_throttle:
        now = time.monotonic()
        throttle_key = (normalized_level, category_text, message_text, exception_text)
        throttle_record = _IZOM_PROPUI_FREE_DIAGNOSTIC_THROTTLE.get(throttle_key)
        if throttle_record is not None:
            try:
                elapsed = now - float(throttle_record.get('last_seen', 0.0))
            except (TypeError, ValueError, OverflowError):
                elapsed = _IZOM_PROPUI_FREE_DIAGNOSTIC_THROTTLE_SECONDS
            if elapsed < _IZOM_PROPUI_FREE_DIAGNOSTIC_THROTTLE_SECONDS:
                throttle_record['last_seen'] = now
                throttle_record['suppressed_count'] = int(throttle_record.get('suppressed_count', 0) or 0) + 1
                return None
            suppressed_count = int(throttle_record.get('suppressed_count', 0) or 0)
            throttle_record['last_seen'] = now
            throttle_record['suppressed_count'] = 0
        else:
            if len(_IZOM_PROPUI_FREE_DIAGNOSTIC_THROTTLE) >= _IZOM_PROPUI_FREE_DIAGNOSTIC_THROTTLE_LIMIT:
                del _IZOM_PROPUI_FREE_DIAGNOSTIC_THROTTLE[next(iter(_IZOM_PROPUI_FREE_DIAGNOSTIC_THROTTLE))]
            _IZOM_PROPUI_FREE_DIAGNOSTIC_THROTTLE[throttle_key] = {
                'last_seen': now,
                'suppressed_count': 0,
            }

    details_text = str(details or '').strip()
    if suppressed_count:
        summary = f"Suppressed {suppressed_count} similar diagnostic{'s' if suppressed_count != 1 else ''}."
        details_text = f"{details_text}\n{summary}".strip()

    record = {
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'level': normalized_level,
        'category': category_text,
        'message': message_text,
        'details': details_text,
        'exception': exception_text,
        'traceback': traceback_text,
        'suppressed_count': suppressed_count,
    }
    _IZOM_PROPUI_FREE_DIAGNOSTICS.append(record)
    del _IZOM_PROPUI_FREE_DIAGNOSTICS[:-_IZOM_PROPUI_FREE_DIAGNOSTIC_LIMIT]

    should_print = (
        _IZOM_PROPUI_FREE_LEVEL_WEIGHT[normalized_level] >= _IZOM_PROPUI_FREE_LEVEL_WEIGHT['WARNING']
        or izom_propui_free_debug_enabled()
    )
    if should_print:
        print(f"[izom PropUI Free][{normalized_level}][{category_text}] {message_text}")
        if record['details'] and izom_propui_free_debug_enabled():
            print(record['details'])
        if exception_text:
            print(f"[izom PropUI Free][{normalized_level}][{category_text}] {exception_text}")
        if traceback_text:
            print(traceback_text)
    return record


def izom_propui_free_log_debug(message, *, category='Debug', exception=None, details=None):
    return izom_propui_free_log('DEBUG', message, category=category, exception=exception, details=details, debug_only=True)


def izom_propui_free_log_info(message, *, category='General', exception=None, details=None):
    return izom_propui_free_log('INFO', message, category=category, exception=exception, details=details)


def izom_propui_free_log_warning(message, *, category='General', exception=None, details=None):
    return izom_propui_free_log('WARNING', message, category=category, exception=exception, details=details)


def izom_propui_free_log_error(message, *, category='General', exception=None, details=None):
    return izom_propui_free_log('ERROR', message, category=category, exception=exception, details=details)


def izom_propui_free_log_recovered(category='General', *, exception, hint=None, details=None):
    """Log a recoverable exception at DEBUG level.

    Use this after catching the narrow exception types expected by the
    operation being attempted. A throttled record is retained even when verbose
    logging is off. The traceback is attached when debug diagnostics are
    enabled; the optional `hint` describes the action being attempted.
    """
    message = f"Recovered from exception while {hint}" if hint else "Recovered from exception"
    return izom_propui_free_log(
        'DEBUG',
        message,
        category=category,
        exception=exception,
        details=details,
    )


def izom_propui_free_recent_diagnostics(*, min_level='DEBUG', limit=None):
    min_weight = _IZOM_PROPUI_FREE_LEVEL_WEIGHT[_izom_propui_free_level(min_level)]
    records = [
        dict(record)
        for record in _IZOM_PROPUI_FREE_DIAGNOSTICS
        if _IZOM_PROPUI_FREE_LEVEL_WEIGHT.get(record.get('level', 'INFO'), 20) >= min_weight
    ]
    if limit is not None:
        try:
            count = max(0, int(limit))
        except (TypeError, ValueError, OverflowError):
            count = 0
        if count:
            records = records[-count:]
    return records


def izom_propui_free_clear_diagnostics():
    count = len(_IZOM_PROPUI_FREE_DIAGNOSTICS)
    _IZOM_PROPUI_FREE_DIAGNOSTICS.clear()
    _IZOM_PROPUI_FREE_DIAGNOSTIC_THROTTLE.clear()
    return count

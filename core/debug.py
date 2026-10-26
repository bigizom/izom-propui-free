# SPDX-License-Identifier: GPL-3.0-or-later
from .diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS


def izom_propui_free_debug_print(message, payload=None):
    try:
        from .diagnostics import izom_propui_free_log_debug

        details = None if payload is None else repr(payload)
        izom_propui_free_log_debug(str(message or ''), category='Debug', details=details)
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        print(f"[izom PropUI Free][WARNING][Debug] Could not route debug message through diagnostics: {exc}")
        if payload is None:
            print(message)
            return
        print(message, payload)

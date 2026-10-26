# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
import bpy

from ..core.diagnostics import izom_propui_free_log_recovered


def izom_propui_free_addon_preferences_id(package_name):
    package = str(package_name or '').strip()
    if package.endswith('.ui'):
        package = package.rsplit('.', 1)[0]
    return package or 'izom_propui_free'


class IZOM_PROPUI_FREE_AnnotatedPropertyTarget:
    def __init__(self, cls):
        self._cls = cls
        self._annotations = dict(getattr(cls, '__annotations__', {}) or {})

    def __setattr__(self, name, value):
        if name in {'_cls', '_annotations'}:
            object.__setattr__(self, name, value)
            return
        self._annotations[name] = value

    def apply(self):
        self._cls.__annotations__ = self._annotations

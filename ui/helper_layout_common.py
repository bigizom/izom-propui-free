# SPDX-License-Identifier: GPL-3.0-or-later

_IZOM_PROPUI_FREE_LAYOUT_VIEW_STATE_CACHE = {}
_IZOM_PROPUI_FREE_LAYOUT_VIEW_STATE_CACHE_LIMIT = 64
IZOM_PROPUI_FREE_LAYOUT_MAIN_CONTAINER_ENUM = 'MAIN_PANEL_BODY'


def _izom_propui_free_clear_layout_session_caches():
    _IZOM_PROPUI_FREE_LAYOUT_VIEW_STATE_CACHE.clear()

from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

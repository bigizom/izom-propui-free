# SPDX-License-Identifier: GPL-3.0-or-later

from .helper_layout_rows import (
    _izom_propui_free_layout_collapsed_row_uids,
    _izom_propui_free_set_layout_collapsed_row_uids,
)
from .helper_layout_common import IZOM_PROPUI_FREE_LAYOUT_MAIN_CONTAINER_ENUM



def _izom_propui_free_layout_container_uid_from_enum(value):
    text = str(value or '').strip()
    if text in {'', '0', IZOM_PROPUI_FREE_LAYOUT_MAIN_CONTAINER_ENUM}:
        return ''
    return text


def _izom_propui_free_layout_container_enum_from_uid(value):
    uid = str(value or '').strip()
    return uid or IZOM_PROPUI_FREE_LAYOUT_MAIN_CONTAINER_ENUM


def _izom_propui_free_normalize_layout_active_container_enum(params, valid_container_uids=None):
    if params is None:
        return ''
    return ''


def _izom_propui_free_prune_layout_collapsed_row_uids(params, valid_row_uids):
    valid = {str(uid or '').strip() for uid in (valid_row_uids or []) if str(uid or '').strip()}
    collapsed = [uid for uid in _izom_propui_free_layout_collapsed_row_uids(params) if uid in valid]
    return _izom_propui_free_set_layout_collapsed_row_uids(params, collapsed)


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

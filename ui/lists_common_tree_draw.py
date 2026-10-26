# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.diagnostics import IZOM_PROPUI_FREE_RECOVERABLE_ERRORS
from ..core.diagnostics import izom_propui_free_log_recovered

from .lists_common_base import IZOM_PROPUI_FREE_TREE_INDENT


def _izom_propui_free_draw_tree_indent(row, depth, *, indent=IZOM_PROPUI_FREE_TREE_INDENT):
    for _ in range(max(0, int(depth or 0))):
        row.separator(factor=indent)


def _izom_propui_free_tree_arrow_slot(row, *, width=None):
    slot = row.row(align=True)
    slot.alignment = 'LEFT'
    if width is not None:
        try:
            slot.ui_units_x = width
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
        )
    return slot


def _izom_propui_free_draw_tree_arrow_spacer(row, *, width=None):
    # When no explicit width is requested, draw the BLANK1 icon directly on the
    # parent row. The spacer is visually just an icon-sized gap — wrapping it in
    # an inner row() adds a widget allocation per indent level per redraw.
    if width is None:
        try:
            row.label(text="", icon='BLANK1')
        except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
            izom_propui_free_log_recovered(
                category='UI',
                exception=exc,
            )
            row.label(text="")
        return
    slot = _izom_propui_free_tree_arrow_slot(row, width=width)
    try:
        slot.label(text="", icon='BLANK1')
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
        slot.label(text="")


def _izom_propui_free_fixed_row(row, *, width=None):
    if width is None:
        return row
    cell = row.row(align=True)
    cell.alignment = 'LEFT'
    try:
        cell.ui_units_x = width
    except IZOM_PROPUI_FREE_RECOVERABLE_ERRORS as exc:
        izom_propui_free_log_recovered(
            category='UI',
            exception=exc,
        )
    return cell


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals())

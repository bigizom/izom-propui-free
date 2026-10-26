# SPDX-License-Identifier: GPL-3.0-or-later


def _izom_propui_free_disable_slider_for_soft_limits(entry):
    if isinstance(entry, dict) and bool(entry.get('use_soft_limits', False)) and bool(entry.get('slider', False)):
        entry['slider'] = False

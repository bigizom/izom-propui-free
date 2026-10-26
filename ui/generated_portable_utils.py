# SPDX-License-Identifier: GPL-3.0-or-later


def _izom_propui_free_join_portable_sections(sections):
    return "\n\n\n".join(str(section).strip() for section in sections if str(section or "").strip()) + "\n"

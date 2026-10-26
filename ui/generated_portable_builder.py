# SPDX-License-Identifier: GPL-3.0-or-later

from .generated_state import (
    IZOM_PROPUI_FREE_GENERATED_SCRIPT_REGISTRY_KEY,
)
from .generated_branding import (
    izom_propui_free_brand_generated_python_source,
    izom_propui_free_resolve_generated_branding,
)
from .generated_portable_draw import _izom_propui_free_prepare_direct_portable_script
from .generated_portable_panel_sections import (
    _izom_propui_free_portable_direct_panel_section,
    _izom_propui_free_portable_direct_register_section,
)
from .generated_portable_runtime_sections import (
    _izom_propui_free_portable_direct_layout_section,
    _izom_propui_free_portable_direct_owner_path_resolver_section,
)
from .generated_portable_utils import _izom_propui_free_join_portable_sections


def _izom_propui_free_build_portable_generated_script(slots, *, registry_key=IZOM_PROPUI_FREE_GENERATED_SCRIPT_REGISTRY_KEY):
    first_slot = next((slot for slot in (slots or []) if isinstance(slot, dict)), {})
    branding = izom_propui_free_resolve_generated_branding((first_slot or {}).get('branding'))
    panels, draw_sources = _izom_propui_free_prepare_direct_portable_script(slots)
    uses_owner_path_resolver = (
        any("_izom_propui_free_resolve_owner_path" in str(source or "") for source in draw_sources)
    )
    uses_compact_label_layout = any("_compact_label_value_layout" in str(source or "") for source in draw_sources)

    header_lines = [
        "# SPDX-License-Identifier: GPL-3.0-or-later",
        "# Generated UI format: 1",
    ]
    if bool(branding.get('show_credit', True)):
        credit_comment = str(branding.get('credit_comment', '') or '').strip()
        if credit_comment:
            header_lines.insert(1, "# " + credit_comment.lstrip('#').strip())
        header_lines.insert(3, "# Edit through izom PropUI when possible; manual edits may be overwritten.")
    header_lines.append("import bpy")
    header_lines.append("from bpy.app.handlers import persistent")
    header_lines.extend([
        "",
        f"_REGISTRY_KEY = {str(registry_key or IZOM_PROPUI_FREE_GENERATED_SCRIPT_REGISTRY_KEY)!r}",
    ])
    sections = ["\n".join(header_lines)]
    if uses_owner_path_resolver:
        sections.append(_izom_propui_free_portable_direct_owner_path_resolver_section())
    if uses_compact_label_layout:
        sections.append(_izom_propui_free_portable_direct_layout_section(
            include_compact_label_layout=uses_compact_label_layout,
        ))
    sections.extend(draw_sources)
    sections.extend(_izom_propui_free_portable_direct_panel_section(panel) for panel in panels)
    sections.append(_izom_propui_free_portable_direct_register_section(
        [str(panel.get("class_name", "") or "").strip() for panel in panels],
    ))
    source = _izom_propui_free_join_portable_sections(sections)
    return izom_propui_free_brand_generated_python_source(source, branding)

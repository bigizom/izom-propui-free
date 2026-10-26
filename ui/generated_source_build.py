# SPDX-License-Identifier: GPL-3.0-or-later

from .generated_source_header import (
    _izom_propui_free_generated_source_header,
)
from .generated_source_prune import (
    _izom_propui_free_prune_generated_draw_helpers,
)
from .generated_source_prepare import (
    _izom_propui_free_prepare_generated_entries,
)
from .generated_source_common import (
    _GeneratedLineTarget,
    _StandalonePanelBuilder,
)
from .generated_branding import (
    izom_propui_free_generated_branding_from_params,
    izom_propui_free_resolve_generated_branding,
)


def _izom_propui_free_append_generated_entries(params, lines, entries, *, generated_control_keys=None, branding=None):
    builder = _StandalonePanelBuilder(
        params,
        entries,
        str(getattr(params, 'izom_propui_free_default_target_owner_path', '') or '').strip(),
        generated_control_keys=generated_control_keys,
        branding=branding,
    )
    cond_by_uid = builder._build_visibility_conditions(None, entries)
    builder._avail_cond_by_uid = {}
    groups = builder._entry_draw_groups(entries, cond_by_uid)
    for group in groups:
        if not group:
            continue
        target = _GeneratedLineTarget('izom_propui_free_root', [])
        builder._draw_entry_group(target, group)
        for line in target._lines:
            lines.append(f"    {line}")


def izom_propui_free_build_generated_draw_source(
        params,
        *,
        generated_control_keys=None,
        entries=None,
        owner_paths=None,
        branding=None,
):
    resolved_branding = izom_propui_free_resolve_generated_branding(
        branding if branding is not None else izom_propui_free_generated_branding_from_params(params)
    )
    if entries is None or owner_paths is None:
        entries, owner_paths = _izom_propui_free_prepare_generated_entries(params)
    resolved_generated_control_keys = dict(generated_control_keys or {})
    sections = []
    for function_name in ('_izom_propui_free_generated_draw',):
        lines = _izom_propui_free_generated_source_header(
            owner_paths,
            function_name=function_name,
            branding=resolved_branding,
        )
        header_line_count = len(lines)
        _izom_propui_free_append_generated_entries(
            params,
            lines,
            entries,
            generated_control_keys=resolved_generated_control_keys,
            branding=resolved_branding,
        )
        if len(lines) == header_line_count:
            if not entries:
                lines.append("    izom_propui_free_root.label(text='No generated PropUI entries yet.')")
            else:
                lines.append("    return")
        lines = _izom_propui_free_prune_generated_draw_helpers(lines)
        sections.append("\n".join(lines))
    source = "\n\n".join(sections) + "\n"
    return source, owner_paths


from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

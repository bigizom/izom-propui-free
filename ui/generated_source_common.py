# SPDX-License-Identifier: GPL-3.0-or-later

from ..core.cache import izom_propui_free_cached_entry_tree_bundle
from .panel_codegen import IzomPropUIPanelCodegenMixin
from .generated_branding import izom_propui_free_resolve_generated_branding


class _GeneratedLineTarget:
    def __init__(self, layout, lines):
        self.layout = layout
        self._lines = lines

    def add_line(self, line):
        self._lines.append(str(line))


class _StandalonePanelBuilder(IzomPropUIPanelCodegenMixin):
    def __init__(self, params, entries, default_owner_path, *, generated_control_keys=None, branding=None):
        self.params = params
        self.target_owner_path = default_owner_path
        self.generated_control_keys = dict(generated_control_keys or {})
        self.generated_branding = branding
        self.generated_branding_resolved = izom_propui_free_resolve_generated_branding(
            branding if branding is not None else params
        )
        self._izom_propui_free_panel_tree_state = izom_propui_free_cached_entry_tree_bundle(params).get('tree_state', {})
        self._avail_cond_by_uid = {}



from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

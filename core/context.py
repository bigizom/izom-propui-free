# SPDX-License-Identifier: GPL-3.0-or-later

import bpy


def izom_propui_free_context_params(context=None):
    active_context = context or getattr(bpy, 'context', None)
    scene = getattr(active_context, 'scene', None)
    return getattr(scene, 'izom_propui_free', None) if scene is not None else None

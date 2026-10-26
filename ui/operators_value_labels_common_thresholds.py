# SPDX-License-Identifier: GPL-3.0-or-later

from .operators_value_labels_common_base import (
    _izom_propui_free_threshold_field_name,
    _izom_propui_free_value_label_companion_key_for_collection,
)
from ..core.value_labels_common import _izom_propui_free_is_numeric_type
from .helper_value_labels_thresholds import (
    _izom_propui_free_normalize_threshold_collection,
)


def _izom_propui_free_normalize_value_label_collection_thresholds(collection, entry, collection_owner, collection_name, info):
    if collection is None or entry is None or info is None:
        return
    prop_type = str(info.get('source_type', '') or '')
    if not _izom_propui_free_is_numeric_type(prop_type):
        return
    field_name = _izom_propui_free_threshold_field_name(prop_type, field_root='target_value')
    companion_key = _izom_propui_free_value_label_companion_key_for_collection(
        collection_name,
        entry,
        collection_owner,
        field_name,
        reference_entry=info.get('source_entry') or entry,
    )
    _izom_propui_free_normalize_threshold_collection(
        collection,
        field_name,
        prop_type,
        min_value=info.get('min_value'),
        max_value=info.get('max_value'),
        companion_key=companion_key,
        params=info.get('params'),
        base_value=info.get('min_value'),
    )


def _izom_propui_free_finalize_value_label_thresholds(collection, entry, active_owner, collection_name, info):
    if not info or collection is None or entry is None:
        return

    source_type = str(info.get('source_type', '') or '')
    if not _izom_propui_free_is_numeric_type(source_type):
        return

    _izom_propui_free_normalize_value_label_collection_thresholds(
        collection,
        entry,
        active_owner,
        collection_name,
        info,
    )




from ..core.exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

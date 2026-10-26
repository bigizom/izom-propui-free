# SPDX-License-Identifier: GPL-3.0-or-later

from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, StringProperty
from bpy.types import PropertyGroup

from ..core.constants import (
    IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT,
    IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_MAX,
    IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_MIN,
    IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT,
    IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_MAX,
    IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_MIN,
)
from .helpers import _izom_propui_free_layout_row_settings_updated
from .model_proxies import _izom_propui_free_add_editor_float_proxy_properties


class IZOM_PROPUI_FREE_LayoutRow(PropertyGroup):
    row_index: IntProperty(
        name="Row",
        description="Generated Layout row number",
        default=1,
        min=1,
        options={'HIDDEN'},
    )
    row_height_scale: FloatProperty(
        name="Row Height",
        description="Vertical scale applied to this generated layout row",
        default=IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT,
        min=1.0,
        max=2.0,
        soft_min=1.0,
        soft_max=2.0,
        precision=2,
        update=_izom_propui_free_layout_row_settings_updated,
    )
    row_inset_left_enabled: BoolProperty(
        name="Left Inset",
        description="Add empty generated UI space before this row's contents",
        default=False,
        update=_izom_propui_free_layout_row_settings_updated,
    )
    row_inset_left_amount: FloatProperty(
        name="Left Amount",
        description="Amount of empty generated UI space before this row's contents",
        default=IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT,
        min=IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT,
        max=IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT,
        soft_min=IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT,
        soft_max=IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT,
        precision=1,
        update=_izom_propui_free_layout_row_settings_updated,
    )

class IZOM_PROPUI_FREE_LayoutItem(PropertyGroup):
    uid: StringProperty(
        name="UID",
        description="Internal stable identifier used for Generated Layout selection",
        default="",
        options={'HIDDEN'},
    )
    entry_uid: StringProperty(
        name="Entry UID",
        description="Referenced izom PropUI entry shown in the Generated Layout editor",
        default="",
        options={'HIDDEN'},
    )
    row_index: IntProperty(
        name="Row",
        description="Generated Layout row number",
        default=1,
        min=1,
    )
    column_index: IntProperty(
        name="Column Index",
        description="Internal Generated Layout column index",
        default=1,
        min=1,
        options={'HIDDEN'},
    )

class IZOM_PROPUI_FREE_LayoutViewItem(PropertyGroup):
    uid: StringProperty(
        name="UID",
        description="Internal stable identifier used for Generated Layout editor selection",
        default="",
        options={'HIDDEN'},
    )
    kind: EnumProperty(
        name="Kind",
        description="Editor-only Generated Layout view item type",
        items=[
            ('ROW_HEADER', 'Row Header', 'Generated Layout row header'),
            ('ENTRY_ITEM', 'Entry Item', 'Generated Layout entry item'),
            ('DIVIDER', 'Divider', 'Generated Layout zone divider'),
        ],
        default='ENTRY_ITEM',
        options={'HIDDEN'},
    )
    layout_uid: StringProperty(
        name="Layout UID",
        description="Underlying layout item for entry rows",
        default="",
        options={'HIDDEN'},
    )
    entry_uid: StringProperty(
        name="Entry UID",
        description="Underlying source entry",
        default="",
        options={'HIDDEN'},
    )
    parent_uid: StringProperty(
        name="Parent UID",
        description="Editor-only parent link for Generated Layout row grouping",
        default="",
        options={'HIDDEN'},
    )
    row_index: IntProperty(
        name="Row",
        description="Generated Layout row number for this editor-only item",
        default=1,
        min=1,
        options={'HIDDEN'},
    )
    column_index: IntProperty(
        name="Column Index",
        description="Generated Layout column index for this editor-only item",
        default=1,
        min=1,
        options={'HIDDEN'},
    )
    row_member_uids_json: StringProperty(
        name="Row Member UIDs",
        description="Internal ordered layout item ids for this row header",
        default="[]",
        options={'HIDDEN'},
    )
    ui_order: IntProperty(
        name="UI Order",
        description="Editor-only Generated Layout view order",
        default=1,
        options={'HIDDEN'},
    )


_izom_propui_free_add_editor_float_proxy_properties(
    IZOM_PROPUI_FREE_LayoutRow,
    {
        'row_height_scale': {
            'name': "Row Height",
            'description': "Vertical scale applied to this generated layout row",
            'default': IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT,
            'min': IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_MIN,
            'max': IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_MAX,
        },
        'row_inset_left_amount': {
            'name': "Left Amount",
            'description': "Amount of empty generated UI space before this row's contents",
            'default': IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT,
            'min': IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_MIN,
            'max': IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_MAX,
        },
    },
)


CLASSES = (
    IZOM_PROPUI_FREE_LayoutRow,
    IZOM_PROPUI_FREE_LayoutItem,
    IZOM_PROPUI_FREE_LayoutViewItem,
)

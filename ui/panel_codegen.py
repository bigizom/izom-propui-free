# SPDX-License-Identifier: GPL-3.0-or-later

from .panel_codegen_conditions import _IzomPropUICodegenConditionsMixin
from .panel_codegen_analysis import _IzomPropUICodegenAnalysisMixin
from .panel_codegen_ruletext import _IzomPropUICodegenRuleTextMixin
from .panel_codegen_layout_conditions import _IzomPropUICodegenLayoutConditionsMixin
from .panel_codegen_layout_entry_style import _IzomPropUICodegenLayoutEntryStyleMixin
from .panel_codegen_layout_components import _IzomPropUICodegenLayoutComponentsMixin
from .panel_codegen_layout_labels import _IzomPropUICodegenLayoutLabelsMixin
from .panel_codegen_cell_property import _IzomPropUICodegenPropertyCellMixin
from .panel_codegen_cell_special import _IzomPropUICodegenSpecialCellMixin
from .panel_codegen_cell_entry import _IzomPropUICodegenEntryCellMixin
from .panel_codegen_cell_text import _IzomPropUICodegenTextCellMixin
from .panel_codegen_cell_slots import _IzomPropUICodegenSlotCellMixin
from .panel_codegen_group_standard import _IzomPropUICodegenStandardGroupMixin
from .panel_codegen_group_fill import _IzomPropUICodegenFillGroupMixin
from .panel_codegen_group_dispatch import _IzomPropUICodegenGroupDispatchMixin


class IzomPropUIPanelCodegenMixin(
    _IzomPropUICodegenConditionsMixin,
    _IzomPropUICodegenAnalysisMixin,
    _IzomPropUICodegenRuleTextMixin,
    _IzomPropUICodegenLayoutConditionsMixin,
    _IzomPropUICodegenLayoutEntryStyleMixin,
    _IzomPropUICodegenLayoutComponentsMixin,
    _IzomPropUICodegenLayoutLabelsMixin,
    _IzomPropUICodegenPropertyCellMixin,
    _IzomPropUICodegenSpecialCellMixin,
    _IzomPropUICodegenEntryCellMixin,
    _IzomPropUICodegenTextCellMixin,
    _IzomPropUICodegenSlotCellMixin,
    _IzomPropUICodegenStandardGroupMixin,
    _IzomPropUICodegenFillGroupMixin,
    _IzomPropUICodegenGroupDispatchMixin,
):
    pass

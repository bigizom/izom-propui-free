# SPDX-License-Identifier: GPL-3.0-or-later


IZOM_PROPUI_FREE_BOOL_VISIBILITY_ITEMS = [
    ('ALWAYS', 'Always', 'Always show this child property'),
    ('WHEN_TRUE', 'When Parent Is On', 'Show only when the parent boolean is enabled'),
    ('WHEN_FALSE', 'When Parent Is Off', 'Show only when the parent boolean is disabled'),
]

IZOM_PROPUI_FREE_NUMBER_VISIBILITY_ITEMS = [
    ('ALWAYS', 'Always', 'Always show this child property'),
    ('EQUAL', 'When Parent Equals', 'Show only when the parent equals a specific value'),
    ('GREATER', 'When Parent Is At Least', 'Show only when the parent is at or above a specific value'),
    ('LESS', 'When Parent Is At Most', 'Show only when the parent is at or below a specific value'),
    ('RANGE', 'When Parent In Range', 'Show only when the parent is within a specific range'),
]

IZOM_PROPUI_FREE_VALUE_LABEL_MATCH_MODE_ITEMS = [
    ('EQUAL', 'Equals', 'Match only when the value equals this value'),
    ('GREATER', 'At Least', 'Match when the value is at or above this value'),
    ('LESS', 'At Most', 'Match when the value is at or below this value'),
    ('RANGE', 'In Range', 'Match when the value is between the two values'),
]

IZOM_PROPUI_FREE_MULTI_COMPONENT_LAYOUT_ITEMS = [
    ('INLINE', 'One Row', 'Draw array components inline in one generated UI row'),
    ('SPLIT_LABEL', 'One Row, Split Label', "Use Blender's split-label style for the main label while keeping the value in the same generated UI row"),
    ('INLINE_LABEL', 'One Row, Label Above', 'Draw the label above one inline component row inside the same generated UI cell'),
    ('STACKED', 'Separate Rows', 'Draw array components on separate lines inside the same generated UI cell'),
    ('STACKED_SPLIT_LABEL', 'Separate Rows, Split Main Label', "Use Blender's split-label style for the main label while keeping component labels with the value controls"),
    ('STACKED_COMPONENT_SPLIT_LABEL', 'Separate Rows, Split Component Labels', "Draw the main label above, then use Blender's split-label style on each component row"),
]

IZOM_PROPUI_FREE_MULTI_COMPONENT_LAYOUT_IDS = frozenset(
    identifier for identifier, _label, _description in IZOM_PROPUI_FREE_MULTI_COMPONENT_LAYOUT_ITEMS
)

IZOM_PROPUI_FREE_STANDALONE_MULTI_COMPONENT_LABEL_ABOVE_LAYOUT_IDS = frozenset({
    'INLINE_LABEL',
    'STACKED',
    'STACKED_COMPONENT_SPLIT_LABEL',
})

IZOM_PROPUI_FREE_NATIVE_MULTI_COMPONENT_LAYOUT_IDS = frozenset({
    'INLINE',
    'SPLIT_LABEL',
    'INLINE_LABEL',
})


def izom_propui_free_normalize_multi_component_layout(value, default='INLINE'):
    fallback = str(default or 'INLINE').strip().upper() or 'INLINE'
    if fallback not in IZOM_PROPUI_FREE_MULTI_COMPONENT_LAYOUT_IDS:
        fallback = 'INLINE'
    normalized = str(value or fallback).strip().upper() or fallback
    return normalized if normalized in IZOM_PROPUI_FREE_MULTI_COMPONENT_LAYOUT_IDS else fallback


IZOM_PROPUI_FREE_MULTI_COMPONENT_DRAW_MODE_ITEMS = [
    ('WIDGET', 'Native Control', 'Use Blender native whole-value controls for color and direction subtypes'),
    ('COMPONENTS', 'Component Fields', 'Draw individual component fields'),
]

IZOM_PROPUI_FREE_MULTI_COMPONENT_DRAW_MODE_IDS = frozenset(
    identifier for identifier, _label, _description in IZOM_PROPUI_FREE_MULTI_COMPONENT_DRAW_MODE_ITEMS
)

IZOM_PROPUI_FREE_NATIVE_CONTROL_SUBTYPES = frozenset({
    'COLOR',
    'COLOR_GAMMA',
    'DIRECTION',
})


def izom_propui_free_normalize_multi_component_draw_mode(value, default='WIDGET'):
    fallback = str(default or 'WIDGET').strip().upper() or 'WIDGET'
    if fallback not in IZOM_PROPUI_FREE_MULTI_COMPONENT_DRAW_MODE_IDS:
        fallback = 'WIDGET'
    normalized = str(value or fallback).strip().upper() or fallback
    if normalized in IZOM_PROPUI_FREE_MULTI_COMPONENT_DRAW_MODE_IDS:
        return normalized
    return fallback


def izom_propui_free_subtype_supports_native_control(subtype):
    return str(subtype or 'NONE').strip().upper() in IZOM_PROPUI_FREE_NATIVE_CONTROL_SUBTYPES


IZOM_PROPUI_FREE_VALUE_LABEL_LAYOUT_ITEMS = [
    ('INLINE', 'One Row', 'Draw the label and value in one generated UI row'),
    ('SPLIT_LABEL', 'One Row, Split Label', "Use Blender's property-split row so the label sits to the left of the value field or checkbox"),
    ('LABEL_ABOVE', 'Label Above', 'Draw the label above the value field in the generated UI'),
]

IZOM_PROPUI_FREE_VALUE_LABEL_LAYOUT_IDS = frozenset(
    identifier for identifier, _label, _description in IZOM_PROPUI_FREE_VALUE_LABEL_LAYOUT_ITEMS
)


def izom_propui_free_normalize_value_label_layout(value, default='INLINE'):
    fallback = str(default or 'INLINE').strip().upper() or 'INLINE'
    if fallback not in IZOM_PROPUI_FREE_VALUE_LABEL_LAYOUT_IDS:
        fallback = 'INLINE'
    normalized = str(value or fallback).strip().upper() or fallback
    return normalized if normalized in IZOM_PROPUI_FREE_VALUE_LABEL_LAYOUT_IDS else fallback


IZOM_PROPUI_FREE_FLOAT_ARRAY_SUBTYPE_ITEMS = [
    ('NONE', 'None', 'No special array subtype behavior'),
    ('COLOR', 'Linear Color', 'Color in the linear space'),
    ('COLOR_GAMMA', 'Gamma-Corrected Color', 'Color in the gamma corrected space'),
    ('TRANSLATION', 'Translation', 'Translation'),
    ('DIRECTION', 'Direction', 'Direction'),
    ('VELOCITY', 'Velocity', 'Velocity'),
    ('ACCELERATION', 'Acceleration', 'Acceleration'),
    ('EULER', 'Euler Angles', 'Euler rotation angles in radians'),
    ('QUATERNION', 'Quaternion Rotation', 'Quaternion rotation'),
    ('AXISANGLE', 'Axis-Angle', 'Angle and axis to rotate around'),
    ('XYZ', 'XYZ', 'XYZ'),
]

IZOM_PROPUI_FREE_ARRAY_SUBTYPE_ITEMS = IZOM_PROPUI_FREE_FLOAT_ARRAY_SUBTYPE_ITEMS

IZOM_PROPUI_FREE_FLOAT_SUBTYPE_ITEMS = [
    ('NONE', 'None', 'No special float subtype'),
    ('PIXEL', 'Pixel', 'Pixel value'),
    ('UNSIGNED', 'Unsigned', 'Unsigned number'),
    ('PERCENTAGE', 'Percentage', 'Percentage'),
    ('FACTOR', 'Factor', 'Factor'),
    ('ANGLE', 'Angle', 'Angle in radians'),
    ('TIME', 'Time (Scene Relative)', 'Time in scene frames converted to seconds'),
    ('TIME_ABSOLUTE', 'Time (Absolute)', 'Time in seconds'),
    ('DISTANCE', 'Distance', 'Distance value'),
    ('DISTANCE_CAMERA', 'Camera Distance', 'Camera distance value'),
    ('POWER', 'Power', 'Power value'),
    ('TEMPERATURE', 'Temperature', 'Temperature value'),
    ('WAVELENGTH', 'Wavelength', 'Wavelength value'),
    ('COLOR_TEMPERATURE', 'Color Temperature', 'Color temperature value'),
    ('FREQUENCY', 'Frequency', 'Frequency value'),
]

IZOM_PROPUI_FREE_TEXT_ALIGNMENT_ITEMS = [
    ('LEFT', 'Left', 'Align the text to the left side of the row'),
    ('CENTER', 'Center', 'Align the text to the center of the row'),
    ('RIGHT', 'Right', 'Align the text to the right side of the row'),
]

IZOM_PROPUI_FREE_TEXT_ROLE_ITEMS = [
    ('TEXT', 'Text', 'Draw a text label row'),
    ('DIVIDER', 'Divider', 'Draw a single generated-row divider line'),
    ('SPACER', 'Spacer', 'Draw empty generated-row space'),
]

IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_MIN = 1.0
IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_MAX = 2.0
IZOM_PROPUI_FREE_LAYOUT_ROW_HEIGHT_SCALE_DEFAULT = 1.0
IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_MIN = 1.5
IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_MAX = 1.5
IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_AMOUNT_DEFAULT = 1.5
IZOM_PROPUI_FREE_LAYOUT_ROW_INSET_UNIT_SCALE = 0.7

IZOM_PROPUI_FREE_RULE_SOURCE_BOOL_STATE_ITEMS = [
    ('WHEN_FALSE', 'When Off', 'Match when the selected boolean component is off'),
    ('WHEN_TRUE', 'When On', 'Match when the selected boolean component is on'),
]

IZOM_PROPUI_FREE_OTHER_LABEL_RULE_KIND_ITEMS = [
    ('LABEL', 'Label Override', 'Use this row label as the override result'),
    ('FALLBACK', 'Fallback', 'Reset to the current fallback label for this rule set instead of using an override label'),
]

IZOM_PROPUI_FREE_INTERNAL_PROP_IDS = {
    '_RNA_UI',
}

IZOM_PROPUI_FREE_ENTRY_TREE_MAX_DEPTH = 12
IZOM_PROPUI_FREE_ARRAY_SIZE_MIN = 1
IZOM_PROPUI_FREE_ARRAY_SIZE_MAX = 32
IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TAB = 'Controls'
IZOM_PROPUI_FREE_DEFAULT_GENERATED_PANEL_TITLE = 'Custom Controls'

from .exports import izom_propui_free_public_names  # noqa: E402,F401

__all__ = izom_propui_free_public_names(globals(), all_public=True)

# izom PropUI Free

Build native Blender control panels without writing their layout by hand. Add controls, arrange them into rows and generate a panel in the 3D Viewport sidebar.

**Version 1.1.6 · Blender 5.0 or newer · GPL-3.0-or-later**

[**Download Free**](https://github.com/bigizom/izom-propui-free/releases/latest) · [PropUI website](https://propui.bigizom.com/)

## Make your first panel

1. Download **izom_propui_free-1.1.6.zip** from Releases. Use this installation ZIP rather than GitHub's source-code archive.
2. Install the ZIP through Blender's extension/add-on installer and enable **izom PropUI Free**.
3. Open the 3D Viewport sidebar with **N**, then choose **PropUI Free**.
4. Choose an existing Object under **Property Storage**.
5. Add controls to **Entry List** and adjust them under **Selected Entry**.
6. Add the controls to **Generated Layout**, arrange their rows, and choose a **Sidebar Tab** and **Panel Title**.
7. Press **Generate UI**.

The controls use Blender's normal custom properties and UI widgets. Use native animation and drivers where Blender supports them. Connecting a property to a rig, material or other scene behavior uses Blender's usual driver workflow; creating a control does not automatically make those connections.

## Controls

| Type | Use it for |
|---|---|
| Float | Decimal values, with limits, soft limits, step, precision, subtypes and optional slider display. |
| Integer | Whole-number values with limits, soft limits and step, shown as a normal number field. |
| Boolean | True/false checkboxes, with optional labels for each state. |
| Array | Float, integer or Boolean components, including supported native color/vector widgets. |
| Text | Headings, labels, dividers and spacers, with alignment, alert styling and optional icons. |

All property controls in a Free setup use one storage Object. Each has a **Property ID**, which identifies its custom property on that Object. Use different IDs for controls that need separate values. A Text entry creates no custom property.

Arrays support up to **32 components**. Choose a whole native widget where the subtype supports it, or show individual component fields. Free uses plain integer fields and Boolean checkboxes.

## Arrange your panel

**Entry List** holds the controls and their settings. **Generated Layout** decides which controls appear and where they appear. Removing an item from Generated Layout keeps its entry in Entry List.

Add, duplicate, remove and reorder entries with the list controls. Combine up to **three controls in a row**, adjust row height from **1 to 2**, or enable a fixed left indent. Safe Import helps bring entries into Generated Layout without unnecessarily disturbing existing rows.

Scalar controls offer **One Row**, **One Row, Split Label** and **Label Above**. Arrays also offer separate component rows and split-label layouts. Text icons can **Hug Text** when the text is centered; left and right alignment already keep icons attached.

Search follows the current tree view. Expand a parent, or turn off tree hints for a flat view, to find entries inside collapsed groups. Search preserves your selection and saved collapse state.

## Labels and visibility

**Dynamic Labels** changes a property's label according to its own value. Rules run from top to bottom; the first match wins. Numeric comparisons, ranges and supported array/component matches let labels respond to the control. Boolean controls can use different labels for true and false.

Set **Parent** to connect a child entry to another entry, then configure **Child Visibility**. For example, a Boolean parent can show extra controls only when enabled. Parenting affects the generated panel as well as the authoring list.

Free supports child visibility. Dynamic text on Text entries, labels driven by other entries, and conditions that leave a child visible but disabled belong to other PropUI editions.

## Save and reuse

- Save the **.blend** to keep the editor setup with its Scene and the custom property values on their storage Object.
- Generated panel code is saved as a Blender **Text datablock**. Blender's script-trust settings control whether it can run automatically when opening a file. Allow scripts only for files you trust.
- Export **setup JSON** to reuse a panel design in another file, or use the clipboard transfer. Setup JSON does not bundle the storage Object or the rest of the scene.
- Imports show a preview and conversion notes before replacing your setup. Cancel keeps the current setup.

Free accepts compatible setups from Free, Full and Rigify. It retains supported Float, Integer, Boolean, Array and Text controls, converts compatible settings, and explains skipped or simplified content. Unsupported entry types are skipped; advanced containers are flattened and oversized rows are split. Review the preview, choose valid Object storage and generate the panel after import.

## Generate safely

Normal generation creates or updates the managed properties. **Replace Storage** and **Clean Old Targets** can remove properties; review their confirmations before accepting them. Keep a saved copy of important scene work.

If generation fails, Free restores its property-storage changes. Interrupted setup exports preserve the previous destination file. Diagnostics provide details you can copy when reporting a problem.

If a generated control is missing, check that it is included in Generated Layout and that its parent visibility allows it to appear. If the panel is missing after reopening a file, check Blender's script permission and the generated Text datablock. If storage cannot be found, choose a valid Object again.

## Choosing an edition

Free is designed for a simple Object-based sidebar panel with the five control types above. Other PropUI editions offer existing-property capture, additional entry types, operator buttons, richer layouts and Rigify integration. Free setup JSON can be imported into those editions when your panel needs grow.

See the [PropUI website](https://propui.bigizom.com/) for the available editions.

## License

izom PropUI Free is licensed under [GPL-3.0-or-later](LICENSE.txt).

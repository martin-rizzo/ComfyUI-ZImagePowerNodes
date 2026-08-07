/**
 * File    : custom_widgets.js
 * Purpose : Register all custom widgets used in this project.
 * Author  : Martin Rizzo | <martinrizzo@gmail.com>
 * Date    : Feb 3, 2026
 * Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
 * License : MIT
 *- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
 *                        ComfyUI-ZImagePowerNodes
 *       ComfyUI nodes designed specifically for the "Z-Image" model.
 *_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
*/
import { app }                          from "../../../scripts/app.js";
import { addSeparatorWidget }           from "./custom_widgets/separator_widget.js";
import { addVisualStyleGalleryWidget }  from "./custom_widgets/ui_styles.js";
import { addColorPaletteGalleryWidget } from "./custom_widgets/ui_palettes.js";
import { addStyleGalleryButton }        from "./custom_widgets/style_gallery_button.js";
import { CustomStylesComboController }  from "./custom_widgets/custom_styles_combo.js";
const ENABLED = true;

/**
 * Creates and adds a Combo widget that automatically synchronizes custom styles
 * from the user's style definitions.
 *
 * This function is called directly by the ComfyUI framework whenever a node
 * containing this widget is instantiated.
 *
 * @param {LGraphNode} node - The node instance where the widget must be added
 * @param {string}     name - Unique identifier for the widget (not used for value serialization)
 * @param {Array}      data - Configuration array where:
 *                                  - [0] = Widget type name
 *                                  - [1] = Object containing the widget configuration.
 * @param {object}     _app - The ComfyApp instance (not used in this implementation)
 * @returns {{ widget: object }}
 *     Object containing the created widget instance.
 */
function _addCustomStyleSelector(node, name, data, _app) {
    const _type         = data[0];
    const widgetOptions = data[1] || {};
    const defaultValue  = widgetOptions.default;

    // create the widget and apply the controller to it
    widgetOptions.values = [];
    const widget = node.addWidget('combo', name, defaultValue, function () {}, widgetOptions);
    node.zipnCustStylesController = new CustomStylesComboController(widget, node, widgetOptions.options);
    return { widget: widget };
}

//#=========================================================================#
//#////////////////////////// REGISTER EXTENSION ///////////////////////////#
//#=========================================================================#

app.registerExtension({
    name: "ZImagePowerNodes.CustomWidgets",

    /** Called when the extension is loaded. */
    init() {
        if( !ENABLED ) return;
        console.log(`[${this.name}]: Extension loaded.`);
    },

    /** Called to register custom widgets. */
    getCustomWidgets() {
        if( !ENABLED ) return {};
        return {
            "ZIPN_SEPARATOR"            : addSeparatorWidget,
            "ZIPN_STYLE_SELECTOR"       : addVisualStyleGalleryWidget,
            "ZIPN_PALETTE_SELECTOR"     : addColorPaletteGalleryWidget,
            "ZIPN_CUSTOM_STYLE_SELECTOR": _addCustomStyleSelector,

            // [DEPRECATED]
            "ZIPN_STYLE_GALLERY_BUTTON": addStyleGalleryButton,
        };
    },

});

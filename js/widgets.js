/**
 * File    : widgets.js
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
import { app }                      from '../../../scripts/app.js';
import { GalleryWidget }            from './widgets/gallery_widget.js';
import { SeparatorWidget }          from './widgets/separator_widget.js';
import { addStyleGalleryButton }    from './widgets/style_gallery_button.js';
import { UserInputComboController } from './widgets/user_input_combo_controller.js';
import { StyleWidgetDelegate  , requireVisualStyleGalleryDialog  } from './widgets/ui_styles.js';
import { PaletteWidgetDelegate, requireColorPaletteGalleryDialog } from './widgets/ui_palettes.js';
const ENABLED = true;


/**
 * Adds a separator widget to the node.
 *
 * The data[1] (options) object supports the following properties:
 *  - `mode`      {string}: Determines the visual appearance. Available modes:
 *                          "spacer" (empty vertical padding), "divider" (standard line),
 *                          "dotted" (dashed line), or "bold" (thick line).
 *  - `color`     {string}: A CSS color string to define the line color.
 *  - `height`    {number}: The total vertical space allocated for the widget in pixels.
 *  - `thickness` {number}: The line weight in pixels.
 *
 * @param {Object} node - The node instance where the widget will be attached.
 * @param {string} name - The name identifier for the widget.
 * @param {Array}  data - Configuration array where:
 *                        - [0] = widget type name
 *                        - [1] = object containing the optional configurations.
 * @param {Object} _app - The ComfyApp instance.
 *
 * @returns {{ widget: Object }}
 *     An object containing the added separator widget instance.
 */
function _addSeparator(node, name, data, _app) {
    const type   = data[0];
    const kwargs = data[1] || {};
    const widget = node.addCustomWidget( new SeparatorWidget(type, name, kwargs) );
    return { widget: widget };
}


/**
 * Adds a `Style Selector` widget that utilizes a gallery dialog to select the style.
 *
 * @param {Object} node - The node instance where the widget will be added.
 * @param {string} name - The name identifier for the widget.
 * @param {Array}  data - Configuration array where:
 *                        - [0] = widget type name
 *                        - [1] = object containing the optional configurations.
 * @param {Object} _app - The ComfyApp instance.
 *
 * @returns {{ widget: Object }}
 *     An object containing the added style selector widget.
 */
function _addStyleSelector(node, name, data, _app) {
    const type          = data[0];
    const kwargs        = data[1] || {};
    const widgetConfig = {
        height        : 40,
        allow_variants: false,
        endpoint      : '',
        images_url    : '',
        dialog        : {},
        ...kwargs
    };
    const dialogConfig = {
        title     : 'Visual Styles',
        size      : 'default',
        view_mode : 'grid',
        icon      : 'mdi.mdi-image-multiple-outline',
        endpoint  : widgetConfig.endpoint,
        images_url: widgetConfig.images_url,
        ...widgetConfig.dialog
    };
    const widgetDelegate = new StyleWidgetDelegate(widgetConfig.endpoint, widgetConfig.images_url);
    let widget = new GalleryWidget(type, node, name, widgetConfig, widgetDelegate, (widget) =>
    {
        // launch dialog and update widget value
        const styleDialog  = requireVisualStyleGalleryDialog(dialogConfig.endpoint, dialogConfig.images_url);
        const currentStyle = widget.value;
        styleDialog.launch( dialogConfig, currentStyle, (selectedStyle) => {
            widget.forceUpdate( selectedStyle );
        });
    });
    widget = node.addCustomWidget( widget );
    return { widget: widget };
}


/**
 * Adds a `Palette Selector` widget that utilizes a gallery dialog to select a palette.
 *
 * @param {Object} node - The node instance where the widget will be added.
 * @param {string} name - The name identifier for the widget.
 * @param {Array}  data - Configuration array where:
 *                        - [0] = widget type name
 *                        - [1] = object containing the optional configurations.
 * @param {Object} _app - The ComfyApp instance.
 *
 * @returns {{ widget: Object }}
 *     An object containing the added palette selector widget.
 */
function _addPaletteSelector(node, name, data, _app) {
    const type   = data[0];
    const kwargs = data[1] || {};
    const widgetConfig = {
        height        : 40,
        allow_variants: false,
        endpoint      : '',
        dialog        : {},
        ...kwargs
    };
    const dialogConfig = {
        title    : 'Color Palettes',
        size     : 'small',
        view_mode: 'list',
        icon     : 'mdi.mdi-palette-outline',
        endpoint : widgetConfig.endpoint,
        ...widgetConfig.dialog
    };
    const widgetDelegate = new PaletteWidgetDelegate(widgetConfig.endpoint);
    let widget = new GalleryWidget(type, node, name, widgetConfig, widgetDelegate, (widget) =>
    {
        // launch dialog and update widget value
        const paletteDialog  = requireColorPaletteGalleryDialog(dialogConfig.endpoint);
        const currentPalette = widget.value;
        paletteDialog.launch( dialogConfig, currentPalette, (selectedPalette) => {
            widget.forceUpdate( selectedPalette );
        });
    });
    widget = node.addCustomWidget( widget );
    return { widget: widget };
}


/**
 * Adds a COMBO widget that automatically synchronizes items from user input text.
 *
 * @param {Object} node - The node instance where the widget will be added.
 * @param {string} name - The name identifier for the widget.
 * @param {Array}  data - Configuration array where:
 *                        - [0] = string with the widget type
 *                        - [1] = object containing the optional configurations.
 * @param {Object} _app - The ComfyApp instance. (no usado actualmente)
 *
 * @returns {{ widget: Object }}
 *     An object containing the added combo box widget.
 */
function _addUserInputComboBox(node, name, data, _app) {
    const _type  = data[0];
    const kwargs = data[1] || {};
    const widgetConfig = {
        user_input : 'user_input',
        item_marker: '>>>',
        values     : [],
        ...kwargs
    };
    // create the `COMBO` widget and attach the controller to it
    const widget = node.addWidget('combo', name, kwargs.default, function () {}, widgetConfig);
    widget.zipnController = new UserInputComboController(widget, node,
                                                         widgetConfig.user_input,
                                                         widgetConfig.options,
                                                         widgetConfig.item_marker);
    return { widget: widget };
}


//#=========================================================================#
//#////////////////////////// REGISTER EXTENSION ///////////////////////////#
//#=========================================================================#

app.registerExtension({
    name: 'ZImagePowerNodes.CustomWidgets',

    /** Called when the extension is loaded. */
    init() {
        if( !ENABLED ) return;
        console.log(`[${this.name}]: Extension loaded.`);
    },

    /** Called to register custom widgets. */
    getCustomWidgets() {
        if( !ENABLED ) return {};
        return {
            'ZIPN_SEPARATOR'         : _addSeparator,
            'ZIPN_STYLE'             : _addUserInputComboBox,
            'ZIPN_PALETTE'           : _addUserInputComboBox,
            'ZIPN_PREDEFINED_STYLE'  : _addStyleSelector,
            'ZIPN_PREDEFINED_PALETTE': _addPaletteSelector,

            // [DEPRECATED]
            'ZIPN_STYLE_GALLERY_BUTTON': addStyleGalleryButton,
        };
    },

});

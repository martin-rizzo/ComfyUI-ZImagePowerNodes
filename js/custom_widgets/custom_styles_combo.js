/**
 * File    : custom_styles_combo.js
 * Purpose : A combo box to select custom styles that updates automatically
 *           based on the style templates created by the user.
 * Author  : Martin Rizzo | <martinrizzo@gmail.com>
 * Date    : Aug 2, 2026
 * Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
 * License : MIT
 *- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
 *                        ComfyUI-ZImagePowerNodes
 *       ComfyUI nodes designed specifically for the "Z-Image" model.
 *_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
 */
export { CustomStylesComboController };
import { schedulePeriodicCallback } from '../common_timer.js';
import { getInputNode }             from '../common.js';

// Captures styles names from the custom styles template configuration.
const STYLE_NAME_REGEX = />>>\s*(.*?)\s*$/gm;


/**
 * The controller class for the "COMBO" widget that provides a dynamic
 * list of custom styles by reading them from a linked text node.
 */
class CustomStylesComboController {

    /**
     * Creates an instance of this controller.
     *
     * @param {Object}        widget              - The combo widget to be controlled.
     * @param {ComfyNode}     node                - The ComfyUI node instance where the widget is attached.
     * @param {Array<string>} defaultCustomStyles - A list of custom styles to display when the node
     *                                              is not connected to any text.
     */
    constructor(widget, node, defaultCustomStyles) {
        this.node                    = node;
        this.widget                  = widget;
        this.inputName               = "custom_styles";
        this.comboBoxOptions         = [];
        this.defaultOptions          = [];
        this.defaultLowercaseOptions = new Set();

        if( Array.isArray(defaultCustomStyles) ) {
            this.defaultOptions          = defaultCustomStyles;
            this.defaultLowercaseOptions = new Set(defaultCustomStyles.map(s => s.toLowerCase()));
        }

        this.lastInputText   = null;
        this.lastInputStyleNames = null;

        // bind widget options to the dynamic array (`this.comboBoxOptions`),
        // allowing real-time updates of the dropdown list
        this.widget.options.values = () => this.comboBoxOptions;

        // schedule periodic checks to update the list
        // of available custom styles based on node input
        schedulePeriodicCallback(node, () => this.checkAndSyncOptions());
    }

    /**
     * Monitors the input node for changes and updates the combo widget options accordingly.
     *
     * This method reads the input node's text and extract the custom styles names
     * from it. It then updates the combo widget options when the any style name changes.
     */
    checkAndSyncOptions() {
        const inputNode = getInputNode(this.node, this.inputName);
        const inputText = inputNode?.widgets[0].value || "";

        // check if the input text has actually changed
        if( this.lastInputText === inputText ) { return; }
        this.lastInputText = inputText;

        // extract style names based on `STYLE_NAME_REGEX`
        const inputStyleArray = [...inputText.matchAll(STYLE_NAME_REGEX)].map(match => match[1].trim()).filter(name => name.length > 0);
        const inputStyleNames = inputStyleArray.join("\n");

        // check if the extracted custom style names have changed
        if( this.lastInputStyleNames === inputStyleNames ) { return; }
        this.lastInputStyleNames = inputStyleNames;

        // if all input style names are contained within the default options,
        // use default options
        const allInDefaults = inputStyleArray.every(style => this.defaultLowercaseOptions.has(style.toLowerCase()));
        if( allInDefaults ) {
            this.resetToDefaultOptions();
            return;
        }
        // update the combo box options with the custom style names
        try {
            this.updateComboBoxOptions( inputStyleArray );
        }
        catch( error ) {
            this.resetToDefaultOptions();
            console.error("CustomStylesComboController cannot update options:", error);
        }
    }

    /**
     * Updates the combo box options by processing a string or an array of strings.
     *
     * @param {string|string[]} options - The new options to be set for the combo box.
     *                                    If a string is provided, items should be
     *                                    separated by newline characters.
     */
    updateComboBoxOptions(options) {
        // ensure the input is converted into an array of strings
        const optionArray =
            Array.isArray(options)      ? options :
            typeof options === 'string' ? options.split('\n') :
            null;
        if( !optionArray ) {
            throw new Error("Invalid input type, expected string or array of strings.");
        }
        // update options (removing whitespace and filtering out empty options)
        this.comboBoxOptions = optionArray
            .map(style => String(style).trim())
            .filter(style => style.length > 0);
    }

    /**
     * Resets the widget options to the provided defaultCustomStyles.
     */
    resetToDefaultOptions() {
        this.comboBoxOptions = this.defaultOptions;
    }
}

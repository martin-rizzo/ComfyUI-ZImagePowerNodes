/**
 * File    : user_input_combo_controller.js
 * Purpose : Controller for combo boxes that automatically updates options
 *           based on user-defined text input.
 * Author  : Martin Rizzo | <martinrizzo@gmail.com>
 * Date    : Aug 23, 2026
 * Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
 * License : MIT
 *- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
 *                        ComfyUI-ZImagePowerNodes
 *       ComfyUI nodes designed specifically for the "Z-Image" model.
 *_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
 */
export { UserInputComboController };
import { schedulePeriodicCallback } from '../common_timer.js';
import { getInputNode }             from '../common.js';

/**
 * Controller class to manage dynamic combo box options in ComfyUI nodes
 * based on plain text user input.
 */
class UserInputComboController {
    /**
     * Creates an instance of this controller.
     *
     * @param {Object}        widget          - The combo widget to be controlled.
     * @param {ComfyNode}     node            - The ComfyUI node instance where the widget is attached.
     * @param {string}        userInput       - The name of the node input from where to read the user-created items.
     * @param {Array<string>} defaultItems    - A list of item names to display when the node input is not connected.
     * @param {string}        [itemTag=">>>"] - The custom tag used to capture item names from the text input.
     */
    constructor(widget, node, userInput, defaultItems, itemTag = ">>>") {
        this.node                    = node;
        this.widget                  = widget;
        this.userInput               = userInput;
        this.comboBoxOptions         = [];
        this.defaultOptions          = [];
        this.defaultLowercaseOptions = new Set();

        // escape special regular expression characters in `itemTag`;
        // adds a backslash (\) before symbols like '*' or '$' so
        // they are treated as literal text
        const escapedItemTag = itemTag.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        this.itemNameRegex = new RegExp(`^${escapedItemTag}\\s*(.*?)\\s*$`, 'gm');

        if( Array.isArray(defaultItems) ) {
            this.defaultOptions          = defaultItems;
            this.defaultLowercaseOptions = new Set(defaultItems.map(s => s.toLowerCase()));
        }

        this.lastInputText      = null;
        this.lastInputItemNames = null;

        // bind widget options to the dynamic array `this.comboBoxOptions`,
        // allowing real-time updates of the dropdown list
        this.widget.options.values = () => this.comboBoxOptions;

        // schedule periodic checks to update the list
        // of available custom items based on node input
        schedulePeriodicCallback(node, () => this.checkAndSyncOptions());
    }

    /**
     * Monitors the node input for changes and updates the combo widget options accordingly.
     *
     * This method reads the text of the node connected to the input, extracts
     * the item names from it using the configured regex, and then updates
     * the combo widget options when any name changes.
     */
    checkAndSyncOptions() {
        const userInputNode = getInputNode(this.node, this.userInput);
        const inputText     = userInputNode?.widgets[0].value || "";

        // check if the input text has actually changed
        if( this.lastInputText === inputText ) {
            return;
        }
        this.lastInputText = inputText;

        // extract item names based on `this.itemNameRegex`
        const inputItemArray = [...inputText.matchAll(this.itemNameRegex)]
            .map(match => match[1].trim())
            .filter(name => name.length > 0);

        const inputItemNames = inputItemArray.join("\n");

        // check if the extracted custom item names have changed
        if( this.lastInputItemNames === inputItemNames ) {
            return;
        }
        this.lastInputItemNames = inputItemNames;

        // update the combo box options with the custom item names
        try {
            this.updateComboBoxOptions(inputItemArray);
        } catch (error) {
            this.resetToDefaultOptions();
            console.error("UserInputComboController cannot update options:", error);
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
            .map(item => String(item).trim())
            .filter(item => item.length > 0);

        // ensure the widget value remains valid after updating the option set.
        this.validateAndSyncWidgetValue();
    }

    /**
     * Validates the widget value against the current combo options.
     * If the current value is not present in the options list, it
     * replaces the value with the best matching option.
     */
    validateAndSyncWidgetValue() {
        const options = this.comboBoxOptions;
        const widget  = this.widget;

        // if the current value is already a valid option, no action is needed
        if( options.includes(widget.value) ) {
            return;
        }

        // since the current value is missing from the options,
        // search for the option that shares the longest common prefix with 'value'
        const value        = String(widget.value ?? '').toLowerCase();
        let   bestMatch    = undefined;
        let   maxPrefixLen = 0;

        for( const option of options ) {
            const optionLower = option.toLowerCase();
            let   prefixLen   = 0;
            const minLen      = Math.min(value.length, optionLower.length);

            while( prefixLen < minLen && value[prefixLen] === optionLower[prefixLen] ) {
                prefixLen++;
            }

            if( prefixLen > maxPrefixLen ) {
                maxPrefixLen = prefixLen;
                bestMatch    = option;
            }
        }

        // update value with the best match.
        // NOTE: This doesn't work for sub-graphs! value updates applied here
        //       will not reflect on the outer sub-graph's promoted widget
        const newValue = bestMatch || (options.length > 0 ? options[0] : "");
        widget.value = newValue;

        if( typeof widget.callback === 'function' ) {
            widget.callback(newValue);
        }
    }

    /**
     * Resets the widget options to the default names that were passed
     * in the constructor.
     */
    resetToDefaultOptions() {
        this.comboBoxOptions = this.defaultOptions;
    }

}

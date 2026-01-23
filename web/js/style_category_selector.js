/**
 * File    : style_category_selector.js
 * Purpose : Implement a 'style' widget that shows only the styles corresponding with the selected category.
 * Author  : Martin Rizzo | <martinrizzo@gmail.com>
 * Date    : Jan 22, 2026
 * Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
 * License : MIT
 *- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
 *                        ComfyUI-ZImagePowerNodes
 *       ComfyUI nodes designed specifically for the "Z-Image" model.
 *_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
*/
import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";
const ENABLED = true;
/**
 * Object encapsulating the style category selection functionality.
 * @typedef {Object} StyleCategorySelector
 *   @property {Object}                         categoryWidget     - The combobox that selects the category to show.
 *   @property {Object}                         styleWidget        - The combobox that will be refilled with styles.
 *   @property {Object.<string, Array<string>>} stylesByCategory   - An object mapping each category to a list of styles.
 *   @property {string}                         oldCategory        - The name of the last selected category.
 *   @property {Object.<string, string>}        selectedByCategory - An object storing the last selected style for each category.
 */


/**
 * Initializes the StyleCategorySelector object with specific widgets.
 * @param {StyleCategorySelector} self           - The StyleCategorySelector object to initialize.
 * @param {Object}                categoryWidget - The combobox that manages categories.
 * @param {Object}                styleWidget    - The combobox that manages styles.
 * @param {Object.<string, Array<string>>} stylesByCategory - An object mapping each category to a list of styles.
 */
function init(self, categoryWidget, styleWidget, stylesByCategory) {

    self.categoryWidget     = categoryWidget;
    self.styleWidget        = styleWidget;
    self.stylesByCategory   = stylesByCategory;
    self.oldCategory        = self.categoryWidget.value;
    self.selectedByCategory = {};

    // fill the style combo widget with all the styles from the current category
    fillStyleWidget(self, self.categoryWidget.value);

    // save the existing callback function
    const originalCallback = self.categoryWidget.callback;

    self.categoryWidget.callback = async (value) => {
        onCategoryChange(self, value);
        if (typeof originalCallback === 'function') { await originalCallback(value); }
    }
}


/**
 * Fills the style combo widget with styles corresponding to the given category.
 *
 * @param {StyleCategorySelector} self - The StyleCategorySelector object.
 * @param {string}            category - The name of the category whose styles should be displayed.
 * @returns {string}
 *     The name of the default style for the given category,
 *     which is either "none" or the first style available.
 */
function fillStyleWidget(self, category) {

    // if the category is not valid -> styles = ["none"]
    if( category in self.stylesByCategory === false ) {
        self.styleWidget.options.values = ["none"];
        return "none"
    }

    // fill the style combo widget with the option "none"
    // followed by all the styles from the category
    let styles = ["none"];
    const catStyles = self.stylesByCategory[category];
    for (let i = 0; i < catStyles.length; i++) {
        styles.push( catStyles[i] );
    }
    self.styleWidget.options.values = styles;

    // by default try to select the second style
    // (because the first always is "none")
    return styles[ styles.length>=2 ? 1 : 0 ]
}


/**
 * Handles the change in category by updating available styles.
 * @param {StyleCategorySelector} self - The StyleCategorySelector object whose category has changed.
 * @param {string}         newCategory - The name of the new selected category.
 */
function onCategoryChange(self, newCategory) {

    // store the selection that existed before the change
    self.selectedByCategory[ self.oldCategory ] = self.styleWidget.value;
    self.oldCategory = newCategory;

    // fill the style combo widget with all the styles for the new category
    // and get the default style for that category
    let defaultStyle = fillStyleWidget(self, newCategory);

    // if the category already had a previously selected style, use it as the default
    if( newCategory in self.selectedByCategory ) {
        defaultStyle = self.selectedByCategory[newCategory];
    }
    self.styleWidget.value = defaultStyle;
}


/**
 * Fetches available styles by category from the API.
 * @returns - An object mapping categories to list of styles, or an empty object on failure.
 */
async function fetchQuotedStylesByCategory() {
    try {
        const response = await api.fetchApi("/zi_power/quoted_styles/by_category");
        if ( response.ok ) { return await response.json();  }
    }
    catch (error) { console.error(error); }
    return {};
}


//#=========================================================================#
//#////////////////////////// REGISTER EXTENSION ///////////////////////////#
//#=========================================================================#

app.registerExtension({
    name: "ZImagePowerNodes.StyleCategorySelector",

    /**
     * Called when the extension is loaded.
     */
    init()
    {
        if (!ENABLED) return;
        console.log("##>> Style Prompt Encoder: extension loaded.")
    },

	/**
	 * Called every time ComfyUI creates a new node.
	 * @param {ComfyNode} node - The node that was created.
	 */
	async nodeCreated(node)
    {
		if (!ENABLED) return;
        const comfyClass = node?.comfyClass ?? "";

        // only applies to "Style & Prompt Encoder" and "Style String Injector"
		if( !comfyClass.startsWith("StylePromptEncoder " ) &&
            !comfyClass.startsWith("StyleStringInjector ")  )
        { return; }

        const categoryWidget   = node.widgets.find(w => w.name === "category");
        const styleWidget      = node.widgets.find(w => w.name === "style"   );
        const stylesByCategory = await fetchQuotedStylesByCategory();

        // if any of the widgets or stylesByCategory could not be created, return
        if( !categoryWidget || !styleWidget || Object.keys(stylesByCategory).length === 0 )
        { return; }

        node.styleCategorySelectorZ = {};
        init(node.styleCategorySelectorZ, categoryWidget, styleWidget, stylesByCategory);
	},

})

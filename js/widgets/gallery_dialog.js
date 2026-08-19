/**
 * File    : gallery_dialog.js
 * Purpose : A generic, customizable ComfyUI dialog for selecting items through an image gallery.
 * Author  : Martin Rizzo | <martinrizzo@gmail.com>
 * Date    : May 8, 2026
 * Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
 * License : MIT
 *- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
 *
 * While this class is part of the `ComfyUI-ZImagePowerNodes` suite, it was
 * designed to be as generic and modular as possible. The goal is for it to
 * be easily plug-and-play in any other ComfyUI Nodes project you might be
 * working on.
 *
 * Feel free to use it, modify it, or integrate it however you like! If you
 * find it useful, a quick shout-out to this project or a mention of my name
 * would be greatly appreciated. :)
 *
 * Note that although the code is currently compatible with Nodes 2.0, it
 * uses deprecated ComfyUI functions that may be removed at some point.
 * I intend to migrate the code to full compatibility as soon as official
 * Nodes 2.0 documentation becomes available.
 *_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
 */
export { GalleryDialog, GalleryDialogDelegate };
import { ComfyDialog, $el as html } from "../../../scripts/ui.js"; //< deprecated ??
const DIALOG_CONTENT_CLASS       = 'zipn-dialog';
const DIALOG_TITLE_CLASS         = 'zipn-dialog__title';
const DIALOG_ICON_HOLDER_CLASS   = 'zipn-dialog__icon';
const VIEWMODE_BTTN_HOLDER_CLASS = 'zipn-dialog__viewmode';
const DEFAULT_TITLE        = 'Dialog';
const DEFAULT_TITLE_ICON   = 'mdi.mdi-image-multiple-outline';
const DEFAULT_CACHE_BUSTER = Math.floor(Date.now() / 3600000);
const DEFAULT_VARIANT_NAME = "default";


/**
 * This type represents a gallery "Item" with metadata and display properties.
 * These items are supplied by the {@link GalleryDialogDelegate} through
 * its `fetchItemArray()` function.
 *
 * @typedef {Object} GalleryDialogItem
 * @property {number} idx           - (Required) The position index of the item in the provided array.
 * @property {string} name          - (Required) The name of the item, used for selection and display.
 * @property {string} [category]    - (Optional) The category of the item.
 * @property {string} [description] - (Optional) A detailed description of the item.
 * @property {string} [tags]        - (Optional) Tags associated with the item.
 * @property {string} [displayName] - (Internal) Display name that overrides the `name` property.
 *                                    Used for special display scenarios where the standard name
 *                                    should be temporarily replaced.
 */


/**
 * Base provider class for GalleryDialog.
 * Users should extend this class and implement the `fetchItemArray()`
 * and `getCategories()` methods.
 */
class GalleryDialogDelegate {

    /**
     * Fetches an array with data about each item to be displayed in the gallery.
     * Must be overridden by subclasses to implement data retrieval.
     *
     * @abstract
     * @returns {Promise<Array<Object>>}
     *   Resolves to the array of formatted gallery items.
     *   Each item object must contain the following properties:
     *       - idx        : Unique identifier for the item (the index in the list)
     *       - name       : The display name of the item (string)
     *       - category   : The category the item belongs to (string)
     *       - description: A detailed description of the item (string)
     *       - tags       : A list of strings containing associated tags (Array<string>)
     *
     * @example
     * // How to implement in a subclass:
     * class MyDelegate extends GalleryDialogDelegate {
     *     async fetchItemArray() {
     *         const data = await myApi.get('/items');
     *         return data.map((item, index) => ({
     *           idx        : index,
     *           name       : item.title,
     *           category   : item.group,
     *           description: item.desc,
     *           tags       : item.labels || [],
     *         }));
     *     }
     * }
     */
    async fetchItemArray() {
        throw new Error("Method 'fetchItemArray()' must be implemented by subclasses.");
    }

    /**
     * Returns an array of category definitions used for filtering the gallery items.
     *
     * When implemented, this method provides the categories used in the
     * gallery's filtering UI. Each category definition is an array of
     * three strings: [category, displayName, description].
     *
     * If not overridden, there will be no filtering available in the gallery.
     *
     * @returns {Array<Array<string>>}
     *   An array of category definitions where each item contains:
     *     - category    (string): The value used for matching gallery items (must match the "category" property in items)
     *     - displayName (string): The visible name shown in the UI
     *     - description (string): Tooltip description for screen readers/accessibility
     *
     * @example
     * class MyDelegate extends GalleryDialogDelegate {
     *   getCategories() {
     *     return [
     *       ['images'   , 'Images'   , 'View all image files'   ],
     *       ['videos'   , 'Videos'   , 'View all video files'   ],
     *       ['documents', 'Documents', 'View all document files']
     *     ];
     *   }
     * }
     */
    getCategories() {
        return null;
    }

    /**
     * Renders the main image HTML element for the selected item.
     * This method CAN be overridden to provide custom image rendering.
     *
     * The current implementation renders a lazy-loaded image using the item's
     * thumbnail property, or returns an empty string if the item or thumbnail
     * is missing.
     *
     * @param {Object|null} item - The data object representing the item, or `null` if no item is selected.
     * @param {string}      htmlClass   - CSS class to be applied to the img tag
     * @returns {string}
     *    The HTML string representing the image element
     *    or an empty string if the item or thumbnail is missing.
     */
    htmlItemImage(_item, _value, _options, _htmlClass) {
        throw new Error("Method 'htmlItemImage(..)' must be implemented by your subclass if your GalleryDialog is intended to show images.");
    }

    /**
     * Renders the HTML content of the panel displaying details of the selected item.
     * This method is NOT intended to be overridden by subclasses.
     *
     * The current implementation renders a structured layout consisting of
     * the item's name as a header, the item's image, and its description.
     *
     * @param {Object|null} item - The data object representing the item, or `null` if no item is selected.
     * @returns {string}
     *    The HTML string representing the content of the details panel.
     */
    htmlItemDetailsPane(item, name, options) {
        const imageHTML = this.htmlItemImage(item, name, options, 'zipn-image');
        return `
           <h1>${name || ""}</h1>
           ${imageHTML}
           <p>${item?.description || ""}</p>
           `;
    }

}

/**
 * Internal delegate for a sub-dialog that allows selection of variants for an item.
 * This delegate is forwards most functionality to the main `GalleryDialogDelegate`,
 * while customizing only the presentation for variant selection.
 *
 * The `variants` array is populated with sub-items/variants before launching
 * the sub-dialog. This is typically done via `delegate.variants = [...variants];`.
 * 
 * @class   _VariantsSubDialogDelegate
 * @extends GalleryDialogDelegate
 * @param {GalleryDialogDelegate} mainDelegate - The main delegate to which most methods are forwarded.
 */
class _VariantsSubDialogDelegate extends GalleryDialogDelegate {

    constructor(mainDelegate) {
        super();
        this.variants     = [];
        this.mainDelegate = mainDelegate;
    }
    async fetchItemArray() {
        return this.variants;
    }
    getCategories() {
        return null;
    }
    htmlItemImage(item, name, options, htmlClass) {
        return this.mainDelegate.htmlItemImage(item, name, options, htmlClass);
    }
    htmlItemDetailsPane(item, name, options) {
        return this.mainDelegate.htmlItemDetailsPane(item, name, options);
    }
}


//#=========================================================================#
//#//////////////////////////// GALLERY DIALOG /////////////////////////////#
//#=========================================================================#

/**
 * A wrapper class for `_GalleryDialog` that implements a lazy-initialization pattern.
 *
 * In the ComfyUI framework, `ComfyDialog` instances depend on the UI context being
 * fully initialized. To allow developers to declare `GalleryDialog` instances as
 * global variables or static properties during the application load phase, this
 * wrapper defers the actual instantiation of the underlying `_GalleryDialog`
 * until the `launch` method is explicitly called.
 *
 * @example
 *   // You can safely instantiate this early in your module
 *   const gallery = new GalleryDialog(new MyDelegate());
 *
 *   // The actual _GalleryDialog is created only when this is invoked
 *   gallery.launch({}, "default", (item) => console.log(item));
 */
class GalleryDialog {

    /**
     * Creates a new instance, registering a delegate object to customize the dialog behavior.
     * @param {GalleryDialogDelegate} delegate - The object that provides the item data and renderer.
     */
    constructor(delegate) {
        // ensure delegate has the right type
        if( !(delegate instanceof GalleryDialogDelegate) ) {
            throw new TypeError('delegate must be an instance of GalleryDialogDelegate');
        }
        this._instance = null;
        this.delegate  = delegate;
    }

    /**
     * Launches the gallery dialog with the provided configuration.
     * @param {Object}  options          - Optional configuration object for the gallery dialog, can be empty.
     * @param {string}  [options.title]  - The title to display in the dialog header
     * @param {string}  [options.icon]   - Icon to show before the title in the dialog header.
     *                                     * For PrimeIcons   : Use "pi.[icon name]" e.g., "pi.pi-image"; (see https://primevue.org/icons/#list)
     *                                     * For Pictogrammers: Use "mdi.[icon name]" e.g., "mdi.mdi-image"; (see https://pictogrammers.com/library/mdi)
     *                                     * Or empty string to hide the icon
     * @param {string}  [options.size]           - Force a diferent size for the dialog window. Supported values: "small", "default"
     * @param {string}  [options.view_mode]      - Force the view-mode of the dialog. Supported values: "list", or "grid"
     * @param {boolean} [options.allow_variants] - If True, enables grouping all the variants of the same item
     * @param {boolean} [options.cache_buster]   - Override the default cache-buster value
     * @param {string}  initialItemName - Name of the item to show selected when dialog opens
     * @param {Function} onSelect       - Callback function to execute when an item is selected
     * @example
     *   const myGalleryDialog = new GalleryDialog( new MyGalleryDialogDelegate() );
     *   const currentItemName = "default";
     *   myGalleryDialog.launch({}, currentItemName, (selectedItemName) => {
     *     console.log("Selected:", selectedItemName);
     *   });
     */
    launch(options, selectedName, onSelect) {

        // create the instance only once (singleton instance logic)
        if( !this._instance ) {
             this._instance = new _GalleryDialog(this.delegate);
        }
        // launch/relaunch the dialog
        this._instance.onLaunch(options, selectedName, onSelect);
    }
}


//#=========================================================================#
//#/////////////////////////////// INTERNAL ////////////////////////////////#
//#=========================================================================#

class _GalleryDialog extends ComfyDialog {

    /**
     * Creates a new instance, registering a delegate object to customize the dialog behavior.
     * @param {GalleryDialogDelegate} delegate - The object that provides the item data and renderer.
     */
    constructor(delegate) {
        super();
        _ensureCSSLoaded();

        //---- INTERNAL STATE VARIABLES -------------------
        // - should be re-initialized every time the dialog is launched

        /** @type {boolean} Indica si el diálogo está abierto. */
        this.isOpen = false;

        /** @type {string} The initial element name (before applying the selected one). */
        this.initialItemName = "";

        /** @type {number|null} IDX of the initial card/item (which will be highlighted). */
        this.initialCardIDX = null;

        /** @type {number|null} IDX of the card/item being pointed by the mouse. */
        this.hoveredCardIDX = null;

        /** @type {number|null} Index in `resultItem[]` of the card/item currently focused via keyboard arrow navigation. */
        this.resultIndex = null;

        /** @type {Array<object>} An array of elements that match the search text. */
        this.resultItems = [];

        /** @type {number} Number of columns used in the search results grid. */
        this.resultColumns = 4;  // grid=4 ; list=1

        /** @type {("grid"|"list")} User-selected view mode for the dialog, allows switching between grid and list view. */
        this.viewModeSelected = "grid";

        /** @type {(""|"grid"|"list")} Forced view mode that disables user option to change view mode. Empty string means view mode can be changed by user. */
        this.viewModeForced = "";

        /** @type {number|null} ID of the previously selected item. */
        this.oldSelectionIDX = null;

        /** @type {string} Text entered by the user to filter styles (case-insensitive). */
        this.textFilter = "";

        /** @type {string} Active category filter ("photo", "illustration", "wild", "custom"). Empty means all categories. */
        this.categoryFilter = "";

        //---- INTERNAL VARIABLES -------------------------

        /** @type {GalleryDialogDelegate} The object that provides the item data and renderer. */
        this.delegate = delegate;

        /** @type {Array<GalleryDialogItem>} An array to store items in ID order for fast access. */
        this.itemsByIDX = [];

        /** @type {Array<GalleryDialogItem>} */
        this.groupsByIDX = null;

        this.subDialog = null;

        /** @type {number|null} Timer used by the lockPointer method. */
        this.pointerLockedTimer = null;

        /** @type {number|null} Timer used by the 'onInputChange' event. */
        this.inputChangeTimer2 = null;

        /** @type {boolean} Flag used by 'onInputChange' to block mouse events. */
        this.isPointerLocked = false;

        /** @type {Array<[string, HTMLElement]>}
         *     The buttons in the toolbar that allow filtering by category.
         *     The array contains pairs of category name and button element. */
        this.categoryButtons = [];

        /** @type {Function|null} Callback function invoked when the user selects an item. */
        this.onSelectItem = null;

        // create the custom dialog
        this.element = _makeCustomDialog(
            DIALOG_TITLE_CLASS,
            DIALOG_ICON_HOLDER_CLASS,
            //-- DIALOG -------------------------
            html(`div.${DIALOG_CONTENT_CLASS}`,
                {}, [

                // UPPER TOOLBAR
                this.createToolbar(),

                // BODY
                html("div.zipn-dialog__body", {}, [
                    html("div.zipn-dialog__details"),
                    html("div.zipn-dialog__results", { id: "zipn-dialog__results" }, [
                        html("div.zipn-grid", { id: "zipn-search-results" })
                    ])
                ]),

                // FOOTER
                html("div.zipn-dialog__footer", {}, [
                    html("div.zipn-dialog__statusbar")
                ]),
            ]),
            //-- CLOSE CALLBACK -----------------
            () => this.onCancel()
        );

        //---- DIALOG ELEMENTS ----------------------------

        /** @type {HTMLElement|null} Search input element in the dialog. */
        this.searchInputEl = this.element.querySelector('#zipn-search-input');

        /** @type {HTMLElement|null} Element containing search results. */
        this.searchResultsEl = this.element.querySelector('#zipn-search-results');

        /** @type {HTMLElement|null} Element containing the details pane. */
        this.detailsPaneEL = this.element.querySelector('.zipn-dialog__details');

        //---- EVENT LISTENERS ----------------------------

        const CARD_SELECTOR = '.zipn-grid-card, .zipn-list-card';
        _setupCardHoverListeners( this.searchResultsEl, CARD_SELECTOR,
            (card     ) => { this.onCardEnter(card); },
            (_card    ) => { },
            (card     ) => { this.onCardClick(card); },
            (container) => { this.onCardContainerLeave(container); }
        );
        this.searchInputEl.addEventListener('input'  , (e) => { this.onInputChange(e.target); });
        this.searchInputEl.addEventListener('keydown', (e) => { if (this.onInputKeyDown(e.key)) { event.preventDefault(); } });
        this.searchInputEl.addEventListener('blur'   , ()  => { this.onInputLostFocus(); } );
    }


    /**
     * Returns the ID of the currently selected element.
     * @returns {number|null} The selected element's ID or null if no selection exists.
     */
    getSelectionIDX() {
        const resultID = (this.resultIndex != null) ? this.resultItems[this.resultIndex]?.idx : null;
        return (this.hoveredCardIDX != null) ? this.hoveredCardIDX : resultID;
    }

    /**
     * Returns a string representing the current view mode ("list" or "grid")
     */
    getViewMode() {
        return this.viewModeForced || this.viewModeSelected;
    }

    setVisibility(visible) {
        if( visible ) {
            this.show(); // this.element.style.display = 'flex';
            this.searchInputEl.focus();
        } else {
            this.element.style.display = 'none';
        }
    }

    /**
     * Closes the dialog.
     */
    close() {
        this.onClose();
        super.close();
    }

    /**
     * Updates the selected element and displays its details in the dialog.
     * @param {boolean|Object} shouldScroll - If true, scrolls to the selected element. Defaults to false.
     *                                        Can also be an object containing the scrollIntoView options.
     * @param {boolean}        force        - If true, updates the selection even if no change occurred. Defaults to false.
     */
    updateSelection(shouldScroll=false, force=false) {
        const newSelectionIDX = this.getSelectionIDX();
        const detailsID       = newSelectionIDX != null ? newSelectionIDX : this.initialCardIDX;
        if( !force && newSelectionIDX === this.oldSelectionIDX ) { return; }

        // deactivate the card with the old element
        const oldCardEl = this.oldSelectionIDX != null ? this.element.querySelector(`#zipn-element-${this.oldSelectionIDX}`) : null;
        if( oldCardEl ) { oldCardEl.classList.remove('active'); }

        this.oldSelectionIDX = newSelectionIDX;

        // activate the card with the new element and optionally scroll to it
        const newCardEl = newSelectionIDX != null ? this.element.querySelector(`#zipn-element-${newSelectionIDX}`) : null;
        if( newCardEl ) { newCardEl.classList.add('active'); }
        if( newCardEl && shouldScroll ) {
            let options = typeof shouldScroll === "object" ? shouldScroll : { behavior: 'smooth', block: 'nearest' };
            newCardEl.scrollIntoView(options);
        }
        // re-render details pane
        _GalleryDialog.renderDetails(this.detailsPaneEL, detailsID, this.groupsByIDX || this.itemsByIDX, this.delegate, this.options);
    }

    /**
     * Updates the search filters and visualization modes based on a command.
     *
     * This method processes a given command to modify the current view mode
     * or category/text filters, then updates the displayed styles in the
     * gallery according to these changes.
     *
     * @param {string} command - A string representing the update operation,
     *   starting with:
     *     '$' followed by 'grid' or 'list' to switch view modes
     *     '@' followed by a category name to filter by category (empty string for no filtering)
     *     '>' followed by a text to filter styles by name (empty string for no filtering)
     */
    updateSearchResults(command) {
        let shouldScroll = false;

        // if the command starts with "$", change the selected view mode
        if( command.startsWith('$') ) {
            const viewMode = command.substring(1);
            if( viewMode == this.viewModeSelected ) { return; }
            this.viewModeSelected = viewMode;
            this.updateToolbar();
            shouldScroll = { behavior: 'instant', block: 'center' };
        }

        // if the command starts with "@", change the category filter
        else if( command.startsWith('@') ) {
            const categoryFilter = command.substring(1);
            if( categoryFilter == this.categoryFilter ) { return; }
            this.categoryFilter = categoryFilter;
            this.updateToolbar();
            this.resultIndex = null;
        }

        // if the command starts with ">", change the text filter
        else if( command.startsWith(">") ) {
            const textFilter = command.substring(1);
            if( textFilter == this.textFilter ) { return; }
            this.textFilter = textFilter;
            if( this.textFilter  ) { this.resultIndex = 0;    }
            else                   { this.resultIndex = null; }
        }

        // calculate the number of columns in the search-result (used for keyboard control)
        this.resultColumns = (this.getViewMode()=="grid" ? 4 : 1);

        // apply filters and re-render gallery
        this.resultItems = _GalleryDialog.filterItems( this.textFilter, this.categoryFilter, this.searchNameIndex );
        _GalleryDialog.renderResults( this.searchResultsEl, this.getViewMode(), this.resultItems, this.options, this.delegate, this.initialCardIDX);

        // disable focus if there are no results
        if( this.resultItems.length == 0 ) { this.resultIndex = null; }

        // update the visual aspect of the card shown as active
        this.updateSelection(shouldScroll,true);
    }

    /**
     * Renders the gallery grid with the provided items.
     *
     * This static method generates HTML content for displaying a list or grid
     * of items based on the specified view mode. Each item is represented as
     * an object in the `items` array and includes properties such as: 'idx',
     * 'name', 'category', etc...
     *
     * @param {HTMLElement}           containerEl   - The container element where the gallery will be rendered.
     * @param {string}                viewMode      - The current view mode ('grid' or 'list') that determines
     *                                                 the layout of each item in the gallery. This parameter
     *                                                 is used to apply appropriate CSS classes.
     * @param {Array<Object>}         items         - An array of objects representing the items to display.
     * @param {GalleryDialogDelegate} delegate      - The object responsible for rendering each item.
     * @param {string|null}           initialItemID - The ID of the initially selected item, which will receive
     *                                                 an additional CSS class ('initial') for highlighting.
     * @example
     * const items = [
     *   { idx: 0, name: 'Modern Look', thumbnail: '/images/modern.jpg' },
     *   { idx: 1, name: 'Retro Feel' , thumbnail: '/images/retro.jpg' }
     * ];
     * renderResults(document.getElementById('gallery-container'), 'grid', items, this.options, delegate, 0);
     */
    static renderResults(containerEl, viewMode, items, dialogOptions, delegate, initialItemID = null) {
        const baseClass   = `zipn-${viewMode}`;
        containerEl.className = baseClass;

        containerEl.innerHTML = items.map( itemOrGroup => {
            const idx  = itemOrGroup.idx;
            const name = itemOrGroup.displayName || itemOrGroup.name;
            const item = itemOrGroup.variants ? itemOrGroup.variants[0] : itemOrGroup;
            const extraClass = item.idx === initialItemID ? ' initial' : '';
            const thumbnailHTML = delegate.htmlItemImage(item, name, dialogOptions, `zipn-thumb`);
            return `
                <div class="${baseClass}-card${extraClass}" id="zipn-element-${idx}" data-id="${idx}">
                    ${thumbnailHTML}
                    <p class="zipn-text">${name}</p>
                </div>`;

        }).join('');
    }

    static renderDetails(detailsPaneEl, itemID, itemsByID, delegate, dialogOptions) {
        if( itemID == null ) {
            detailsPaneEl.innerHTML = delegate.htmlItemDetailsPane(null, "", dialogOptions);
            return;
        }
        const itemOrGroup = itemsByID[ itemID ];
        const name        = itemOrGroup.displayName || itemOrGroup.name;
        const item        = itemOrGroup.variants ? itemOrGroup.variants[0] : itemOrGroup;
        detailsPaneEl.innerHTML = delegate.htmlItemDetailsPane(item, name, dialogOptions);
    }

    /**
     * Filters items based on a search query and a category.
     * @param {string} query          - The search string provided by the user.
     * @param {string} categoryFilter - The category to filter by, or empty string for no filter.
     * @param {Array<[string, object]>} searchNameIndex - Array of tuples containing search string and their corresponding item.
     * @returns {Array<object>}
     *     A list of items matching both the query terms and the category.
     */
    static filterItems(query, categoryFilter, searchNameIndex) {
        const queryParts  = query ? _toSearchString(query).split(/\s+/).filter(Boolean) : [];
        const searchWords = queryParts.filter(part => !part.startsWith('#'));
        const searchTags  = queryParts.filter(part => part.startsWith('#'));
        return searchNameIndex
            .filter(([itemName, item]) => {
                if( categoryFilter && item.category !== categoryFilter ) {
                    return false;
                }
                if( searchTags.length === 0 ) {
                    return searchWords.every(word => itemName.includes(word));
                }
                const matchesAllWords = searchWords.every(word => itemName.includes(word));
                const matchesAnyTag   = item.tags && searchTags.some(searchTag => item.tags.includes(searchTag));
                return matchesAllWords && matchesAnyTag;
            })
            .map(([, item]) => item);
    }


    //-- EVENTS -----------------------------------------------------------

    /**
     * Called when the dialog is launched or re-opened.
     * Configures the dialog according to options, initializes variables, and loads items from the server.
     * @param {Object}   options         - Optional configuration object for the gallery dialog;
     *                                     [view GalleryDialog.launch(...) for more info]
     * @param {string}   initialItemName - Name of the item to show selected when dialog opens
     * @param {Function} onSelect        - Callback function to execute when an item is selected
     */
    onLaunch(options, initialItemName, onSelect) {
        const dialogContentEl      = this.element?.querySelector(`.${DIALOG_CONTENT_CLASS}`);
        const dialogTitleEl        = this.element?.querySelector(`.${DIALOG_TITLE_CLASS}`);
        const dialogIconHolder     = this.element?.querySelector(`.${DIALOG_ICON_HOLDER_CLASS}`);
        const viewModeButtonHolder = this.element?.querySelector(`.${VIEWMODE_BTTN_HOLDER_CLASS}`);

        // store the item selection callback and the configuration options
        this.onSelectItem = onSelect;
        this.options = {
            title          : DEFAULT_TITLE,
            icon           : DEFAULT_TITLE_ICON,
            size           : "default",
            view_mode      : "default",
            allow_variants : false,
            cache_buster   : DEFAULT_CACHE_BUSTER,
            ...options
        };

        // create/remove `this.subDialog` de acuerdo a si el usuario requirio `allow_variants`
        if( !this.options.allow_variants ) {
            this.subDialog = null;
        }
        else if( !this.subDialog ) {
            const subDialogDelegate = new _VariantsSubDialogDelegate( this.delegate );
            this.subDialog = new GalleryDialog(subDialogDelegate);
        }

        // update dialog title [options.title]
        if( dialogTitleEl ) { dialogTitleEl.textContent = this.options.title; }

        // update dialog icon [options.icon]
        const iconEl = html(`i.${this.options.icon}`, {style:{"font-size":"1.25rem", "margin-right":".5rem"}});
        dialogIconHolder?.replaceChildren( iconEl );

        // handle view-mode forced configuration [options.view_mode]
        // if a forced view-mode is set, remove view mode buttons
        if( this.options.view_mode==="list" || this.options.view_mode==="grid" ) {
            this.viewModeForced = this.options.view_mode;
            this.resultColumns  = (this.getViewMode()=="grid" ? 4 : 1);
            this.gridButtonEl   = null;
            this.listButtonEl   = null;
            viewModeButtonHolder?.replaceChildren();
        } else {
            this.viewModeForced = "";
            this.resultColumns  = (this.getViewMode()=="grid" ? 4 : 1);
            this.gridButtonEl   = this.createToolButton("zipn-grid-btn", 'pi pi-image', "", "Grid View", () => { this.updateSearchResults("$grid"); });
            this.listButtonEl   = this.createToolButton("zipn-list-btn", 'pi pi-list' , "", "List View", () => { this.updateSearchResults("$list"); });
            const viewModeButtonHolder = this.element?.querySelector(`.${VIEWMODE_BTTN_HOLDER_CLASS}`);
            viewModeButtonHolder?.replaceChildren(_GalleryDialog.DIVIDER, this.gridButtonEl, this.listButtonEl );
        }

        // handle dialog size configuration [options.size]
        dialogContentEl.classList.toggle('zipn-dialog--small', this.options.size === 'small');

        // initialize variables as if the dialog had just been created
        this.isOpen              = true;
        this.initialItemName     = initialItemName;
        this.initialCardIDX      = null;
        this.resultItems         = [];
        this.resultIndex         = null;
        this.hoveredCardIDX      = null;
        this.oldSelectionIDX     = null;
        this.textFilter          = '';
        this.categoryFilter      = "";
        this.isPointerLocked     = false;
        this.searchInputEl.value = '';
        // `this.viewMode` is not set here because it persists between dialog reopenings

        // load style data from server and focus on the initial style
        this.delegate.fetchItemArray().then( items =>
        {
            // process the received data
            this.onReceiveItems(items);

            // if the initial card is in the list of results,
            // focus on that initial card !
            const initialCardIndex = this.findResultIndexFromIDX(this.initialCardIDX);
            if( initialCardIndex >= 0 ) {
                this.resultIndex = initialCardIndex;
                this.updateSelection();
                requestAnimationFrame( () => {
                //requestAnimationFrame( () => {
                    const focusedCardID = this.resultIndex != null ? this.resultItems[this.resultIndex]?.idx : null;
                    const focusedCardEl = this.elementFromCardID(focusedCardID);
                    if( focusedCardEl ) { focusedCardEl.scrollIntoView({ block: 'start' }); }
                //});
                });
            }
        });

        this.show();
        this.updateToolbar();
        this.searchInputEl.focus();

        // trigger enter animation
        //requestAnimationFrame(() => { this.element.classList.add('fade-in'); });
    }

    onCancel() {
        this.onSelectItem?.(this.initialItemName, true);
        this.close();
    }

   /**
    * Called when the user selects an item of the main list.
    *
    * This function invokes the `onSelectItem(..)` callback with the name of
    * the selected item. If the item contains variants, it opens a sub-dialog
    * to allow the user to select a specific variant before finalizing.
    */
    onItemChosen() {
        const selectionIDX = this.getSelectionIDX();
        const itemsByIDX   = this.groupsByIDX || this.itemsByIDX;

        // attempt to retrieve the currently selected item;
        // exit if no selection exists // if the item has a single variant, select that variant
        let item = selectionIDX != null ? itemsByIDX[selectionIDX] : null;
        if( item == null ) { return; }
        if( item.variants && item.variants.length == 1 ) { item = item.variants[0];  }

        // handle the final process based on variants and sub-dialog presence.
        if( item.variants && this.subDialog ) {
            // item has variants and sub-dialog exists -> launch sub-dialog to select a variant
            this.subDialog.delegate.variants = item.variants;
            this.setVisibility(false);
            this.subDialog.launch({title: item.name, size:"small", view_mode:"list"}, item.variants[0].name, (selectedName, canceled) => {
                if( canceled ) { this.setVisibility(true); return; }
                this.onSelectItem?.(selectedName);
                this.close();
            });
        }
        else if( item.variants && !this.subDialog ) {
            // item has variants but no sub-dialog -> fallback to selecting the first variant
            this.onSelectItem?.(item.variants[0].name);
            this.close();
        }
        else {
            // item has no variants -> select the item directly.
            this.onSelectItem?.(item.name);
            this.close();
        }
    }

    /**
     * Called when the dialog is closed. Updates the open state flag.
     */
    onClose() {
        this.isOpen = false;
    }


    /**
     * Called when item data is received from the server.
     * Initializes internal arrays and maps with the received data.
     * @param {Array} items - An array of items received from the server.
     */
    onReceiveItems(items) {

        if( this.options?.allow_variants ) {
            this.itemsByIDX  = items;
            this.groupsByIDX = _groupItemsByGroupName( items );

            this.searchNameIndex = this.groupsByIDX.map(item => {
                return [ _toSearchString(item.name), item ];
            });

        }
        else {
            this.itemsByIDX = items;
            this.groupsByIDX = null;

            // build the search index used by the search bar
            this.searchNameIndex = items.map(item => {
                return [ _toSearchString(item.name), item ];
            });

            // find initial card ID based on initial element name
            const initialItemName    = _toSearchString(this.initialItemName);
            const initialNameAndItem = this.searchNameIndex.find( ([itemName, ]) => itemName === initialItemName );
            this.initialCardIDX = initialNameAndItem ? initialNameAndItem[1].idx : null;
        }

        // new items loaded, refresh the search results!
        this.updateSearchResults("!refresh");
        this.updateSelection();
    }


    /**
     * Called when the search input loses focus.
     * Try to keep the search input focused always.
     */
    onInputLostFocus() {
        if( !this.isOpen ) { return; }
        setTimeout(() => { if (this.isOpen) this.searchInputEl.focus(); }, 0);
    }


    /**
     * Called when the text in the search input changes.
     * Updates the search results and the active item, locking the pointer
     * movement events temporarily to prevent they interfering with the
     * search result autoselection.
     * @param {HTMLInputElement} inputEl - The search input element.
     * @param {boolean} isEnterPressed   - Indicates whether the Enter key was pressed.
     */
    onInputChange(inputEl, isEnterPressed = false) {

        // temporarily lock pointer movement events
        this.lockPointer();

        // debounce the search results update
        clearTimeout(this.inputChangeTimer2);
        this.inputChangeTimer2 = setTimeout(() =>
        {
            // always update the search results first so that when user
            // presses enter it will accept the most updated result
            this.updateSearchResults(`>${inputEl.value}`);
            if( isEnterPressed ) {
                this.onItemChosen();
            }
            this.hoveredCardIDX = null;
            this.updateSelection();

        }, isEnterPressed ? 100 : 300);

    }


    /**
     * Called when a key is pressed in the search input.
     * @param {string} key - The key that was pressed.
     * @return {boolean}
     *   True if the key if handled by the method and should not be processed by the input field.
     */
    onInputKeyDown(key) {
        let resultIndex = this.resultIndex;

        if     ( key === 'Escape' ) { this.onCancel(); return; }
        else if( key === 'Enter'  ) { this.onInputChange(this.searchInputEl, true); }
        else if( this.resultIndex != null || this.hoveredCardIDX != null )
        {
            // if the current selection is determined by the mouse pointer,
            // capture that selection!
            if( resultIndex == null ) {
                resultIndex = this.findResultIndexFromIDX(this.hoveredCardIDX);
                if( resultIndex<0 ) { resultIndex=0; }
            }

            // cursor key movement
            const oldResultIndex = this.resultIndex;
            if     ( key === 'ArrowUp'    ) { resultIndex-=this.resultColumns; }
            else if( key === 'ArrowDown'  ) { resultIndex+=this.resultColumns; }
            else if( key === 'ArrowLeft'  ) { resultIndex--; }
            else if( key === 'ArrowRight' ) { resultIndex++; }
            if( resultIndex >= this.resultItems.length ) { resultIndex = oldResultIndex; }
            if( resultIndex <  0                       ) { resultIndex = oldResultIndex; }

        }
        // if there is no selection (e.g. just opened the dialog) and user presses down,
        // first search result gets selected
        else if( this.resultIndex == null && key === 'ArrowDown' ) {
            if( this.resultItems ) { resultIndex = 0; }
        }

        // if the selected search result index is modified, update its on-screen representation
        if( this.resultIndex !== resultIndex ) {
            this.resultIndex   = resultIndex;
            this.hoveredCardIDX = null;
            this.lockPointer();
            this.updateSelection(true);
        }
        return ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(key);
    }


    /**
     * Called when the mouse enters a card.
     * @param {HTMLElement} cardEl - The card element that was entered.
     */
    onCardEnter(cardEl) {
        if( this.isPointerLocked ) { return; }
        // updates the currently pointed card ID and triggers selection updates
        this.hoveredCardIDX = Number(cardEl.dataset?.id);
        this.updateSelection();
    }

    /**
     * Called when a card is clicked.
     * @param {HTMLElement} cardEl - The card element that was clicked.
     */
    onCardClick(cardEl) {
        // sets the currently pointed card ID and triggers user selection handling
        this.hoveredCardIDX = Number(cardEl?.dataset?.id);
        this.onItemChosen();
    }

    /**
     * Called when the mouse leaves the card container.
     * This function is responsible for resetting the currently pointed card ID
     * when the user moves the mouse out of the area containing the cards.
     */
    onCardContainerLeave() {
        if( this.isPointerLocked ) { return; }
        this.hoveredCardIDX = null;
        this.updateSelection();
    }


    //-- HELPERS ----------------------------------------------------------

    /**
     * Temporarily locks the pointer movement events.
     *
     * This method sets a flag to prevent pointer movement events from being
     * processed, the flag is reset after a short delay (800 milliseconds).
     */
    lockPointer() {
        this.isPointerLocked = true;
        clearTimeout(this.pointerLockedTimer);
        this.pointerLockedTimer = setTimeout(() => { this.isPointerLocked = false; }, 800);
    }

    /**
     * Finds the index of a card/item in the `resultElements[]` array based on its IDX.
     * @param {number|null} itemIDX - The IDX of the item/card to find.
     * @returns {number} The index of the card with the specified ID, or -1 if not found.
     */
    findResultIndexFromIDX(itemIDX) {
        return itemIDX != null ? this.resultItems.findIndex(card => card.idx == itemIDX) : -1;
    }

    /**
     * Returns the HTML element corresponding to the card with the given ID.
     * @param {number|null} elementID - The ID of the element/card whose corresponding HTML element is sought.
     * @returns {Element|null} The HTML element associated with the given card ID, or null if no match is found.
     */
    elementFromCardID(elementID) {
        return elementID != null ? this.element.querySelector(`#zipn-element-${elementID}`) : null;
    }


    //-- DIALOG COMPONENTS ------------------------------------------------

    /** A spacer element in the toolbar. */
    static get SPACER() { return html("div.zipn-spacer"); }

    /** A divider element (vertical line) in the toolbar. */
    static get DIVIDER() { return html("div.zipn-divider"); }

    /**
     * Creates a button for the toolbar.
     * @param {string}   id      - The unique identifier for the button.
     * @param {string}   icon    - The icon to be used in the button. e.g., "i.pi.pi-image"
     * @param {string}   text    - The text content of the button.
     * @param {string}   tooltip - The title attribute value for the button, representing its tooltip.
     * @param {function} onClick - Function to be executed when the button is clicked.
     * @returns {HTMLElement} A button element with the specified icon, text, tooltip and onclick function.
     */
    createToolButton(id, icon, text, tooltip, onClick) {
        // if no ID is provided, generate a random one
        if( !id ) {
            do { id = 'zipn-btn-' + Math.random().toString(36).slice(2, 9); }
            while( document.getElementById(id) );
        }
        // if the icon ID is provided with spaces between words, convert them to dots
        if( icon ) {
            icon = icon.replace(' ', '.');
        }
        // generate the 3 possible types of buttons:
        //   - button with icon only (no text)
        //   - button with text only
        //   - button with icon and text
        if( icon && !text ) {
            return html( "button.p-button-text", { id: id, title: tooltip, onclick: onClick }, [ html(`i.${icon}`) ] );
        }
        if( !icon && text ) {
            return html( "button.p-button-text", { id: id, title: tooltip, textContent: text, onclick: onClick }, [] );
        }
        return html("button.p-button-text", { id: id, title: tooltip, onclick: onClick }, [
            html(`i.${icon}`, { textContent: text})
        ]);
    }

    /**
     * Creates an input search bar for searching within the gallery dialog.
     * @returns {HTMLElement} An HTML structure representing a search bar.
     */
    createToolbar() {
        const categories = this.delegate.getCategories() || [];

        // create each category button from the `categories` array
        this.categoryButtons = [];
        for (const [category, displayName, description] of categories) {
            const id       = `zipn-${category}-btn`;
            const command  = `@${category}`;
            const buttonEl = this.createToolButton(id, '', displayName, description, () => { this.updateSearchResults(command); });
            this.categoryButtons.push( [category, buttonEl] );
        }

        // add search input
        const toolbarElementList = [];
        toolbarElementList.push(
            html("input", { id: "zipn-search-input", type: "search", placeholder: "Search", autocomplete: "off" } )
        );

        // add category buttons
        if( this.categoryButtons.length > 0 ) {
            toolbarElementList.push(_GalleryDialog.DIVIDER);
            for( const [_, buttonEl] of this.categoryButtons ) {
                toolbarElementList.push( buttonEl );
            }
        }

        // add view-mode buttons holder
        toolbarElementList.push( html(`span.${VIEWMODE_BTTN_HOLDER_CLASS}`) );

        // add viewmode buttons
        if( this.userCanChangeViewMode ) {
            this.gridButtonEl = this.createToolButton("zipn-grid-btn", 'pi pi-image', "", "Grid View", () => { this.updateSearchResults("$grid"); });
            this.listButtonEl = this.createToolButton("zipn-list-btn", 'pi pi-list' , "", "List View", () => { this.updateSearchResults("$list"); });
            toolbarElementList.push(_GalleryDialog.DIVIDER);
            toolbarElementList.push( this.gridButtonEl );
            toolbarElementList.push( this.listButtonEl );
        }

        return html("div", toolbarElementList );
    }

    /**
     * Updates toolbar buttons state based on current view mode and category filter.
     */
    updateToolbar() {
        // update category buttons
        for( const [category, buttonEl] of this.categoryButtons ) {
            buttonEl.classList.toggle('p-highlight', category == this.categoryFilter );
        }
        // update view mode buttons
        const viewMode = this.getViewMode();
        this.listButtonEl?.classList.toggle('p-highlight', viewMode === "list" );
        this.gridButtonEl?.classList.toggle('p-highlight', viewMode === "grid" );
    }


}

//#=========================== HELPER FUNCTIONS ============================#

/**
 * Flag to track if the CSS has been loaded to prevent duplicate injections.
 * @type {boolean}
 */
let _cssLoaded = false;

/**
 * Ensures that the gallery dialog stylesheet is loaded and injected into the document.
 */
function _ensureCSSLoaded() {
    // check if CSS is already loaded to avoid duplicates
    if( _cssLoaded ) { return; }
    try {
        const cssFullPath = import.meta.resolve('./gallery_dialog.css');

        // create a new <link> element and append it to the head of the document
        const link = document.createElement("link");
        link.rel = "stylesheet";
        link.href = cssFullPath;
        document.head.appendChild(link);

        // mark the CSS as loaded
        _cssLoaded = true;
    }
    catch( error ) { console.error("Failed to load GalleryDialog CSS:", error); }
}

/**
 * Creates and returns a custom dialog HTML element for ComfyUI.
 *
 * This implementation utilizes deprecated ComfyUI functions since there is
 * currently no documented method to create custom dialogs. Some ideas and
 * concepts for this implementation were inspired by the ComfYUI-Manager project.
 *
 * @param {string}               titleElClass    - CSS class for the dialog title element.
 * @param {string}               iconHolderClass - CSS class for the icon holder in the dialog header.
 * @param {string|HTMLElement[]} dialogContent   - The content of the dialog, which can be provided
 *                                                 as a string or an array of HTML elements.
 * @param {Function}             onCancel        - Callback function to be executed when the user cancels the dialog.
 * @returns {HTMLElement}
 *    The main DOM element for the created dialog.
 */
function _makeCustomDialog(titleElClass, iconHolderClass, dialogContent, onCancel) {

    const dialogOutsideArea = html("div.p-dialog-mask.p-overlay-mask.p-overlay-mask-enter", {
        parent: document.body,
        style : {
            position      : "fixed",
            height        : "100%",
            width         : "100%",
            left          : "0px",
            top           : "0px",
            display       : "flex",
            justifyContent: "center",
            alignItems    : "center",
            pointerEvents : "auto",
            zIndex        : "1000"
        },
        onclick: (e) => {
            // execute 'onCancel` when click outside of the dialog
            if( e.target === dialogOutsideArea ) { onCancel(); }
        }
    });
    const headerActions = html("div.p-dialog-header-actions");
    const _closeButton  = html("button.zipn-close-button", {
        parent    : headerActions,
        type      : "button",
        ariaLabel : "Close",
        onclick   : onCancel, //< execute `onCancel` when the close button is clicked
        innerHTML : '<i class="pi pi-times"></i>'
    });
    const dialogHeader = html("div.p-dialog-header",
    [
        html("div", [
            html("div", { id: "frame-title-container" }, [
                html("h1", [
                    html( "span."+iconHolderClass  ),
                    html( "span."+titleElClass )
                ])
            ])
        ]),
        headerActions
    ]);
    const contentFrame = html("div.p-dialog-content", {}, _normalizeDOMnodes(dialogContent));
    const dialogFrame  = html("div.p-dialog.p-component.global-dialog", {
            //id    : dialogId,
            parent: dialogOutsideArea,
            style : {
                'display'       : 'flex',
                'flex-direction': 'column',
                'pointer-events': 'auto',
                'margin'        : '0px',
            },
            role     : 'dialog',
            ariaModal: 'true',
        },
        [ dialogHeader, contentFrame ]
    );
    const _hiddenAccessible = html("span.p-hidden-accessible.p-hidden-focusable", {
        parent    : dialogFrame,
        tabindex  : "0",
        role      : "presentation",
        ariaHidden: "true",
        "data-p-hidden-accessible": "true",
        "data-p-hidden-focusable" : "true",
        "data-pc-section"         : "firstfocusableelement"
    });
    return dialogOutsideArea;
}


/**
 * Sets up hover and click event listeners for cards within a container.
 *
 * This function is particularly useful for managing gallery images or item
 * listings where interactive behavior such as highlighting on hover and
 * triggering actions on click are required.
 *
 * @param {HTMLElement} containerEl  - The container element where the cards reside.
 * @param {string}      cardSelector - A CSS selector used to identify card elements.
 * @param {(card: HTMLElement) => void} onCardEnter - Callback function when hovering over a card.
 * @param {(card: HTMLElement) => void} onCardLeave - Callback function when moving the mouse away from a card.
 * @param {(card: HTMLElement) => void} onCardClick - Callback function when clicking on a card.
 * @param {(container: HTMLElement) => void} [onContainerLeave] - Optional callback function when moving the mouse away from the container.
 */
function _setupCardHoverListeners(containerEl, cardSelector, onCardEnter, onCardLeave, onCardClick, onContainerLeave) {

    const hasPointer = true; //!!window.PointerEvent;
    const events = {
        over : hasPointer ? 'pointerover'  : 'mouseover',
        out  : hasPointer ? 'pointerout'   : 'mouseout',
        leave: hasPointer ? 'pointerleave' : 'mouseleave'
    };

    // ensure parameters are of the correct type
    if (!(containerEl instanceof HTMLElement)) {
        throw new TypeError('`containerEl` must be an instance of `HTMLElement`.');
    }

    containerEl.addEventListener(events.over, (e) => {
        const card = e.target.closest(cardSelector);
        if( card && !card.contains(e.relatedTarget) ) { onCardEnter?.(card, e); }
    });

    containerEl.addEventListener(events.out, (e) => {
        const card = e.target.closest(cardSelector);
        if( card && !card.contains(e.relatedTarget) ) { onCardLeave?.(card, e); }
    });

    containerEl.addEventListener('click', (e) => {
        const card = e.target.closest(cardSelector);
        if( card ) { onCardClick?.(card, e); }
    });

    containerEl.addEventListener(events.leave, (e) => {
        onContainerLeave?.(containerEl, e);
    });
}

/**
 * Normalizes content input into an array of DOM nodes
 * @param {*} content - Content to normalize (string|Node|Node[]|NodeList)
 * @returns {Node[]}
 *    An array of DOM nodes
 */
function _normalizeDOMnodes(content) {
    if( !content ) { return []; }

    if (typeof content === 'string') {
        const template = document.createElement('template');
        template.innerHTML = content.trim();
        return Array.from( template.content.childNodes );
    }
    if (content instanceof Node) {
        return [content];
    }
    if (content instanceof NodeList || Array.isArray(content)) {
        return Array.from(content);
    }
    throw new TypeError(`Content must be a string, Node, NodeList or array. Got: ${typeof content}`);
}


/**
 * Converts any string into a normalized search string.
 * @param {string} text - The string to convert
 * @returns {string} Normalized search string with accents and special characters removed
 * @example
 *     _toSearchString("Café");            // "cafe"
 *     _toSearchString("HÉLLO, Wörld!");   // "hello world"
 *     _toSearchString("Hello-World#123"); // "hello world 123"
 */
function _toSearchString(text) {
    if( typeof text !== 'string' ) return '';
    return text.normalize('NFD').replace(/[\u0300-\u036f]/g, '')  //< removes accents cleanly
               .toLowerCase()                                     //< converts everything to lowercase
               .replace(/[^a-z0-9]+/g, ' ').trim();               //< replaces any non-alphanumeric characters with space
}

/**
 * Parses a string into group-name and variant-name based on the separator "//".
 * @param {string|GalleryDialogItem} textOrItem - A string or an "Item" object.
 * @returns {[string, string]} An array containing [groupName, variantName].
 */
function _extractGroupVariantName(textOrItem) {
    const name = (typeof textOrItem === 'string') ? textOrItem : textOrItem?.name;
    if( !name ) { return ["", ""]; }
    const parts = name.split('//');
    return [parts[0]?.trim() || "", parts[1]?.trim() || ""];
}

/**
 * Groups an array of items/variants based on their group name.
 * @param {Array<GalleryDialogItem>} items - The list of items to be grouped.
 * @returns {Array<Object>}
 *     An array of group objects, each containing the group name and its variants.
 */
function _groupItemsByGroupName(items) {
    if( !Array.isArray(items) ) {
        console.warn('Invalid input: items must be an array.');
        return [];
    }
    const groupsMap = new Map();
    for( const item of items ) {
        const [ groupName, variantName ] = _extractGroupVariantName(item);
        let  group = groupsMap.get(groupName);
        if( !group ) {
            group= { idx: groupsMap.size, name: groupName, category: item.category, variants: [] };
            groupsMap.set(groupName, group);
        }
        // create a copy of the item and inject the new idx value and display name
        const variantItem = { ...item, idx: group.variants.length, displayName: variantName || DEFAULT_VARIANT_NAME };
        group.variants.push(variantItem);
    }
    return Array.from(groupsMap.values());
}

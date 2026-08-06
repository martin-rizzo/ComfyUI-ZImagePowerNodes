/**
 * File    : ui_styles.js
 * Purpose : Implements Dialog, Widget, and DataProvider for visual styles,
 *           ensuring compatibility with previous Power Nodes versions.
 *
 * Author  : Martin Rizzo | <martinrizzo@gmail.com>
 * Date    : May 21, 2026
 * Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
 * License : MIT
 *- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
 *                        ComfyUI-ZImagePowerNodes
 *       ComfyUI nodes designed specifically for the "Z-Image" model.
 *_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
 */
export {
    fetchVisualStyleArray,
    requireVisualStyleGalleryDialog,
    addVisualStyleGalleryWidget,
};
import { api } from "../../../scripts/api.js";
import { GalleryDialog, GalleryDialogDelegate } from "./gallery_dialog.js";
import { GalleryWidget, GalleryWidgetDelegate } from "./gallery_widget.js";

// Cache of promises to avoid duplicate requests for the same endpoint.
const _fetchesByEndpoint = new Map();

// Registry of dialogs for each visual-style database endpoint.
const _dialogsByEndpoint = new Map();


//#==========================================================================#
//#                           FETCH VISUAL STYLES                            #
//# The FIRST generation of UI fetched items directly using this function    #
//# and loaded them into a native ComfyUI combobox. Currently, this function #
//# is internally invoked from GALLERY DIALOG and the GALLERY WIDGET.        #

/**
 * Fetches an array with data about each visual style from the server.
 *
 * Note: The implementation looks a bit complex because of the caching system.
 * It uses an immediately-invoked function (IIFE) to cache the ongoing promise
 * right away, ensuring we don't trigger duplicate network requests for the
 * same endpoint URL.
 *
 * @param {string} endpoint - The full endpoint URL to fetch the styles from.
 * @returns {Promise<Array<Object>>}
 *     Resolves to the array of formatted styles.
 *     Each element in the array is an object with the following properties:
 *       - idx        : Unique identifier for the style (the index in the list)
 *       - name       : The name of the style (string)
 *       - category   : The category of the style (string)
 *       - description: Description of the style (string)
 *       - tags       : An string of comma-separated tags associated with the style (string)
 *       - slug       : url-friendly slug (used for building thumbnail filenames)
 *
 * @example
 *   // Using async/await
 *   const styles = await fetchVisualStyleArray('/zi_power/styles/by_version?v=1.0');
 *   console.log(`Loaded ${styles.length} styles.`);
 * @example
 *   // Using promises (.then)
 *   fetchVisualStyleArray('/zi_power/styles/by_version?v=1.0').then(styles => {
 *       console.log(`Loaded ${styles.length} styles.`);
 *   });
 */
async function fetchVisualStyleArray(endpoint)
{
    if( typeof endpoint !== 'string' || !endpoint.trim() ) {
        console.error(`Invalid endpoint parameter: "${endpoint}". Expected a non-empty string.`);
        return [];
    }

    // if the endpoint already exists in the "fetch cache"
    // (either the ongoing promise or resolved result),
    // RETURN IT!
    if( _fetchesByEndpoint.has(endpoint) ) {
        return _fetchesByEndpoint.get(endpoint);
    }

    // encapsulate the fetch process in a promise
    const fetchPromise = (async () => {
        try {
            // fetch the styles from the given endpoint
            const response = await api.fetchApi(endpoint);
            if( !response.ok ) { throw new Error(`HTTP ${response.status}`); }

            // validate that the response is an actual array
            const styles = await response.json();
            if( !Array.isArray(styles) ) { throw new Error(`Expected an array but received ${typeof palettes}`); }

            return styles.map((style, index) => {
                return {
                    idx        : index,
                    name       : style[0] || "Unknown",
                    category   : style[1] || "Uncategorized",
                    description: style[2] || "",
                    tags       : style[3] || "",
                    slug       : style[4] || style[0] || "" // url-friendly slug (used for thumbnail filenames)
                };
            });

        } catch (error) {
            // if failed, delete the cache for this endpoint to allow future retries
            console.error(`Failed to fetch styles from "${endpoint}": ${error.message}`);
            _fetchesByEndpoint.delete(endpoint);
            return [];
        }
    })();

    // store the promise in cache for future use
    _fetchesByEndpoint.set(endpoint, fetchPromise);
    return fetchPromise;
}


//#=========================================================================#
//#                          STYLE GALLERY DIALOG                           #
//# The SECOND generation of UI added a node button that launched a         #
//# GALLERY DIALOG, which in turn modified a native combo-box in ComfyUI.   #
//#                                                                         #

class StyleDialogDelegate extends GalleryDialogDelegate {

    constructor(endpoint, imagesURLTemplate) {
        super();
        this.endpoint          = endpoint;
        this.imagesURLTemplate = imagesURLTemplate;
    }

    /**
     * Fetches an array with data about each item to be displayed in the gallery.
     * @returns {Promise<Array<Object>>}
     *   A promise that resolves to an array of objects with the following properties:
     *       - idx        : Unique identifier for the item (the index in the list)
     *       - name       : The display name of the item (string)
     *       - category   : The category the item belongs to (string)
     *       - description: A detailed description of the item (string)
     *       - tags       : An string of comma-separated tags associated with the style (string)
     *       - slug       : url-friendly slug (used for building thumbnail filenames)
     */
    async fetchItemArray() {
        return fetchVisualStyleArray(this.endpoint);
    }

    /**
     * Returns an array of category definitions used for filtering the gallery items.
     * @returns {Array<Array<string>>}
     *   An array of category definitions where each item contains:
     *     - category    (string): The value used for matching gallery items (must match the "category" property in items)
     *     - displayName (string): The visible name shown in the UI
     *     - description (string): Tooltip description for screen readers/accessibility
     */
    getCategories() {
        return [
        /*   CATEGORY        DISPLAY_NAME    DESCRIPTION                      */
            [""            , "All"         , "Search all styles"               ],
            ["photo"       , "Photo"       , "Search only photographic styles" ],
            ["illustration", "Illustration", "Search only illustration styles" ],
            ["wild"        , "Wild"        , "Search only wild styles"         ],
            ["custom"      , "Custom"      , "Search only custom styles"       ]
        ];
    }

    /**
     * Renders the main image HTML element for the selected item.
     *
     * This implementation renders a lazy-loaded image using the item's
     * properties and the template stored in `this.imagesURLTemplate`,
     * or returns an empty string if the item is `null` or invalid.
     *
     * @param {Object|null} item      - The data object representing the item, or `null` if no item is selected.
     * @param {string}      value     - The value of the item, as reported to the backend.
     * @param {Object}      options   - An object containing the options with which the dialog was configured.
     * @param {string}      htmlClass - CSS class to be applied to the img tag
     * @returns {string}
     *    The HTML string representing the image element
     *    or an empty string if the item is `null` or invalid.
     */
    htmlItemImage(item, value, options, htmlClass) {
        if( !item?.slug ) { return ""; }
        const data = {
            slug       : item.slug,
            file       : item.slug, //< backend already includes the extension (e.g. "casual_photo.jpg")
            size       : htmlClass.includes('thumb') ? "small" : "big",
            cachebuster: options.cache_buster
        };
        const imageURL = this.imagesURLTemplate.replace(/{(\w+)}/g, (match, key) => data[key] ?? match);
        return `<img class="${htmlClass}" src="${imageURL}" loading="lazy" alt="${value | ""}"/>`;
    }

}

/**
 * Returns a style selection dialog containing the styles loaded from the specified endpoint.
 * @param {string} endpoint          - The full endpoint URL to fetch the styles from.
 * @param {string} imagesURLTemplate - The template for the image URL of each style.
 * @returns {GalleryDialog}
 *   The gallery dialog instance for the specified endpoint
 * @example
 *   const styleDialog  = requireVisualStyleGalleryDialog("/api/styles/v1/list", "/api/styles/thumbs/{file}?size={size}");
 *   const currentStyle = "Anime";
 *   styleDialog.launch( {}, currentStyle, (selectedStyle) => {
 *       console.log("Selected Style: " + selectedStyle);
 *   });
 */
function requireVisualStyleGalleryDialog(endpoint, imagesURLTemplate) {

    // check if a dialog is already registered for the specified endpoint
    const dialog = _dialogsByEndpoint.get(endpoint);
    if( dialog ) { return dialog; }

    // If no dialog exists for this endpoint, create a new one
    const newDelegate = new StyleDialogDelegate(endpoint, imagesURLTemplate);
    const newDialog   = new GalleryDialog(newDelegate);
    _dialogsByEndpoint.set(endpoint, newDialog);
    return newDialog;
}


//#=========================================================================#
//#                          STYLE GALLERY WIDGET                           #
//#   The THIRD generation of UI uses a "GALLERY WIDGET" to launch a        #
//#   "GALLERY DIALOG", both of them customized by 'delegate' objects.      #
//#                                                                         #

class StyleWidgetDelegate extends GalleryWidgetDelegate {

    constructor(endpoint, imagesURLTemplate) {
        super();
        this.endpoint = endpoint;
        this.imagesURLTemplate = imagesURLTemplate;
    }

    async fetchItemArray() {
        return fetchVisualStyleArray(this.endpoint);
    }

    getItemText(item, value, options) {
        if( !item ) { return "Undefined"; }
        if( options.allow_variants ) {
            const parts = item.name.split("//");
            const name      = parts[0]?.trim() || "";
            const variation = parts[1]?.trim() || "";
            return `${name}\n${variation}`;
        }
        return item.name;
    }

    /**
     * Draws the image/thumbnail for a specific item.
     *
     * @param {CanvasRenderingContext2D} ctx - The canvas 2D rendering context
     * @param {Object}   rect    - The rectangle object defining the drawing area (left, top, width, height)
     * @param {Object}   item    - The data of the item to be drawn
     * @param {string}   value   - The current value of the widget as reported to the backend
     * @param {Object}   options - An object containing the options with which the widget was configured
     * @param {Function} requestImage - A function to request an image from a URL
     * @returns {number}
     *     The width (in pixels) occupied by the thumbnail, representing the
     *     space used on the right side of the drawing area.
     */
    drawItemThumbnail(ctx, rect, item, value, options, requestImage) {
        if( !item?.slug ) { return 0; }

        const data       = {
            slug       : item.slug,
            file       : item.slug, //< backend already includes the extension (e.g. "casual_photo.jpg")
            size       : "small",
            cachebuster: options.cache_buster
        };
        const thumbSize  = 32;
        const rect_right = rect.left + rect.width;
        const imageURL   = this.imagesURLTemplate.replace(/{(\w+)}/g, (match, key) => data[key] ?? match);
        const image      = requestImage(imageURL);

        // if the image is fully loaded, draw it!!
        if( image.complete && image.naturalWidth > 0 ) {
            const x = rect_right - thumbSize;
            const y = rect.top + (rect.height - thumbSize) / 2;
            ctx.drawImage(image, x, y, thumbSize, thumbSize);
        }
        // draw a temporary placeholder (e.g., a subtle gray square)
        // while the image is being downloaded in the background
        else {
            ctx.fillStyle = "#2a2a2a";
            const x = rect_right - thumbSize;
            const y = rect.top + (rect.height - thumbSize) / 2;
            ctx.fillRect(x, y, thumbSize, thumbSize);
        }
        return thumbSize;
    }
}


function addVisualStyleGalleryWidget(node, name, data) {
    const type          = data[0];
    const options       = data[1] || {};
    const endpoint      = options.endpoint   || "";
    const imagesURL     = options.images_url || "";
    const dialogOptions = options.dialog || {};
    const widgetDelegate = new StyleWidgetDelegate(endpoint, imagesURL);
    let widget = new GalleryWidget(type, node, name, options, widgetDelegate, (widget) =>
    {
        // launch dialog and update widget value
        const styleDialog  = requireVisualStyleGalleryDialog(endpoint, imagesURL);
        const currentStyle = widget.value;
        styleDialog.launch( dialogOptions, currentStyle, (selectedStyle) => {
            widget.forceUpdate( selectedStyle );
        });
    });
    widget = node.addCustomWidget( widget );
    return { widget: widget };
}


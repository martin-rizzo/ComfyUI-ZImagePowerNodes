/**
 * File    : gallery_widget.js
 * Purpose : A generic, customizable ComfyUI node widget for selecting
 *           items featuring thumbnail previews.
 * Author  : Martin Rizzo | <martinrizzo@gmail.com>
 * Date    : May 18, 2026
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
export { GalleryWidget, GalleryWidgetDelegate };
import { LiteGraph, isNodes20, getWidgetBgColor20 } from "../comfyui_bridge.js";
const DEFAULT_CACHE_BUSTER = Math.floor(Date.now() / 3600000);


//#========================= GalleryWidgetDelegate =========================#

/**
 * Base class to implement to customize the gallery widget.
 * This class defines the method for retrieving all items available
 * for selection and the rendering method for each item.
 */
class GalleryWidgetDelegate {

    /**
     * Fetches an array with data about each item that can be selected.
     * Subclasses MUST implement this method to provide item data.
     *
     * @returns {Promise<Array<Object>>}
     *   Resolves to the array of formatted gallery items.
     *   Each item object must contain at least the following properties:
     *       - name : The display name of the item (string)
     *       - any data to be rendered with the widget
     * @example
     * // How to implement in a subclass:
     * class MyWidgetDelegate extends GalleryWidgetDelegate {
     *     async fetchItemArray() {
     *         const data = await myApi.get('/items');
     *         return data.map((item, index) => ({
     *           name       : item.title || "unknown",
     *           description: item.desc,
     *           thumbnail  : item.thumbnail,
     *         }));
     *     }
     * }
     */
    async fetchItemArray() {
        throw new Error("Method 'fetchItemArray()' must be implemented by any GalleryWidgetDelegate subclass");
    }

    /**
     * Gets the displayed description text for the given item.
     * Subclasses MUST implement this method to provide custom description logic.
     *
     * @param {Object} item    - The item data object containing item properties such as name and category
     * @param {string} value   - The current value of the widget, as reported to the backend
     * @param {Object} options - An object containing the options with which the widget was configured
     * @returns {string}
     *     A string representing the item's description, with one or two lines separated
     *     by a newline character ('\n').
     * @example
     *     // Example of subclass implementation:
     *     getItemText(item, value) {
     *         return `${item.name}\n${item.category}`;
     *     }
     */
    getItemText(_item, _value, _options) {
        return "getItemText(..) missing";
    }

    /**
     * Called when a thumbnail needs to be drawn for a specific item.
     * Subclasses MUST implement this method to provide custom thumbnail rendering.
     *
     * The implementation must draw the thumbnail aligned to the RIGHT side
     * of the provided rectangle area.
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
    drawItemThumbnail(ctx, rect, _item, _value, _options, _requestImage) {
        const thumbWidth = 32;
        const rect_right = rect.left + rect.width;
        ctx.fillStyle = '#FF4D4D';
        ctx.fillRect(rect_right-thumbWidth, rect.top, rect.width, rect.height);
        return thumbWidth;
    }

    /**
     * Called when text details need to be drawn for a specific item.
     * This method CAN be overridden to provide custom text rendering.
     *
     * The implementation must draw the text aligned to the RIGHT side of
     * the provided rectangle area. Typically draws 1 or 2 lines of text
     * (line1 + optional line2), this default implementation will draw a
     * single centered line if `line2` is empty.
     *
     * @param {CanvasRenderingContext2D} ctx - The canvas 2D rendering context
     * @param {Object} rect    - The rectangle object defining the drawing area (top, left, width, height)
     * @param {string} line1   - The primary text content to be drawn
     * @param {string} line2   - The optional secondary text content
     * @param {Object} item    - The data of the item to be drawn
     * @param {string} value   - The current value of the widget as reported to the backend
     * @param {Object} options - An object containing the options with which the widget was configured
     * @returns {number}
     *     The width (in pixels) occupied by the widest rendered text element,
     *     which represents the space used by the text on the right side of
     *     the drawing area.
     */
    drawItemText(ctx, rect, line1, line2, _item, _value, _options) {
        const rightEdge   = rect.left + rect.width;
        const top         = rect.top    - 2;
        const height      = rect.height + 4;
        const centerY1    = top  + (height / (line2 ? 3 : 2));
        const centerY2    = top  + (height / 3) * 2;
        ctx.textBaseline = 'middle';
        ctx.textAlign    = 'right';

        // LINE 1: top line in bold
        ctx.font      = `bold ${LiteGraph.NODE_TEXT_SIZE}px ${LiteGraph.NODE_FONT}`;
        ctx.fillStyle = LiteGraph.WIDGET_TEXT_COLOR;
        ctx.fillText(line1, rightEdge, centerY1);
        let width = ctx.measureText(line1).width;

        // LINE 2 (optional): bottom line
        if( line2 ) {
            ctx.font      = `${LiteGraph.NODE_SUBTEXT_SIZE}px ${LiteGraph.NODE_FONT}`;
            ctx.fillStyle = LiteGraph.WIDGET_SECONDARY_TEXT_COLOR;
            ctx.fillText(line2, rightEdge, centerY2);
            const width2 = ctx.measureText(line2).width;
            if( width2 > width ) { width = width2; }
        }
        return width;
    }

    /**
     * Called when the navigation arrows (left/right) need to be drawn.
     * This method is NOT intended to be overridden by subclasses.
     *
     * @param {CanvasRenderingContext2D} ctx - The canvas rendering context used for drawing.
     * @param {Object} rect - The rectangle object containing {left, top, width, height}.
     *                        The method will adjust the properties of this object to define
     *                        the inner area available for subsequent content drawing.
     * @param {number}  padding          - The internal padding to be subtracted from the rectangle dimensions.
     * @param {number}  arrowWidth       - The width allocated for each arrow button area.
     * @param {boolean} enableLeftArrow  - Whether the left arrow should be rendered as enabled.
     * @param {boolean} enableRightArrow - Whether the right arrow should be rendered as enabled.
     * 
     * @example
     * const area = { left: 0, top: 0, width: 100, height: 50 };
     * drawArrows(ctx, area, 5, 20, true, false);
     * // The 'area' object is now updated to represent the inner content space.
     */
    drawArrows(ctx, rect, padding, arrowWidth, enableLeftArrow, enableRightArrow) {
        // prepare for drawing arrows
        ctx.font         = `${LiteGraph.NODE_TEXT_SIZE}px ${LiteGraph.NODE_FONT}`;
        ctx.textAlign    = "center";
        ctx.textBaseline = "middle";
        const centerY    = rect.top + (rect.height / 2);
        const rect_right = rect.left + rect.width;

        // draw left and right arrows
        ctx.fillStyle = enableLeftArrow ? LiteGraph.WIDGET_TEXT_COLOR : LiteGraph.WIDGET_DISABLED_TEXT_COLOR;
        ctx.fillText("◀", rect.left  + (arrowWidth/2), centerY);
        ctx.fillStyle = enableRightArrow ? LiteGraph.WIDGET_TEXT_COLOR : LiteGraph.WIDGET_DISABLED_TEXT_COLOR;
        ctx.fillText("▶", rect_right - (arrowWidth/2), centerY);

        // calculate the inside rect
        rect.left += arrowWidth + padding ;  rect.width  -= 2*arrowWidth + 2*padding;
        rect.top  += padding              ;  rect.height -= 2*padding;
    }
}


//#=========================================================================#
//#//////////////////////// INTERNAL IMPLEMENTATION ////////////////////////#
//#=========================================================================#

/**
 * A generic, customizable ComfyUI widget for selecting items, featuring
 * thumbnail previews and navigation controls.
 */
class GalleryWidget {

    /**
     * Creates a new GalleryWidget instance customized with the given options.
     * @param {string}                type       - The type of the widget. Generally a custom type registered by the user in ComfyUI.
     * @param {string}                name       - Unique identifier for the widget (not used for value serialization)
     * @param {Object}                options    - Configuration options (e.g., styles, height, socketless).
     * @param {GalleryWidgetDelegate} delegate   - Instance responsible for item data and rendering.
     * @param {Function}              [onAction] - Optional callback function executed when the center of the widget is clicked.
     */
    constructor(type, node, name, options, delegate, onAction) {

        /** @type {string} The type of the widget. Generally a custom type registered by the user in ComfyUI */
        this.type = type;

        this.node = node;

        /** @type {string} Unique identifier for the widget (not used for value serialization) */
        this.name = name;

        /** @type {GalleryWidgetDelegate} External object to render the items */
        this.delegate = delegate || new GalleryWidgetDelegate();

        /** @type {number} Index of the currently selected item (-1 = nothing selected) */
        this._selectedIndex = -1;

        /** @type {Array<number>} The horizontal and vertical margins of the widget */
        this.widgetMargin = [14, 1];

        /** @type {number} Width of the left/right arrow buttons */
        this.arrowButtonWidth = 24;

        /** @type {Function|null} Optional function to execute when the user clicks in the center of the widget. */
        this.onAction = onAction || null;

        /** @type {boolean} Flag used by ComfyUI to know if the value must be serialized */
        this.serialize = true;

        this._cachedImageURL = null;
        this._cachedImage    = null;

        /** @type {Object} The configuration options passed to the widget */
        this.options = {
            height        : 48,
            allow_variants: false,
            cache_buster  : DEFAULT_CACHE_BUSTER,
            ...options
        };

        // bind methods to ensure correct 'this' context
        this.draw          = this.draw.bind(this);
        this.onPointerDown = this.onPointerDown.bind(this);
        this.computeSize   = this.computeSize.bind(this);

        // load item data
        this.itemArray = [];
        this.delegate.fetchItemArray().then( itemArray => {
            if( Array.isArray(itemArray) && itemArray.length>0 ) {
                this.itemArray = itemArray;
                if( this.value == null ) { this.value = itemArray[0]?.name || ""; }
                this._selectedIndex = null;
                this.forceUpdate();
            }
        });
    }

   /**
     * Gets the selected item index.
     * Calculates the index based on `this.value` and ???
     * @returns {number} The index of the selected item or -1 if not found, or no data, or nothing selected.
     */
    get selectedIndex() {
        // if the index was invalidated, recalculate it
        if( this._selectedIndex == null ) {
            this._selectedIndex = -1;
            if( this.value && Array.isArray(this.itemArray) ) {
                this._selectedIndex = this.itemArray.findIndex(item => item.name === this.value);
            }
        }
        return this._selectedIndex;
    }

    /**
     * Sets the selected item index and updates `this.value` accordingly.
     * @param {number} index - The index of the selected item.
     */
    set selectedIndex(index) {
        if( !Array.isArray(this.itemArray) || this.itemArray.length===0 ) { return; }

        // clamp the index
        index = Math.max(0, Math.min(index, this.itemArray.length - 1));
        if( index == this._selectedIndex ) { return; }

        // modify the value and index and trigger visual update
        this.forceUpdate( this.itemArray[index].name );
        this._selectedIndex = index;
    }

    /**
     * Force the widget to update its visual representation (with optional new value)
     * @param {string} [newValue] - The new value to set.
     *                              If not provided, the current value is retained.
     */
    forceUpdate(newValue) {
        const oldValue = this.value;
        this.value = newValue || this.value;

        // If the value was actually modified, then the selected index becomes invalid
        if( this.value !== oldValue ) { this._selectedIndex = null; }

        // ComfyUI automatically injects a 'triggerDraw' method into widgets
        // we call it if available, but we also manually trigger a canvas refresh
        // using 'setDirtyCanvas' as a fallback to ensure the widget redraws
        this.node?.setDirtyCanvas(true);
        if( typeof this.triggerDraw === 'function' ) { this.triggerDraw(); }
    }


    //#------------------------------ EVENTS -------------------------------#

    /**
     * Called when the widget is clicked.
     * @param {CanvasPointer} pointerOrEvent - Pointer or event object containing mouse/touch data
     * @param {ComfyNode}     node           - Node object with position data
     * @param {LGraphCanvas}  _canvas        - Canvas object for coordinate calculations
     * @returns {boolean}
     *     Returns true if processing was successful
     */
    onPointerDown(pointerOrEvent, node, _canvas) {
        // this function may be invoked with different parameters;
        // therefore, any calls lacking the required event or node position are discarded
        if( !pointerOrEvent?.eDown || !node?.pos ) { return; }
        const event           = pointerOrEvent.eDown;
        const useLegacyRender = !isNodes20() && !event.target?.closest('[data-testid="properties-panel"]');

        const htmlElement = event.target;
        let   localX      = event.offsetX;
        let   widgetWidth = htmlElement?.offsetWidth || 0;
        if( useLegacyRender ) {
            // legacy coordinate calculation for older versions prior to Nodes 2.0;
            localX      = event.canvasX - (node.pos[0] || 0);
            widgetWidth = node?.size?.[0] || this.width || 256;
        }

        // defer the action execution until the click is completed (button released)
        pointerOrEvent.onClick = () => {
            if( localX < this.widgetMargin[0] + this.arrowButtonWidth ) {
                this.selectedIndex -= 1;
            } else if( localX > widgetWidth - this.widgetMargin[0] - this.arrowButtonWidth ) {
                this.selectedIndex += 1;
            } else if( this.onAction ) {
                this.onAction(this);
            }
        };
        return true;
    };

    /**
     * Called when the widget needs to be drawn.
     * Draws all widget elements: container, navigation arrows, thumbnails, and descriptive text.
     * @param {CanvasRenderingContext2D} ctx - The canvas rendering context.
     * @param {Object} node          - The parent ComfyNode object where the widget is located.
     * @param {number} widgetWidth   - The width allocated to this widget.
     * @param {number} y             - The vertical offset of the widget.
     * @param {number} widgetHeight  - The height allocated to this widget.
     */
    draw(ctx, node, widgetWidth, y, _widgetHeight) {
        const padding         = 4;
        const spacing         = 6;
        const lastIndex       = this.itemArray.length - 1;
        const selectedIndex   = this.selectedIndex;
        const item            = this.itemArray[selectedIndex];
        const useLegacyRender = ctx.canvas?.classList?.contains("lgraphcanvas");

        // apply width correction for legacy ComfyUI versions where `widgetWidth`
        // was inconsistently reported or failed to sync with the node width
        if( useLegacyRender ) {
            const parentWidth   = this.node?.width || 0;
            if( parentWidth && Math.abs(widgetWidth-parentWidth)>2 ) {
                widgetWidth = parentWidth;
                this.width  = widgetWidth;
            }
        }

        ctx.save();

        const rect = {
            left  : 0 + this.widgetMargin[0],
            top   : y + this.widgetMargin[1],
            width : widgetWidth         - 2*this.widgetMargin[0],
            height: this.options.height - 2*this.widgetMargin[1] };

        // hack to differ the widget appearance in Legacy and Nodes 2.0
        let borderLineSize = 0;
        let widgetBgColor  = getWidgetBgColor20();
        if( useLegacyRender ) {
            borderLineSize = 1;
            widgetBgColor  = LiteGraph.WIDGET_BGCOLOR;
        }

        // draw the widget container
        ctx.fillStyle   = widgetBgColor;
        ctx.strokeStyle = LiteGraph.WIDGET_OUTLINE_COLOR;
        ctx.lineWidth   = borderLineSize;
        ctx.beginPath();
        ctx.roundRect(rect.left, rect.top, rect.width, rect.height, rect.height / 4);
        ctx.fill();
        if( borderLineSize>0 ) { ctx.stroke(); }

        // draw the arrows
        const midLineSize = Math.floor(borderLineSize / 2);
        rect.left += midLineSize ; rect.width  -= 2*midLineSize;
        rect.top  += midLineSize ; rect.height -= 2*midLineSize;
        this.delegate.drawArrows(ctx, rect, padding, this.arrowButtonWidth, selectedIndex>0, selectedIndex<lastIndex, this.bgColor20);

        // draw item thumbnail
        const thumbWidth = this.delegate.drawItemThumbnail(ctx, rect, item, this.value, this.options, (url) => this.requestImage(url) );
        if( typeof thumbWidth === 'number' ) {
            rect.width -= (thumbWidth + spacing);
        }

        // get item text (can be one or two lines)
        let itemText = this.delegate.getItemText(item, this.value, this.options);
        if( typeof itemText === 'string' ) itemText = itemText.split('\n');
        const line1 = itemText.length > 0 ? itemText[0] : "";
        const line2 = itemText.length > 1 ? itemText[1] : "";

        // draw item text on the right side
        const textWidth = this.delegate.drawItemText(ctx, rect, line1, line2, item, this.value, this.options);
        if( typeof textWidth === 'number' ) {
            rect.width -= Math.ceil(textWidth);
        }

        // draw this.name text on the left side
        ctx.font         = `${LiteGraph.NODE_SUBTEXT_SIZE}px ${LiteGraph.NODE_FONT}`;
        ctx.fillStyle    = LiteGraph.WIDGET_SECONDARY_TEXT_COLOR; //this.text_color;
        ctx.textAlign    = 'left';
        ctx.textBaseline = 'middle';
        rect.left -= 7;
        this.drawTextWithEllipsis(ctx, rect, this.name);

        ctx.restore();
    }

    /**
     * Called when the widget size needs to be computed.
     * @param {number} widgetWidth - The widget width
     * @returns {Array} The computed size [width, height]
     */
    computeSize(widgetWidth) {
        return [widgetWidth || 0, this.options.height];
    }


    //#------------------------- INTERNAL METHODS --------------------------#

    /**
     * Draws text with ellipsis truncation within the given rectangle
     * @param {CanvasRenderingContext2D} ctx - The canvas context
     * @param {Object} rect - The rectangle bounds for the text
     * @param {string} text - The text to draw
     */
    drawTextWithEllipsis(ctx, rect, text) {
        if( !text || rect.width <= 0 ) { return; }
        const textX          = rect.left;
        const textY          = rect.top + rect.height / 2;
        const availableWidth = rect.width;

        // check if the text fits within the available width without truncation
        if( ctx.measureText(text).width <= availableWidth ) {
            ctx.fillText(text, textX, textY);
            return;
        }

        // if the ellipsis itself doesn't fit, there's no point in drawing anything
        const ellipsis = '...';
        const ellipsisWidth = ctx.measureText(ellipsis).width;
        if( ellipsisWidth >= availableWidth ) {
            return;
        }

        // binary search to find the optimal cutoff point for the text
        let low  = 0;
        let high = text.length;
        let bestLength = 0;
        while( low <= high )
        {
            const mid      = (low + high) >> 1; //< fast integer division
            const testText = text.substring(0, mid) + ellipsis;
            if (ctx.measureText(testText).width <= availableWidth) {
                // this length fits, try for a longer one
                bestLength = mid; 
                low = mid + 1;
            } else {
                // this length doesn't fit, try a shorter one
                high = mid - 1;
            }
        }
        const displayText = text.substring(0, bestLength) + ellipsis;
        ctx.fillText(displayText, textX, textY);
    }

    /**
     * Requests an image URL and caches it for performance optimization.
     * This method is used to efficiently render item thumbnails by reusing
     * the cached image object.
     *
     * @param {string} url - The URL of the image/thumbnail to request.
     * @returns {HTMLImageElement} The cached image object.
     */
    requestImage(url) {
        // if the URL is the same as the cached one, return the cached image immediately
        if( this._cachedImageURL === url ) { return this._cachedImage; }
        this._cachedImageURL = url;

        // reuse the existing Image object or create a new one if it's the first request
        if( !this._cachedImage ) { this._cachedImage = new Image(); }

        // set the onload event handler to trigger an update when the image is loaded
        this._cachedImage.onload = () => {
            if( this._cachedImageURL === url ) { this.forceUpdate(); }
        };
        // start the asynchronous download in the background
        this._cachedImage.src = url;
        return this._cachedImage;
    }

}


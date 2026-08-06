/**
 * File    : common_dialog.js
 * Purpose : Common script for custom dialogs.
 * Author  : Martin Rizzo | <martinrizzo@gmail.com>
 * Date    : Feb 8, 2026
 * Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
 * License : MIT
 *- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
 *                        ComfyUI-ZImagePowerNodes
 *       ComfyUI nodes designed specifically for the "Z-Image" model.
 *_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
*/
import { $el as html } from "../../../scripts/ui.js"; //< deprrecated ?
export {
    makeCustomDialog,
    setupCardHoverListeners
};


/**
 * Normalizes content into an array of DOM nodes.
 *
 * This function processes input content and ensures it's returned as an array
 * of Node elements, regardless of its original type (string, single node, NodeList,
 * or Array). If the input is not one of these types, it returns an empty array
 * to prevent errors in subsequent operations.
 *
 * @param {string|Node|NodeList|Array<Node>} content - The content that needs to be normalized.
 * @returns {Array<Node>}
 *     An array of DOM nodes representing the input content.
 *     If the content is invalid or cannot be converted to nodes, it returns an empty array.
 */
function normalizeDOMnodes(content)
{
    // handle strings (convert html to array of nodes)
    if( typeof content === 'string' ) {
        const template = document.createElement('template');
        template.innerHTML = content.trim();
        return Array.from(template.content.childNodes);
    }
    // handle single nodes (convert to array for consistency)
    if( content instanceof Node ) {
        return [content];
    }
    // handle NodeLists or arrays of nodes
    if( content instanceof NodeList || Array.isArray(content) ) {
        return Array.from(content);
    }
    // return empty array by default to avoid errors
    return [];
}

/**
 * Creates and returns a custom dialog HTML element for ComfyUI.
 *
 * This implementation utilizes deprecated ComfyUI functions since there is
 * currently no documented method to create custom dialogs. Some ideas and
 * concepts for this implementation were inspired by ComfYUI-Manager project.
 *
 * @param {string} dialogId  - The ID for the dialog element.
 * @param {string} titleId   - The ID for the title element within the dialog.
 * @param {string} title     - The title to be displayed in the dialog header.
 * @param {string} iconClass - The CSS class for the icon that will appear next to the title.
 * @param {string|HTMLElement[]} content - The content of the dialog, which can be a string or an array of HTML elements.
 * @param {Function} onClose - A callback function to be executed when the dialog is closed.
 * @returns {HTMLElement} 
 *     Returns the main container element for the dialog mask.
 */
function makeCustomDialog(dialogId, titleId, title, iconClass, content, onClose) {

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
            // execute `onClose` only if click outside of the dialog
            if( e.target === dialogOutsideArea ) { onClose(); }
        }
    });
    const headerActions = html("div.p-dialog-header-actions");
    const _closeButton  = html("button.p-button.p-component.p-button-icon-only.p-button-secondary.p-button-rounded.p-button-text.p-dialog-close-button", {
        parent    : headerActions,
        type      : "button",
        ariaLabel : "Close",
        onclick   : onClose, //< execute `onClose` when close button is clicked
        innerHTML : '<i class="pi pi-times"></i>'
    });
    const dialogHeader = html("div.p-dialog-header", 
    [
        html("div", [
            html("div", { id: "frame-title-container" }, [
                html("h2.px-4", [
                    html(iconClass, {
                        style: { "font-size": "1.25rem", "margin-right": ".5rem" }
                    }),
                    html("span", { id: titleId, textContent: title })
                ])
            ])
        ]),
        headerActions
    ]);
    const contentFrame = html("div.p-dialog-content", {}, normalizeDOMnodes(content));
    const dialogFrame  = html("div.p-dialog.p-component.global-dialog", {
            id    : dialogId,
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
function setupCardHoverListeners(containerEl, cardSelector, onCardEnter, onCardLeave, onCardClick, onContainerLeave) {

    const hasPointer = true; //!!window.PointerEvent;
    const events = {
        over : hasPointer ? 'pointerover'  : 'mouseover',
        out  : hasPointer ? 'pointerout'   : 'mouseout',
        leave: hasPointer ? 'pointerleave' : 'mouseleave'
    };

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


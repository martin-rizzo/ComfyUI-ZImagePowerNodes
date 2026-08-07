/**
 * File    : common/timer.js
 * Purpose : Helper functions to execute periodic low-priority tasks.
 * Author  : Martin Rizzo | <martinrizzo@gmail.com>
 * Date    : Feb 1, 2026
 * Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
 * License : MIT
 *- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
 *                        ComfyUI-ZImagePowerNodes
 *       ComfyUI nodes designed specifically for the "Z-Image" model.
 *_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
*/
export { executeLowPriorityTasks, scheduleIntervalCalls };
export { schedulePeriodicCallback };

//#=============================== NEW TIMER ===============================#

/**
 * Global store to hold references to nodes and their associated periodic callbacks.
 * Using a Map allows for efficient lookup and removal of node-related data.
 * @type {Map<ComfyNode, Set<Function>>}
 */
const nodeCallbacksMap = new Map();

/**
 * Handles the cleanup process when a node is removed from the ComfyUI.
 * It removes all associated callbacks and restores the original node behavior.
 *
 * @param {ComfyNode} node - The node that is being removed.
 */
function _onNodeRemoved(node) {
    if( nodeCallbacksMap.has(node) ) {
        nodeCallbacksMap.delete(node);
    }
}

/**
 * Registers a periodic callback associated with a specific ComfyUI node.
 * El periodic callback dejara de ser llamado automaticamente cuando el
 * nodo suministrado sea removido/eliminado.
 *
 * @param {ComfyNode} node             - The node to which the callback is linked.
 * @param {Function}  callbackFunction - The function to be executed periodically.
 * @example
 * schedulePeriodicCallback(myNode, () => console.log('Tick'));
 */
function schedulePeriodicCallback(node, callbackFunction) {

    // check if this is the first time we are associating a callback with this node
    const isFreshNode = !nodeCallbacksMap.has(node);

    // initialize the set if the node is not in the map
    if( !nodeCallbacksMap.has(node) ) {
        nodeCallbacksMap.set(node, new Set());
    }

    // add the callback to the set
    nodeCallbacksMap.get(node).add(callbackFunction);

    // intercept the `onRemoved` method to trigger the _onNodeRemoved event;
    // (only wrap the original onRemoved function once when the node is fresh)
    if( isFreshNode ) {
        const originalOnRemoved = node.onRemoved;
        node.onRemoved = function() {
            _onNodeRemoved(node);
            if( typeof originalOnRemoved === 'function' ) {
                return originalOnRemoved.apply(this, arguments);
            }
        };
    }
}

/**
 * Executes all registered periodic callbacks across all tracked nodes.
 * Iterates through the map and invokes every function in the sets.
 */
function executePeriodicCallback() {
    for( const [node, callbacks] of nodeCallbacksMap.entries() ) {
        callbacks.forEach((callback) => {
            try { callback(node); }
            catch (error) {
                console.error('Error executing periodic callback:', error);
            }
        });
    }
}


//#=============================== Old Timer ===============================#

let nodes = new Set();


/**
 * Registers a controller to receive periodic interval calls.
 *
 * This function sets up automatic, repeated calls to the specified controller's
 * `onInterval` method. It attempts to use the node associated with the given
 * controller, unless a specific node is provided as an argument.
 *
 * Key features:
 * - Automatically detects the controller's node if no explicit node is supplied.
 * - Ensures that interval calls stop when the associated node is removed from ComfyUI.
 *
 * @param {Object} controller - The controller object, which must have an `onInterval` method.
 * @param {Object} [node]     - An optional node to associate with the interval calls.
 *                              If not provided, the controller's own node will be used.
 */
function scheduleIntervalCalls(controller, node) {
    if( !node ) { node = controller?.node; }
    if( !node ) {
        console.error("No node or controller found to call the onInterval method.");
    }

    // add the node to the set to call the `onInterval()` method
    nodes.add(node);

    // intercept the `onRemoved` method to remove the node from the set
    const originalOnRemoved = node.onRemoved;
    node.onRemoved = function() {
        nodes.delete(this);
        return originalOnRemoved?.apply(this, arguments);
    };
}


/**
 * Executes low-priority tasks for all registered nodes.
 *
 * This function is designed to be called periodically, such as every 5 seconds.
 * It handles lower priority background operations across all registered nodes.
 *
 * Note: The "low priority timer extension" will be responsible for
 *       calling this function.
 */
function executeLowPriorityTasks() {
    // iterate over all registered nodes and call `onInterval()` from the controller
    for( const node of nodes ) {
        node.zzController?.onInterval?.();
    }
    executePeriodicCallback();
}

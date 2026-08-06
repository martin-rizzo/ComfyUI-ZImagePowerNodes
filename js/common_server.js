/**
 * File    : common_server.js
 * Purpose : Common functions for fetching data from the backend.
 * Author  : Martin Rizzo | <martinrizzo@gmail.com>
 * Date    : Feb 9, 2026
 * Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
 * License : MIT
 *- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
 *                        ComfyUI-ZImagePowerNodes
 *       ComfyUI nodes designed specifically for the "Z-Image" model.
 *_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
*/
import { api } from "../../../scripts/api.js";
export {
    fetchLastVersionStyles,
    fetchStyleNamesByCategory09 //< (old) deprecated
};


let _lastVersionStyles = null;

/**
 * Fetches a list of all available styles in the last backend version.
 *
 * This function retrieves the latest style information by making an API call
 * to "/zi_power/styles/last_version". If the data has already been fetched
 * before, it returns the cached result.
 *
 * @param {function(Array<Object>)} onResponse
 *     A callback function that receives an array of style objects.
 *     Each style object contains:
 *       - id         : Unique identifier for the style (the index in the list)
 *       - name       : The name of the style (string)
 *       - lowerName  : The name of the style, converted to lowercase (string)
 *       - category   : The category of the style (string)
 *       - description: Description of the style (string)
 *       - tags       : Array of tags associated with the style (Array<string>)
 *       - thumbnail  : URL for the style's thumbnail image (string)
 *
 * @example
 * fetchLastVersionStyles((styles) => {
 *     styles.forEach(style => console.log(style.name));
 * });
 */
async function fetchLastVersionStyles(onResponse) {
    if( typeof onResponse !== "function" )
    { console.error("The provided argument is not a valid function."); return; }

    // if it has already been queried before, returns the stored result
    if( _lastVersionStyles ) { onResponse( _lastVersionStyles ); return; }

    try {
        const response = await api.fetchApi("/zi_power/styles/last_version");
        const styles   = await response.json();
        if( typeof styles !== "object" )
        { console.error("The fetching of last version style failed."); return; }

        // prefix used when requesting thumbnails
        const thumbnailRequestPrefix = "/zi_power/styles/samples?file=";

        _lastVersionStyles = styles.map((style, index) => {
            return {
                id         : index,
                name       : style[0],
                lowerName  : style[0].toLowerCase(),
                category   : style[1],
                description: style[2],
                tags       : style[3].split(","),
                thumbnail  : thumbnailRequestPrefix + style[4]
            };
        });
        onResponse( _lastVersionStyles );
    } catch (error) {
        console.error("Failed to fetch styles:", error);
    }
}



let _namesByCategory09 = null;

/**
 * Fetches an object containing style names grouped by their categories.
 * @deprecated It's deprecated and maintained for compatibility with old code.
 *
 * @param {function(Object)} onResponse
 *     A callback function that receives an object where each key is a
 *     category name and the value is an array of style names.
 *     NOTE: style names will be quoted in double quotation marks.
 *
 * @example
 * fetchStyleNamesByCategory09((namesByCategory) => {
 *     for(const category in namesByCategory){
 *         console.log(`Styles in ${category}:`);
 *         namesByCategory[category].forEach(name => console.log(name));
 *     }
 * });
 */
async function fetchStyleNamesByCategory09( onResponse) {
    if( typeof onResponse !== "function" )
    { console.error("The provided argument is not a valid function."); return; }

    // if it has already been queried before, returns the stored result
    if( _namesByCategory09 ) { onResponse( _namesByCategory09 ); return; }

    try {
        const response = await api.fetchApi("/zi_power/styles/by_version?version=0.9");
        const styles   = await response.json();
        if( typeof styles !== "object" )
        { console.error("The fetching of last version style failed."); return; }

        let namesByCategory09 = {};
        for( let i=0 ; i<styles.length ; ++i ) {
            const name     = `"${styles[i][0]}"`; //< quoted name
            const category =     styles[i][1];
            if( !namesByCategory09[category] ) { namesByCategory09[category] = []; }
            namesByCategory09[category].push(name);
        }
        _namesByCategory09 = namesByCategory09;

        onResponse( _namesByCategory09 );
    } catch (error) {
        console.error("Failed to fetch styles:", error);
    }
}

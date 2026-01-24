"""
File    : server.py
Purpose : Provides server routes to be used by the nodes of the project.
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jan 22, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

 ComfyUI Server Routes oficial documentation:
 - https://docs.comfy.org/development/comfyui-server/comms_routes

"""
from functools                  import cache
from server                     import PromptServer
from aiohttp                    import web
from .styles.predefined_styles  import PREDEFINED_STYLE_GROUPS
routes = PromptServer.instance.routes


@cache
def _style_names_by_category(quoted: bool | str = False) -> dict[ str, list[str] ]:
    """
    Generates a dictionary mapping categories to all the style names in that category.

    Returns:
        A dictionary where each key is a category and its value is
        a list of style names belonging to that category.
    """
    names_by_category = {}
    for style_group in PREDEFINED_STYLE_GROUPS:
        names = names_by_category.setdefault( style_group.category, [] )
        names.extend( style_group.get_names(quoted=quoted) )

    return names_by_category


@cache
def _style_names_by_category_by_version() -> dict:
    """
    Not implemented yet.
    """
    return {}


#============================== SERVER ROUTES ==============================#

@routes.get("/zi_power/styles/by_category")
async def get_styles_by_category(_):
    """
    Handles GET requests to '/zi_power/styles/by_category'.
    This route returns style names grouped by their respective categories.
    """
    return web.json_response( _style_names_by_category() )

@routes.get("/zi_power/quoted_styles/by_category")
async def get_quoted_styles_by_category(_):
    """
    Handles GET requests to '/zi_power/quoted_styles/by_category'.
    This route returns quoted style names grouped by their respective categories.
    """
    return web.json_response( _style_names_by_category(quoted=True) )



@routes.get("/zi_power/styles/by_version")
async def get_styles_by_version(_):
    """
    Handles GET requests to '/zi_power/styles/by_version'.
    This route returns each historical version,
    where each one contains the styles names in that version grouped by category.
    """
    return web.json_response( _style_names_by_category_by_version() )


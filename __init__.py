"""
File    : __init__.py
Purpose : Register the "Z-Image Power Nodes".
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jan 16, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.

    Copyright (c) 2026 Martin Rizzo

    Permission is hereby granted, free of charge, to any person obtaining
    a copy of this software and associated documentation files (the
    "Software"), to deal in the Software without restriction, including
    without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to
    permit persons to whom the Software is furnished to do so, subject to
    the following conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
    CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
    TORT OR OTHERWISE, ARISING FROM,OUT OF OR IN CONNECTION WITH THE
    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
"""
import os
from comfy_api.latest import ComfyExtension, io
from .nodes.server    import *
__PROJECT_EMOJI = "⚡"                 #< emoji that identifies the project
__PROJECT_MENU  = "Z-Image"            #< name of the menu where all the nodes will be
__PROJECT_ID    = "//ZImagePowerNodes" #< used to identify the project in the ComfyUI node registry.


#================================= LOGGER ==================================#

# initialize the project logger
from comfy.cli_args     import args
from .nodes.core.system import setup_logger
if os.getenv('ZIMAGE_NODES_DEBUG'):
    setup_logger(log_level="DEBUG", emoji=__PROJECT_EMOJI, name="ZI_POWER", use_stdout=args.log_stdout)
else:
    setup_logger(log_level=args.verbose, emoji=__PROJECT_EMOJI, name="ZI_POWER", use_stdout=args.log_stdout)

# import the newly initialized project logger
from .nodes.core.system import logger


#============================ HELPER FUNCTIONS =============================#

def _register_node(node_class, node_subcategory, node_list, deprecated: bool = False):
    """
    Registers a node in the given `node_class_list` with appropriate title based on its category and status.

    After registering all the nodes, the `node_class_list` can be sent to comfy
    in the function `get_node_list(self)` of a ComfyExtension.

    Args:
        node_class       : The class of the node to be registered.
        node_subcategory : The subcategory for the node (used for the menu grouping)
        node_list        : List where the node will be appended after registration.
        deprecated (optional): Indicates whether the node is deprecated. Defaults to False.
    """
    # add a '/' to the beginning of node_subcategory if it doesn't already start with one
    if node_subcategory and not node_subcategory.startswith("/"):
        node_subcategory = "/" + node_subcategory

    class_name     = node_class.__name__
    title          = node_class.xTITLE
    category       = f"{__PROJECT_EMOJI}{__PROJECT_MENU}{node_subcategory}"
    comfy_node_id  = f"{class_name} {__PROJECT_ID}"

    if deprecated:
        title = f"❌{title} [Deprecated]"
    else:
        title = f"{__PROJECT_EMOJI}| {title}"

    node_class.xTITLE         = title
    node_class.xCATEGORY      = category
    node_class.xCOMFY_NODE_ID = comfy_node_id
    node_class.xDEPRECATED    = deprecated
    node_list.append( node_class )


#======================= COMFY EXTENSION (V3 schema) =======================#

class ZImagePowerNodesExtension(ComfyExtension):

    # must be declared as async
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        _PROJECT_MENU= "ZiNodes"
        nodes = []


        #-- ROOT --------------------------------
        subcategory = ""

        from .nodes.empty_zimage_latent_image import EmptyZImageLatentImage
        _register_node( EmptyZImageLatentImage, subcategory, nodes )

        from .nodes.illustration_style_prompt_encoder import IllustrationStylePromptEncoder
        _register_node( IllustrationStylePromptEncoder, subcategory, nodes )

        from .nodes.photo_style_prompt_encoder import PhotoStylePromptEncoder
        _register_node( PhotoStylePromptEncoder, subcategory, nodes )

        from .nodes.save_image import SaveImage
        _register_node( SaveImage, subcategory, nodes )

        from .nodes.style_prompt_encoder import StylePromptEncoder
        _register_node( StylePromptEncoder, subcategory, nodes )

        from .nodes.zsampler_turbo import ZSamplerTurbo, ZSamplerTurboCurve
        _register_node( ZSamplerTurbo, subcategory, nodes )
        _register_node( ZSamplerTurboCurve, subcategory, nodes )


        #--[ __deprecated ]----------------------
        subcategory = "__deprecated"

        # this is where nodes that were deprecated and
        # maintained only for compatibility go

        # from .nodes.example_node import ExampleNode
        # _register_node( ExampleNode, subcategory, nodes, deprecated=True )

        logger.info(f"Imported {len(nodes)} nodes")
        return nodes


async def comfy_entrypoint() -> ZImagePowerNodesExtension:
    return ZImagePowerNodesExtension()


WEB_DIRECTORY = "./web"
__all__ = ["WEB_DIRECTORY"]

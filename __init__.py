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
from comfy_api.latest                import ComfyExtension, io
from .nodes                          import custom_routes
from .nodes.core.helpers             import get_project_version
from .nodes.data.predefined_styles   import PREDEFINED_STYLES
from .nodes.data.predefined_palettes import PREDEFINED_PALETTES
__PROJECT_EMOJI = "⚡"                 #< emoji that identifies the project
__PROJECT_MENU  = "Z-Image"            #< name of the menu where all the nodes will be
__PROJECT_ID    = "//ZImagePowerNodes" #< used to identify the project in the ComfyUI node registry.


#================================= LOGGER ==================================#

# initialize the project logger
from comfy.cli_args      import args
from .nodes.core.system  import setup_logger
if os.getenv('ZIMAGE_NODES_DEBUG'):
    setup_logger(log_level="DEBUG", emoji=__PROJECT_EMOJI, name="ZI_POWER", use_stdout=args.log_stdout)
else:
    #console_log_level = get_console_log_level(args.verbose)
    setup_logger(log_level='INFO', emoji=__PROJECT_EMOJI, name="ZI_POWER", use_stdout=args.log_stdout)

# import the newly initialized project logger
from .nodes.core.system  import logger


#============================ HELPER FUNCTIONS =============================#

def _register_node(node_class      : type,
                   node_class_list : list[type],
                   node_subcategory: str,
                   deprecated      : bool | None = None,
                   experimental    : bool | None = None,
                   ):
    """
    Registers a node in the given `node_class_list` with appropriate title based on its category and status.

    After registering all the nodes, the `node_class_list` can be sent to comfy
    in the function `get_node_list(self)` of a ComfyExtension.

    Args:
        node_class           : The class of the node to be registered.
        node_class_list      : List where the node will be appended after registration.
        node_subcategory     : The subcategory for the node (used for menu grouping).
        deprecated (optional): Indicates if the node is deprecated. If not provided,
                               it's automatically determined based on the subcategory.
    """

    # if `deprecated`` is not provided, it will be automatically
    # determined based on the subcategory where it's being registered
    if deprecated == None:
        deprecated = "deprecated" in node_subcategory.lower()

    # if `experimental` is not provided, it will be automatically
    # determined based on the subcategory where it's being registered
    if experimental == None:
        experimental = "experimental" in node_subcategory.lower()

    # add a '/' to the beginning of node_subcategory if it doesn't already start with one
    if node_subcategory and not node_subcategory.startswith("/"):
        node_subcategory = "/" + node_subcategory

    class_name     = node_class.__name__
    title          = node_class.xTITLE
    category       = f"{__PROJECT_EMOJI}{__PROJECT_MENU}{node_subcategory}"
    comfy_node_id  = f"{class_name} {__PROJECT_ID}"

    if deprecated:
        title = f"❌[DEPRECATED] {title}"
    elif experimental:
        title = f"⚗️🔬| {title}"
    else:
        title = f"{__PROJECT_EMOJI}| {title}"

    node_class.xTITLE         = title
    node_class.xCATEGORY      = category
    node_class.xCOMFY_NODE_ID = comfy_node_id
    node_class.xDEPRECATED    = deprecated
    node_class_list.append( node_class )


#======================= COMFY EXTENSION (V3 schema) =======================#

class ZImagePowerNodesExtension(ComfyExtension):

    # must be declared as async
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        _PROJECT_MENU= "ZiNodes"
        nodes = []


        #-- ROOT --------------------------------
        subcategory = ""

        from .nodes.zsampler_turbo_2_simple import ZSamplerTurbo2Simple
        _register_node( ZSamplerTurbo2Simple, nodes, subcategory )

        from .nodes.zsampler_turbo_2 import ZSamplerTurbo2
        _register_node( ZSamplerTurbo2, nodes, subcategory )

        from .nodes.zsampler_turbo_2_advanced import ZSamplerTurbo2Advanced
        _register_node( ZSamplerTurbo2Advanced, nodes, subcategory )

        from .nodes.style_prompt_encoder_2 import StylePromptEncoder2
        _register_node( StylePromptEncoder2, nodes, subcategory )

        from .nodes.style_string_injector_2 import StyleStringInjector2
        _register_node( StyleStringInjector2, nodes, subcategory )

        from .nodes.my_top_10_styles import MyTop10Styles
        _register_node( MyTop10Styles, nodes, subcategory )

        from .nodes.my_top_10_styles_editor import MyTop10StylesEditor
        _register_node( MyTop10StylesEditor, nodes, subcategory )

        from .nodes.save_image import SaveImage
        _register_node( SaveImage, nodes, subcategory )

        from .nodes.empty_zimage_latent_image import EmptyZImageLatentImage
        _register_node( EmptyZImageLatentImage, nodes, subcategory )

        from .nodes.vae_encode_soft_inpainting import VAEEncodeSoftInpainting
        _register_node( VAEEncodeSoftInpainting, nodes, subcategory )


        #--[ __deprecated ]----------------------
        subcategory = "__deprecated"

        # this is where nodes that were deprecated and
        # maintained only for compatibility go

        from .nodes.deprecated_nodes.photo_style_prompt_encoder import PhotoStylePromptEncoder
        _register_node( PhotoStylePromptEncoder, nodes, subcategory )

        from .nodes.deprecated_nodes.illustration_style_prompt_encoder import IllustrationStylePromptEncoder
        _register_node( IllustrationStylePromptEncoder, nodes, subcategory )

        from .nodes.deprecated_nodes.style_prompt_encoder import StylePromptEncoder
        _register_node( StylePromptEncoder, nodes, subcategory )

        from .nodes.deprecated_nodes.style_string_injector import StyleStringInjector
        _register_node( StyleStringInjector, nodes, subcategory )

        from .nodes.deprecated_nodes.zsampler_turbo_1 import ZSamplerTurbo
        _register_node( ZSamplerTurbo, nodes, subcategory )

        from .nodes.deprecated_nodes.zsampler_turbo_1_advanced import ZSamplerTurboAdvanced
        _register_node( ZSamplerTurboAdvanced, nodes, subcategory )

        from .nodes.deprecated_nodes.zsampler_turbo_2_laboratory import ZSamplerTurbo2Laboratory
        _register_node( ZSamplerTurbo2Laboratory, nodes, subcategory )


        #--[ __experimental ]--------------------
        subcategory = "__experimental"

        from .nodes.load_zimage_model import LoadZImageModel
        _register_node( LoadZImageModel, nodes, subcategory )

        from .nodes.load_qwen34b_model import LoadQwen34bModel
        _register_node( LoadQwen34bModel, nodes, subcategory )

        from .nodes.zsampler_turbo_X21 import ZSamplerTurboX21
        _register_node( ZSamplerTurboX21, nodes, subcategory )

        from .nodes.zsampler_turbo_X21_advanced import ZSamplerTurboX21Advanced
        _register_node( ZSamplerTurboX21Advanced, nodes, subcategory )

        from .nodes.style_prompt_encoder_X21 import StylePromptEncoderX21
        _register_node( StylePromptEncoderX21, nodes, subcategory )

        from .nodes.custom_style_prompt_encoder_X21 import CustomStylePromptEncoderX21
        _register_node( CustomStylePromptEncoderX21, nodes, subcategory )

        from .nodes.advanced_vae_decoder_X21 import AdvancedVAEDecoderX21
        _register_node( AdvancedVAEDecoderX21, nodes, subcategory )

        from .nodes.basic_image_filters import BasicImageFilters
        _register_node( BasicImageFilters, nodes, subcategory )


        #--[ utils ]-----------------------------
        subcategory = "utils"

        from .nodes.image_labeler import ImageLabeler
        _register_node( ImageLabeler, nodes, subcategory )

        from .nodes.image_grid_builder import ImageGridBuilder
        _register_node( ImageGridBuilder, nodes, subcategory )


        # report version and the number of nodes added by this extension
        version           = get_project_version()
        num_of_deprecated = sum(node_class.xDEPRECATED for node_class in nodes)
        num_of_nodes      = len(nodes) - num_of_deprecated
        and_deprecated    = f" and {num_of_deprecated} deprecated ones" if num_of_deprecated>0 else ""

        # count the number of pre-defined styles that are not custom styles
        canonical_names            = PREDEFINED_STYLES.by_version("1.0.0").canonical_names()
        num_of_predefined_styles   = sum(1 for name in canonical_names if not name.startswith("custom"))
        num_of_predefined_palettes = len( PREDEFINED_PALETTES.by_version("2.0.0") );

        logger.info(f"Version: {version}")
        logger.info(f"This package includes {num_of_nodes} active nodes{and_deprecated}.")
        logger.info(f"It also features {num_of_predefined_styles} predefined visual styles,")
        logger.info(f"and {num_of_predefined_palettes} predefined palettes.")
        return nodes


async def comfy_entrypoint() -> ZImagePowerNodesExtension:
    return ZImagePowerNodesExtension()


WEB_DIRECTORY = "./js"
__all__ = ["WEB_DIRECTORY"]

"""
File    : empty_zimage_latent_image.py
Purpose : Create a new batch of empty latent images to be used as a starting point.
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jan 18, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

    The V3 schema documentation can be found here:
    - https://docs.comfy.org/custom-nodes/v3_migration

"""
import torch
import comfy.model_management
from comfy_api.latest import io

LANDSCAPE_SIZES_BY_ASPECT_RATIO = {
    "1:1  (square)"      : (1024.0, 1024.0), # Social media posts and profile pictures
    "4:3  (retro tv)"    : (1182.4,  886.8), # Legacy television and older computer monitors
    "3:2  (photo)"       : (1252.8,  837.0), # DSLR cameras and standard 35mm film # (1254.1, 836.1)
    "16:10  (monitor)"   : (1295.3,  809.5), # Common in MacBooks and productivity laptops
    "16:9  (widescreen)" : (1365.3,  768.0), # Current universal standard for video and TV
    "2:1  (univisium)"   : (1448.2,  724.0), # Modern streaming series and smartphone screens
    "21:9  (ultrawide)"  : (1564.2,  670.4), # Wide cinema format and ultrawide monitors
    "12:5  (anamorphic)" : (1586.4,  661.0), # Standard theatrical widescreen cinema release
    "70:27  (cinerama)"  : (1648.8,  636.0), # Extreme panoramic cinema format
    "32:9  (super wide)" : (1930.9,  543.0), # Dual-monitor width for ultra-wide displays
    # "48:35  (35 mm)"     : (1199.2,  874.4),
    # "71:50  (~imax)"     : (1220.2,  859.3),
}
SCALES_BY_NAME = {
    "small"                : 1.0,
    "medium (recommended)" : 1.3,
    "large"                : 1.6,
}

DEFAULT_ASPECT_RATIO = "3:2  (photo)"
DEFAULT_SCALE        = "medium (recommended)"


class EmptyZImageLatentImage(io.ComfyNode):
    xTITLE         = "Empty Z-Image Latent Image"
    xCATEGORY      = ""
    xCOMFY_NODE_ID = ""
    xDEPRECATED    = False

    #__ INPUT / OUTPUT ____________________________________
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            display_name  = cls.xTITLE,
            category      = cls.xCATEGORY,
            node_id       = cls.xCOMFY_NODE_ID,
            is_deprecated = cls.xDEPRECATED,
            description   = (
                "Create a new batch of empty latent images to be used as a starting point for denoising with the Z-Image model."
            ),
            inputs=[
                io.Boolean.Input("horizontal",
                                 default=False, label_on="yes", label_off="no",
                                 tooltip="When enabled, the generated images will have a landscape orientation. "
                                         "By default, the node produces portrait images prioritizing mobile use. ",
                                ),
                io.Combo.Input  ("ratio",
                                 default=DEFAULT_ASPECT_RATIO, options=cls.ratios(),
                                 tooltip="The aspect ratio for the generated images. This affects the width-to-height "
                                         "proportion of the image. ",
                                 ),
                io.Combo.Input  ("size",
                                 default=DEFAULT_SCALE, options=cls.sizes(),
                                 tooltip="The relative size of the generated images. Larger sizes can lead to more "
                                         "detailed results but require more computational resources and may cause "
                                         "hallucinations in some cases. ",
                                  ),
                io.Int.Input    ("batch_size",
                                 default=1, min=1, max=4096,
                                 tooltip="The number of images to generate in a single processing batch.",
                                ),
            ],
            outputs=[
                io.Latent.Output(tooltip="An empty latent image generated according to the given parameters."),
                io.Int.Output(display_name="width",
                              tooltip="Actual pixel width after snapping to the 32-pixel grid."),
                io.Int.Output(display_name="height",
                              tooltip="Actual pixel height after snapping to the 32-pixel grid."),
            ]
        )

    #__ FUNCTION __________________________________________
    @classmethod
    def execute(cls, horizontal: bool, ratio: str, size: str, batch_size: int) -> io.NodeOutput:
        GRID_SIZE         = 32
        LATENT_CHANNELS   = 16  #< z-image latent has 16 channels
        LATENT_BLOCK_SIZE =  8  #< 8x8 pixels per latent block

        scale                         = SCALES_BY_NAME.get(size, 1.0)
        desired_width, desired_height = LANDSCAPE_SIZES_BY_ASPECT_RATIO.get(ratio, (1024, 1024))
        desired_width, desired_height = desired_width * scale, desired_height * scale
        if not horizontal:
            desired_width, desired_height = desired_height, desired_width

        # fix image size to be divisible by the grid
        image_width  = int( (desired_width  // GRID_SIZE) * GRID_SIZE )
        image_height = int( (desired_height // GRID_SIZE) * GRID_SIZE )

        # calculate the latent dimensions
        latent_width    = int( image_width  // LATENT_BLOCK_SIZE )
        latent_height   = int( image_height // LATENT_BLOCK_SIZE )
        latent_device   = comfy.model_management.intermediate_device()

        # create the latent image as a tensor of zeros
        latent = torch.zeros( (batch_size, LATENT_CHANNELS, latent_height, latent_width), device=latent_device )
        return io.NodeOutput({"samples": latent}, image_width, image_height)


    #__ internal functions ________________________________

    @classmethod
    def ratios(cls) -> list[str]:
        return list( LANDSCAPE_SIZES_BY_ASPECT_RATIO.keys() )

    @classmethod
    def sizes(cls) -> list[str]:
        return list( SCALES_BY_NAME.keys() )



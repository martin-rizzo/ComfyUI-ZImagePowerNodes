"""
File    : basic_image_filters.py
Purpose : Experimental node to apply simple filters to generated images.
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jul 27, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
     ComfyUI nodes designed to power the "Z-Image/Z-Image Turbo" models.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

 ComfyUI V3 Schema oficial documentation:
 - https://docs.comfy.org/custom-nodes/v3_migration

"""
import torch
from enum                import Enum
from typing              import Any
from functools           import cache
from comfy_api.latest    import io
from .custom_widgets     import Separator
from .core.helpers_image import adjust_hsv_components, stretch_histogram, apply_dithering, convert_to_rgb
class Filter(Enum):
    """Enum representing available image processing filters.
    Attributes:
        NONE            : Represents no filter applied.
        BLACK_AND_WHITE : Grayscale filter.
        COLOR           : Standard color level filter.
        COLOR_TWIST     : Hue component twist filter.
        INTENSITY_1     : Low color intensity filter.
        INTENSITY_2     : High color intensity filter.
    """
    NONE             = "none"
    BLACK_AND_WHITE  = "bw"
    COLOR            = "color"
    COLOR_TWIST      = "color_twist"
    INTENSITY_1      = "intensity_1"
    INTENSITY_2      = "intensity_2"
   #SATURATION_NOISE = "saturation_noise"


class BasicImageFilters(io.ComfyNode):
    xTITLE         = "Basic Image Filters"
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
            description   = (""
            ),
            search_aliases=["decode", "decode latent", "latent to image", "render latent"],
            inputs=[
                io.Image.Input       ("images"),
                io.Boolean.Input     ("enable_auto_contrast",
                                      tooltip="When enabled, automatically adjusts the dynamic range of the "
                                              "image to fix washed-out tones and optimize contrast boundaries."
                                     ),
                io.Boolean.Input     ("enable_filters",
                                      tooltip="When enabled, applies the color correction filters configured below. "
                                              "If disabled, all filter selections and adjustments are bypassed."
                                     ),
                Separator.Input("divider1", mode="divider"),#--------------------------------------
                io.Combo.Input       ("filter_1",
                                      options=cls.filters(),
                                      tooltip="The color correction filter to apply to the resulting image."
                                     ),
                io.Float.Input       ("filter_1_control", min=-0.5, max=0.5, default=0.0, step=0.1,
                                      tooltip="The calibration offset for the selected filter. "
                                              "This value has a range from -0.5 to 0.5 with 0.0 as the "
                                              "default ideal baseline balance."
                                     ),
                Separator.Input("divider2", mode="spacer"),#--------------------------------------
                io.Combo.Input       ("filter_2",
                                      options=cls.filters(),
                                      tooltip="The color correction filter to apply to the resulting image."
                                     ),
                io.Float.Input       ("filter_2_control", min=-0.5, max=0.5, default=0.0, step=0.1,
                                      tooltip="The calibration offset for the selected filter. "
                                              "This value has a range from -0.5 to 0.5 with 0.0 as the "
                                              "default ideal baseline balance."
                                     ),
                Separator.Input("divider3", mode="spacer"),#--------------------------------------
                io.Combo.Input       ("filter_3",
                                      options=cls.filters(),
                                      tooltip="The color correction filter to apply to the resulting image."
                                     ),
                io.Float.Input       ("filter_3_control", min=-0.5, max=0.5, default=0.0, step=0.1,
                                      tooltip="The calibration offset for the selected filter. "
                                              "This value has a range from -0.5 to 0.5 with 0.0 as the "
                                              "default ideal baseline balance."
                                     ),
            ],
            outputs=[
                io.Image.Output(tooltip="The final filtered image."),
            ],
        )

    #__ FUNCTION __________________________________________
    @classmethod
    def execute(cls,
                images: torch.Tensor,
                enable_auto_contrast: bool,
                enable_filters      : bool,
                filter_1            : str,
                filter_1_control    : float,
                filter_2            : str,
                filter_2_control    : float,
                filter_3            : str,
                filter_3_control    : float,
                divider1: Any = None,
                divider2: Any = None,
                divider3: Any = None,
                ):

        # convert images to shape [B, C, H, W] compatible with torchvision & kornia
        images = images.permute(0, 3, 1, 2)
        color_space = 'rgb'

        # restrict values to [0,1] via contrast adjustment or direct clamping
        if enable_auto_contrast:
            images = stretch_histogram(images)
        else:
            images = torch.clamp(images, 0.0, 1.0)

        # apply filters, which may modify the color space of the images
        if enable_filters:
            images, color_space = cls.apply_filter_to_images(images, color_space, filter_1, filter_1_control)
            images, color_space = cls.apply_filter_to_images(images, color_space, filter_2, filter_2_control)
            images, color_space = cls.apply_filter_to_images(images, color_space, filter_3, filter_3_control)

        # convert back to RGB color space
        # and return to [B, H, W, C] shape, which is compatible with ComfyUI
        images = convert_to_rgb(images, color_space).permute(0, 2, 3, 1).contiguous()
        return (images, )


    #__ internal functions ________________________________

    @staticmethod
    def apply_filter_to_images(images     : torch.Tensor,
                               color_space: str,
                               filter     : Filter | str,
                               value      : float
                               ) -> tuple[torch.Tensor, str]:
        if isinstance(filter,str):
            filter = Filter(filter)

        if filter == Filter.NONE:
            return images, color_space

        elif filter == Filter.BLACK_AND_WHITE:
            contrast_factor = 1 + (value*1.2 if value<0 else value*0.8)
            images = adjust_hsv_components(images,
                                           saturation_target      = 0,
                                           contrast_scurve_factor = contrast_factor,
                                           input_color_space      = color_space)
            return images, 'hsv'

        elif filter == Filter.COLOR:
            contrast_factor = 1 + (value*1.0 if value<0 else value*1.0)
            images = adjust_hsv_components(images,
                                           saturation_scurve_factor = contrast_factor,
                                           contrast_scurve_factor   = (contrast_factor-1)*0.2 + 1,
                                           input_color_space        = color_space)
            return images, 'hsv'

        elif filter == Filter.COLOR_TWIST:
            images = adjust_hsv_components(images,
                                           hue_shift_factor  = value*2,
                                           input_color_space = color_space)
            return images, 'hsv'

        elif filter == Filter.INTENSITY_1:
            contrast_factor = 1 + (value*1.0 if value<0 else value*1.0)
            images = adjust_hsv_components(images,
                                           saturation_target      = 0.35,
                                           contrast_scurve_factor = contrast_factor,
                                           input_color_space      = color_space)
            return images, 'hsv'

        elif filter == Filter.INTENSITY_2:
            contrast_factor = 1 + (value*1.0 if value<0 else value*1.0)
            images = adjust_hsv_components(images,
                                           saturation_target      = 0.40,
                                           contrast_scurve_factor = contrast_factor,
                                           input_color_space      = color_space)
            return images, 'hsv'

        raise ValueError(f'Invalid filter: {filter.value}')


    @staticmethod
    @cache
    def filters() -> list[str]:
        return [f.value for f in Filter]

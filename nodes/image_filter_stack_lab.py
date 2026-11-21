"""
File    : image_filter_stack_lab.py
Purpose : Node to apply simple post-processing filters to images using LAB color space
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Nov 13, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
     ComfyUI nodes designed to power the "Z-Image/Z-Image Turbo" models.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

 ATTENTION:
  As a convention in this module, the Lab color space is handled as follows:
   - Tuple of 3 Tensors (ColorChannels): "L" is normalized to [0, 1].
   - Single Tensor                     : "L" uses the standard range of [0, 100].

"""
import kornia
import torch
import math
from torch import Tensor
from torchvision.transforms.v2.functional import gaussian_blur
from enum                import Enum
from typing              import TypeAlias, NamedTuple
from comfy_api.latest    import io
from .                   import widgets as zi
from functools           import cache
ColorChannels: TypeAlias = tuple[Tensor, Tensor, Tensor]


class Filter(Enum):
    """
    Enum representing available image processing filter effects.

    Members:
        NONE            : No filter effect is applied.
        COLOR           : Linear color level adjustment (saturation).
        COLOR_SHIFT     : Linear hue shift adjustment.
        COLOR_TWIST     : Hue shift that varies with pixel lightness.
        CHROMA_BLUR     : Gaussian blur applied exclusively to chrominance components.
        CONTRAST_Z      : Contrast-like correction, calibrated for Z-Image models.
        BRIGHTNESS_CURVE: Brightness curve adjustment based on the initial slope at x=0.
    """
    NONE             = "none"
    COLOR            = "color"
    COLOR_SHIFT      = "color_shift"
    COLOR_TWIST      = "color_twist"
    CHROMA_BLUR      = "chroma_blur"
    CONTRAST_Z       = "contrast_z"
    BRIGHTNESS_CURVE = "brightness_curve"


class FilterRange(NamedTuple):
    """
    Defines the valid range and default value for a filter parameter.

    Attributes:
        min_val: The minimum allowed value for the filter.
        default: The baseline value for the filter.
        max_val: The maximum allowed value for the filter.
    """
    min_val: float
    default: float
    max_val: float


FILTER_RANGES: dict[Filter, FilterRange] = {
    Filter.COLOR:            FilterRange(0.20, 1.00, 2.10),
    Filter.COLOR_SHIFT:      FilterRange(-15,     0,   15),
    Filter.COLOR_TWIST:      FilterRange(-90,     0,   90),
    Filter.CHROMA_BLUR:      FilterRange(  5,     0,    5),
    Filter.BRIGHTNESS_CURVE: FilterRange(0.50, 1.00, 2.20),
    Filter.CONTRAST_Z:       FilterRange(0.30, 0.66, 1.10),
}
"""Mapping of filter enums to their (min_val, default, max_val) value ranges."""




class ImageFilterStackLAB(io.ComfyNode):
    xTITLE         = "Image Filter Stack [LAB]"
    xDESCRIPTION   = (
        "Applies a set of image processing filters for post-generation color "
        "correction and tone adjustment. Supports up to five simultaneous "
        "filtering layers that execute in sequence. Additionally includes an "
        "optional automatic contrast normalization pass. NOTE: This version of "
        "the node performs its internal operations in the LAB color space, "
        "which tends to produce better color tones."
    )
    xCATEGORY      = ""
    xCOMFY_NODE_ID = ""
    xDEPRECATED    = False

    #__ INPUT / OUTPUT ____________________________________
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            display_name  = cls.xTITLE,
            description   = cls.xDESCRIPTION,
            category      = cls.xCATEGORY,
            node_id       = cls.xCOMFY_NODE_ID,
            is_deprecated = cls.xDEPRECATED,
            search_aliases=["decode", "decode latent", "latent to image", "render latent"],
            inputs=[
                io.Image.Input    ("image"
                                  ),
                io.String.Input   ("settings",
                                   optional=True, multiline=True, force_input=True,
                                   tooltip="A string listing variables and their values for each filter you wish to customize.",
                                  ),

                io.Boolean.Input  ("enable_auto_contrast",
                                   tooltip="When enabled, automatically adjusts the dynamic range of the "
                                           "image to fix washed-out tones and optimize contrast boundaries."
                                  ),

                zi.Separator.Input("divider", mode="divider"),#====================================

                io.Boolean.Input  ("enable_filters",
                                   tooltip="When enabled, applies the color correction filters configured below. "
                                           "If disabled, all filter selections and adjustments are bypassed."
                                  ),

                zi.Separator.Input("spacer1", mode="spacer", height=4),#===========================

                io.Combo.Input    ("filter1",
                                   options=cls.available_filters(),
                                   tooltip="The first color correction filter to apply to the resulting image."
                                  ),
                io.Float.Input    ("filter1_tweak",
                                   default=0.0, min=-0.5, max=0.5, step=0.1, round=0.1,
                                   tooltip="The fine-tuning control for the filter. "
                                           "Range is -0.5 to 0.5, with 0.0 as the ideal baseline balance. "
                                  ),

                zi.Separator.Input("spacer2", mode="spacer", height=6),#===========================

                io.Combo.Input    ("filter2",
                                   options=cls.available_filters(),
                                   tooltip="The second color correction filter to apply to the resulting image."
                                  ),
                io.Float.Input    ("filter2_tweak",
                                   default=0.0, min=-0.5, max=0.5, step=0.1, round=0.1,
                                   tooltip="The fine-tuning control for the filter. "
                                           "Range is -0.5 to 0.5, with 0.0 as the ideal baseline balance. "
                                  ),

                zi.Separator.Input("spacer3", mode="spacer", height=6),#===========================

                io.Combo.Input    ("filter3",
                                   options=cls.available_filters(),
                                   tooltip="The third color correction filter to apply to the resulting image."
                                  ),
                io.Float.Input    ("filter3_tweak",
                                   default=0.0, min=-0.5, max=0.5, step=0.1, round=0.1,
                                   tooltip="The fine-tuning control for the filter. "
                                           "Range is -0.5 to 0.5, with 0.0 as the ideal baseline balance. "
                                  ),

                zi.Separator.Input("spacer4", mode="spacer", height=6),#===========================

                io.Combo.Input    ("filter4",
                                   options=cls.available_filters(),
                                   tooltip="The fourth color correction filter to apply to the resulting image."
                                  ),
                io.Float.Input    ("filter4_tweak",
                                   default=0.0, min=-0.5, max=0.5, step=0.1, round=0.1,
                                   tooltip="The fine-tuning control for the filter. "
                                           "Range is -0.5 to 0.5, with 0.0 as the ideal baseline balance. "
                                  ),

                zi.Separator.Input("spacer5", mode="spacer", height=6),#===========================

                io.Combo.Input    ("filter5",
                                   options=cls.available_filters(),
                                   tooltip="The fifth color correction filter to apply to the resulting image."
                                  ),
                io.Float.Input    ("filter5_tweak",
                                   default=0.0, min=-0.5, max=0.5, step=0.1, round=0.1,
                                   tooltip="The fine-tuning control for the filter. "
                                           "Range is -0.5 to 0.5, with 0.0 as the ideal baseline balance. "
                                  ),
            ],
            outputs=[
                io.Image.Output(tooltip="The final filtered image."),
            ],
        )

    #__ FUNCTION __________________________________________
    @classmethod
    def execute(cls,
                image               : Tensor,
                enable_auto_contrast: bool,
                enable_filters      : bool,
                filter1             : str,
                filter1_tweak       : float,
                filter2             : str,
                filter2_tweak       : float,
                filter3             : str,
                filter3_tweak       : float,
                filter4             : str,
                filter4_tweak       : float,
                filter5             : str,
                filter5_tweak       : float,
                settings            : dict[str,str] | str | None = None,
                divider=None, spacer1=None, spacer2=None, spacer3=None, spacer4=None, spacer5=None
                ):
        # round float values to 1 decimal place
        filter1_tweak = round(filter1_tweak, 1)
        filter2_tweak = round(filter2_tweak, 1)
        filter3_tweak = round(filter3_tweak, 1)
        filter4_tweak = round(filter4_tweak, 1)
        filter5_tweak = round(filter5_tweak, 1)
        color_space = 'rgb'

        # if settings were provided as a string,
        # convert them to a dictionary of string key-value pairs
        if isinstance(settings,str):
            d: dict[str,str] = {}
            for line in settings.strip().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    d[key.strip()] = value.strip()
            settings = d
 

        # convert images to shape [B, C, H, W] compatible with torchvision & kornia.
        # additionally, we clone it to allow free 'in-place' modifications without altering the original.
        image = image.permute(0, 3, 1, 2).clone(memory_format=torch.contiguous_format)

        # restrict values to [0,1] via contrast adjustment or direct clamping
        if enable_auto_contrast:  image = _stretch_contrast(image)
        else:                     image.clamp_(0.0, 1.0)

        # apply filters, which may modify the color space of the images
        channels : ColorChannels | Tensor = image
        if enable_filters:
            channels, color_space = cls.apply_filter_to_channels(channels, color_space, filter=filter1, value=filter1_tweak*2, settings=settings)
            channels, color_space = cls.apply_filter_to_channels(channels, color_space, filter=filter2, value=filter2_tweak*2, settings=settings)
            channels, color_space = cls.apply_filter_to_channels(channels, color_space, filter=filter3, value=filter3_tweak*2, settings=settings)
            channels, color_space = cls.apply_filter_to_channels(channels, color_space, filter=filter4, value=filter4_tweak*2, settings=settings)
            channels, color_space = cls.apply_filter_to_channels(channels, color_space, filter=filter5, value=filter5_tweak*2, settings=settings)

        # convert back to a single tensor in RGB color space.
        # and return to [B, H, W, C] shape, which is compatible with ComfyUI.
        image = _as_rgb_tensor(channels, input_color_space = color_space, denormalize_lab = True)
        image = image.permute(0, 2, 3, 1).contiguous()

        # restrict values to [0,1] via contrast adjustment or direct clamping
        if enable_auto_contrast:  image = _stretch_contrast(image)
        else:                     image.clamp_(0.0, 1.0)

        return (image, )


    #__ internal functions ________________________________

    @staticmethod
    def apply_filter_to_channels(channels   : Tensor | ColorChannels,
                                 color_space: str,
                                 filter     : str | Filter,
                                 value      : float,
                                 settings   : dict[str, str] | None,
                                 ) -> tuple[Tensor | ColorChannels, str]:
        if isinstance(filter,str):
            filter = Filter(filter)

        if filter == Filter.NONE:
            return channels, color_space


        elif filter == Filter.COLOR:

            range = _get_filter_range("color", settings, default=FILTER_RANGES[filter])
            saturation_factor = _bipolar_lerp(value, range.min_val, range.default, range.max_val)
            channels = _lab_adjust_chrominance(channels,
                            saturation_factor = saturation_factor,
                            input_color_space = color_space)
            return channels, 'lab'


        elif filter == Filter.COLOR_SHIFT:

            range = _get_filter_range("color_shift", settings, default=FILTER_RANGES[filter])
            hue_shift_degrees = _bipolar_lerp(value, range.min_val, range.default, range.max_val)
            channels = _lab_adjust_chrominance(channels,
                            hue_shift_degrees = hue_shift_degrees,
                            input_color_space = color_space)
            return channels, 'lab'


        elif filter == Filter.COLOR_TWIST:

            range = _get_filter_range("color_twist", settings, default=FILTER_RANGES[filter])
            hue_twist_degrees = _bipolar_lerp(value, range.min_val, range.default, range.max_val)
            channels = _lab_adjust_chrominance(channels,
                            hue_twist_degrees = hue_twist_degrees,
                            input_color_space = color_space)
            return channels, 'lab'


        elif filter == Filter.CHROMA_BLUR:

            range = _get_filter_range("chroma_blur", settings, default=FILTER_RANGES[filter])
            chroma_blur   = _bipolar_lerp(value, range.min_val, range.default, range.max_val)
            channels = _lab_adjust_chrominance(channels,
                            chroma_blur       = chroma_blur,
                            input_color_space = color_space)
            return channels, 'lab'


        elif filter == Filter.CONTRAST_Z:

            range = _get_filter_range("contrast_z", settings, default=FILTER_RANGES[filter])
            scurve_factor = _bipolar_lerp(value, range.min_val, range.default, range.max_val)
            channels = _lab_adjust_lightness(channels,
                            lightness_scurve_factor = scurve_factor,
                            lightness_scurve_pivot  = 0.25,
                            input_color_space       = color_space)
            return channels, 'lab'


        elif filter == Filter.BRIGHTNESS_CURVE:

            range = _get_filter_range("brightness_curve", settings, default=FILTER_RANGES[filter])
            lightness_initial_slope = _bipolar_lerp(value, range.min_val, range.default, range.max_val)
            channels = _lab_adjust_lightness(channels,
                            lightness_initial_slope = lightness_initial_slope,
                            input_color_space       = color_space)
            return channels, 'lab'


        raise ValueError(f'Invalid effect: {filter.value}')


    @staticmethod
    @cache
    def available_filters() -> list[str]:
        return [f.value for f in Filter]



#========================= COLOR SPACE CONVERSIONS =========================#

def _as_lab_channels(channels: Tensor | ColorChannels,
                     *,
                     input_color_space: str  = "rgb",
                     normalize_lab    : bool = False
                     ) -> ColorChannels:
    """
    Converts a image into a tuple of Lab components (L, a, b).

    Note that the returned components may share memory with the input `channels`,
    therefore, in-place modifications to the returned components can indirectly
    affect the original `channels`.

    Args:
        channels          : The image channels, represented as a single tensor or a tuple of three tensors.
        input_color_space : The color space of the input channels. Defaults to "rgb".
        normalize_lab     : If True, scales the L component of the Lab channels from [0, 100] to [0, 1].

    Returns:
        A tuple of three tensors representing the 'L', 'a', and 'b' components of the image.
        Each tensor has the shape [B, 1, H, W]
    """
    if isinstance(channels,tuple) and input_color_space == "lab":
        return channels

    # ensure input is a tensor
    input_tensor : Tensor
    if isinstance(channels,torch.Tensor):
        input_tensor = channels
    elif isinstance(channels,tuple):
        input_tensor = torch.cat([channels[0], channels[1], channels[2]], dim=1)

    # convert to Lab
    lab_tensor : Tensor
    if   input_color_space == "rgb": lab_tensor = kornia.color.rgb_to_lab(input_tensor)
    elif input_color_space == "hsv": lab_tensor = kornia.color.rgb_to_lab(kornia.color.hsv_to_rgb(input_tensor))
    elif input_color_space == "lab": lab_tensor = input_tensor
    else:
        raise ValueError(f"Unsupported input_color_space: {input_color_space}")

    # return a tuple with each Lab component,
    # normalizing the 'L' component if required
    L, a, b = torch.split(lab_tensor, 1, dim=1)
    if normalize_lab:
        L.mul_(0.01)
    return (L,a,b)


def _as_rgb_tensor(channels: Tensor | ColorChannels,
                   *,
                   input_color_space: str  = "lab",
                   denormalize_lab  : bool = False
                   ) -> Tensor:
    """
    Converts image channels into a single RGB tensor.

    Note that the returned tensor may share memory with the input `channels`,
    therefore, in-place modifications to the returned tensor can indirectly
    affect the original `channels`.

    Args:
        channels         : The image channels, represented as a single tensor or a tuple of three tensors.
        input_color_space: The color space of the input channels. Defaults to "lab".
        denormalize_lab  : If True, scales the L component of LAB channels from [0, 1] back to [0, 100].

    Returns:
        A single tensor representing the image in RGB format.
        If the input is already an RGB tensor, it is returned directly.
    """
    if isinstance(channels,Tensor) and input_color_space == "rgb":
        return channels

    # LAB tuples have the 'L' component normalized to [0, 1].
    # If the user requests denormalization, it must be multiplied by 100.
    if denormalize_lab and isinstance(channels,tuple) and input_color_space == "lab":
        channels[0].mul_(100)

    # concatenate channel dimensions if necessary
    tensor : Tensor
    if isinstance(channels,tuple): tensor = torch.cat(channels, dim=1)
    else:                          tensor = channels

    # convert to RGB if necessary
    if   input_color_space == "rgb": return tensor
    elif input_color_space == "hsv": return kornia.color.hsv_to_rgb(tensor)
    elif input_color_space == "lab": return kornia.color.lab_to_rgb(tensor)
    else:
        raise ValueError(f"Unsupported input_color_space: {input_color_space}")


#============================ IMAGE ADJUSTMENTS ============================#

def _stretch_contrast(images: Tensor,
                      *,
                      q_lower: float = 0.001,
                      q_upper: float = 0.999
                      ) -> Tensor:
    """
    Expands the dynamic range of a batch of images by stretching the histogram.

    Args:
        images : The input tensor with shape [B, C, H, W]
                    with values normalized in the range [0.0, 1.0].
        q_lower: The lower quantile to ignore (e.g., 0.001 for bottom 0.1%).
        q_upper: The upper quantile to ignore (e.g., 0.999 for top 0.1%).

    Returns:
        A tensor containing the batch of images with the dynamic range expanded.
    """
    b, c, h, w = images.shape

    # flatten H, W, C dimensions per batch image -> [B, C*H*W]
    flattened = images.reshape(b, -1)

    # calculate quantiles for each image independently;
    # torch.quantile returns the value at which a specific percentage of data falls;
    # dim=1 ensures independent calculation per image; reshape to [B,1,1,1] allows broadcasting
    low_vals  = torch.quantile(flattened, q_lower, dim=1, keepdim=True).view(b, 1, 1, 1)
    high_vals = torch.quantile(flattened, q_upper, dim=1, keepdim=True).view(b, 1, 1, 1)

    # calculate the range of values for each image and stretch it to [0,1]
    dynamic_range = (high_vals - low_vals).clamp(min=1e-7)
    images = (images - low_vals) / dynamic_range

    # clamp as outliers outside the quantiles will exceed the [0,1] range
    return torch.clamp(images, 0.0, 1.0)


def _lab_adjust_chrominance(image: Tensor | ColorChannels,
                            *,
                            hue_shift_degrees: float =   0.0,
                            hue_twist_degrees: float =   0.0,
                            saturation_factor: float =   1.0,
                            saturation_gamma : float =   1.0,
                            chroma_blur      : float =   0.0,
                            input_color_space: str   = "rgb",
                            ) -> ColorChannels:
    """
    Adjusts the chrominance (color) components of an image in the LAB color space.

    This function processes the 'a' and 'b' channels to apply various color adjustments,
    including hue shifting, hue twisting, saturation scaling, gamma correction, and
    chroma blurring. The 'L' (lightness) channel is preserved throughout the process.

    Args:
        image             : The input image channels, either as a single tensor or a tuple of three tensors.
        hue_shift_degrees : Global rotation angle (in degrees) applied to the a-b chrominance plane.
        hue_twist_degrees : Spatially varying rotation angle (in degrees) that modulates hue based on lightness.
        saturation_factor : Linear scaling factor for the a and b channels. 1.0 means no change.
        saturation_gamma  : Non-linear power factor applied to chroma magnitude. 1.0 disables gamma correction.
        chroma_blur       : Standard deviation for the Gaussian blur applied to the a and b channels. 0.0 disables blurring.
        input_color_space : The color space of the input channels. Defaults to "rgb".

    Returns:
        A tuple of three tensors (L, a, b) representing the adjusted chrominance components.
        Following the convention of this module, the returned Lab tuple always has L normalized to [0,1].
    """

    # ensure Lab components for internal processing; 'L' is normalized to [0,1]
    L, a, b = _as_lab_channels(image, input_color_space=input_color_space, normalize_lab=True)

    # this path applies "hue_shift" when hue_twist == 0.0;
    # it is very fast since it does not need to compute tensor maps for sine and cosine
    if hue_shift_degrees != 0.0 and hue_twist_degrees == 0.0:
        theta = math.radians(hue_shift_degrees)
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)

        a_sin_t = a * sin_t
        a.mul_(cos_t).sub_(b*sin_t)  # a = a * cos - b      * sin
        b.mul_(cos_t).add_(a_sin_t)  # b = b * cos + a_orig * sin

    # this path applies the combined effect of "hue_shift + hue_twist";
    # it is slightly slower and activates with a non-zero hue_twist value.
    if hue_twist_degrees != 0.0:
        shift_r = math.radians(hue_shift_degrees)
        twist_r = math.radians(hue_twist_degrees)

        # spatial theta based on L: (L * 2.0 - 1.0) * twist_r + shift_r
        theta = L.mul(2.0).sub_(1.0).mul_(twist_r).add_(shift_r)
        cos_t = torch.cos(theta)
        sin_t = torch.sin(theta)

        # vectorized spatial rotation (cos_t and sin_t are tensors [B, 1, H, W])
        a_sin_t = a * sin_t
        a.mul_(cos_t).sub_(b*sin_t)
        b.mul_(cos_t).add_(a_sin_t)


    if saturation_factor != 1.0:
        a.mul_(saturation_factor)
        b.mul_(saturation_factor)

    if saturation_gamma != 1.0 and saturation_gamma > 0.0:
        original_chroma = torch.sqrt(a**2 + b**2 + 1e-8)
        chroma = torch.pow(original_chroma, 1.0 / saturation_gamma)
        scale_ratio = chroma / original_chroma
        a.mul_(scale_ratio)
        b.mul_(scale_ratio)

    if chroma_blur > 0.0:
        sigma       = float(chroma_blur)
        kernel_size = int(2 * round(3 * sigma) + 1)
        kernel_size = max(3, kernel_size | 1)

        # concatenate a and b into [B, 2, H, W] and apply gaussian_blur in a single step
        ab = torch.cat([a, b], dim=1)
        ab = gaussian_blur(ab, kernel_size=[kernel_size, kernel_size], sigma=[sigma, sigma])
        a, b = ab.chunk(2, dim=1)

    return L, a, b


def _lab_adjust_lightness(image: Tensor | ColorChannels,
                          *,
                          lightness_stretch      : float =  0.0,
                          lightness_scurve_factor: float =  0.0,
                          lightness_scurve_pivot : float =  0.0,
                          lightness_initial_slope: float =  1.0,
                          lightness_target       : float = -1.0,
                          input_color_space      : str   = "rgb",
                          ) -> ColorChannels:
    """
    Adjusts the lightness (L) component of an image in the LAB color space.

    This function processes the 'L' channel to apply various lightness adjustments,
    including histogram stretching, S-curve mapping, initial slope modification,
    and global target mean adjustment. The 'a' and 'b' (chrominance) channels
    are preserved throughout the process.

    Args:
        image                   : The input image channels, either as a single tensor or a tuple of three tensors.
        lightness_stretch       : Blend factor for histogram stretching. 0.0 disables stretching.
        lightness_scurve_factor : Non-linear power factor for S-curve mapping. 0.0 disables S-curve.
        lightness_scurve_pivot  : Pivot point (0.0 to 1.0) around which the S-curve bends. 0.0 uses default pivot.
        lightness_initial_slope : Linear scaling factor for the initial slope of the lightness curve. 1.0 means no change.
        lightness_target        : Target mean lightness value. Negative values disable target adjustment.
        input_color_space       : The color space of the input channels. Defaults to "rgb".

    Returns:
        A tuple of three tensors (L, a, b) representing the adjusted lightness components.
        Following the convention of this module, the returned Lab tuple always has L normalized to [0,1].
    """

    # ensure Lab components for internal processing; 'L' is normalized to [0,1]
    L, a, b = _as_lab_channels(image, input_color_space=input_color_space, normalize_lab=True)

    if lightness_stretch != 0.0:
        L_stretched = _stretch_contrast(L, q_lower=0.001, q_upper=0.999)
        L = torch.lerp(L, L_stretched, lightness_stretch)

    if lightness_scurve_factor > 0.0 and lightness_scurve_factor != 1.0:
        if lightness_scurve_pivot <= 0.0:
            L.sub_(0.5).mul_(2.0)
            L = torch.sign(L) * torch.pow(torch.abs(L), 1.0 / lightness_scurve_factor)
            L.div_(2.0).add_(0.5)
        else:
            pivot       = float(lightness_scurve_pivot)
            pivot_slope = float(lightness_scurve_factor)
            curvature   = 8.00

            x0 = max(1e-6, min(1.0 - 1e-6, pivot))
            m  = pivot_slope
            k  = curvature

            t = (x0 - L) / x0
            L_left = x0 - x0 * (m * t + (1.0 - m) * torch.pow(torch.clamp(t, min=0.0), k))

            u = (L - x0) / (1.0 - x0)
            L_right = x0 + (1.0 - x0) * (m * u + (1.0 - m) * torch.pow(torch.clamp(u, min=0.0), k))

            L = torch.where(L <= x0, L_left, L_right)

    if lightness_initial_slope != 1.0:
        # apply schlick's rational curve to the normalized L component in [0, 1];
        # compresses highlights if p > 1.0 (or shadows if p < 1.0)
        # y = (p * x) / (1 + (p - 1) * x)
        L = (lightness_initial_slope * L) / (1.0 + (lightness_initial_slope - 1.0) * L)

    if lightness_target >= 0.0:
        L_mean = torch.mean(L, dim=(2, 3), keepdim=True)
        L_mean = torch.clamp(L_mean, min=1e-5)
        L = L * (lightness_target / L_mean)

    return L, a, b


#============================ HELPER FUNCTIONS =============================#

def _bipolar_lerp(factor: float, negative: float, neutral: float, positive: float, /) -> float:
    """
    Performs linear interpolation between `negative` and `positive` values, using `neutral` as pivot point.

    Args:
        factor   : Interpolation factor in the range [-1, 1].
        negative : The lower bound value       (used when factor is -1).
        neutral  : The pivot or baseline value (used when factor is  0).
        positive : The upper bound value       (used when factor is  1).

    Returns:
        The interpolated float value based on the given factor and bounds.
    """
    slope: float = (positive - neutral) if factor >= 0 else (neutral - negative)
    return neutral + factor * slope


def _get_filter_range(varname : str,
                      settings: dict[str, str] | None,
                      /,*,
                      default : FilterRange = FilterRange(-1.0, 0.0, 1.0),
                      ) -> FilterRange:
    """
    Retrieves a FilterRange from the settings dictionary for a given variable name.

    The function attempts to parse a comma-separated string (e.g., "-1.0,0.0,1.0")
    from the settings dictionary. If the string is valid and contains exactly three
    numbers, it returns them as a FilterRange. Otherwise, it falls back to the provided
    default value.

    Args:
        varname  : The key to look up in the settings dictionary.
        settings : A dictionary of string key-value pairs, or None.
        default  : The fallback FilterRange to return if parsing fails or the key is missing.

    Returns:
        A FilterRange representing the parsed values, or the default FilterRange.
    """
    raw_value = settings.get(varname) if isinstance(settings,dict) else None

    if not isinstance(raw_value, str):
        return default

    if raw_value.startswith("(") and raw_value.endswith(")"):
        raw_value = raw_value[1:-1]

    parts = raw_value.split(",")
    if len(parts) != 3:
        return default

    try:
        parsed = tuple(float(p.strip()) for p in parts)
    except ValueError:
        return default

    if any(not math.isfinite(val) for val in parsed):
        return default

    return FilterRange(*parsed)

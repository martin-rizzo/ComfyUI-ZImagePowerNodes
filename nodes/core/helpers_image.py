"""
File    : helpers_image.py
Purpose : Helpers functions for image color filtering using torch, torchvision and kornia
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jul 27, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
"""
import torch
import kornia
from typing import Final


def convert_to_rgb(images            : torch.Tensor,
                   input_color_space : str,
                   ) -> torch.Tensor:
    """
    Convert an input tensor from a specified color space to RGB.
    Args:
        images            : A tensor of shape (B, C, H, W) representing the input images.
        input_color_space : A string indicating the source color space.
                            Supported: 'rgb', 'bgr', 'hsv', 'lab', 'ycbcr'
    Returns:
        A tensor of shape (B, 3, H, W) in RGB color space.
    """
    input_color_space = input_color_space.lower().strip()

    if input_color_space == "rgb":
        return images
    elif input_color_space == "bgr":
        return kornia.color.bgr_to_rgb(images)
    elif input_color_space == "hsv":
        return kornia.color.hsv_to_rgb(images)
    elif input_color_space == "lab":
        return kornia.color.lab_to_rgb(images)
    elif input_color_space == "ycbcr":
        return kornia.color.ycbcr_to_rgb(images)
    else:
        raise ValueError(f"Color space '{input_color_space}' is not supported by convert_to_rgb.")


def calculate_robust_range(input_tensor : torch.Tensor,
                           low_quantile : float = 0.001,
                           high_quantile: float = 0.999,
                           ) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Calculate the lower and upper bounds of a tensor's distribution
    based on specified quantiles to facilitate range normalization.

    Args:
        input_tensor  : The input tensor with shape [B, C, H, W].
        low_quantile  : The lower percentile boundary (e.g., 0.001).
        high_quantile : The upper percentile boundary (e.g., 0.999).

    Returns:
        A tuple containing (low_vals, high_vals) shaped as [B, C, 1, 1].
    """
    # flatten spatial dimensions
    flat_view = input_tensor.flatten(2)  # [B, C, H*W]

    # calculate quantiles along the spatial dimensions
    low_vals  = torch.quantile(flat_view, low_quantile , dim=2, keepdim=True).unsqueeze(-1) # [B, C, 1, 1]
    high_vals = torch.quantile(flat_view, high_quantile, dim=2, keepdim=True).unsqueeze(-1) # [B, C, 1, 1]
    return low_vals, high_vals


def adjust_hsv_components(images                  : torch.Tensor,
                          *,
                          hue_twist_factor        : float =  0.0,
                          saturation_stretch      : float =  0.0,
                          saturation_gamma        : float =  1.0,
                          saturation_factor       : float =  1.0,
                          saturation_target       : float = -1.0,
                          brightness_stretch      : float =  0.0,
                          brightness_scurve_factor: float =  0.0,
                          brightness_scurve_pivot : float =  0.0,
                          brightness_target       : float = -1.0,

                          input_color_space       : str   = "rgb",
                          output_color_space      : str   = "hsv"
                          ) -> torch.Tensor:
    """
    Adjust HSV color space properties.

    Args:
        images                  : Input tensor with shape [B, 3, H, W] and range [0,1]
        hue_twist_factor        : Factor to shift the hue based on the value component.
        saturation_stretch      : Factor to linearly stretch the saturation histogram.
                                  - value = 0.0: Keeps original saturation range.
                                  - value = 1.0: Stretches to the full [0,1] range.
        saturation_gamma        : Gamma correction for the saturation channel. 
                                  - values > 1.0 increase saturation (curves upward)
                                  - values < 1.0 decrease saturation (curves downward)
        saturation_factor       : Multiplicative factor applied to the saturation channel.
        saturation_target       : Target mean saturation value.
        brightness_stretch      : Factor to linearly stretch the brightness histogram.
        brightness_scurve_factor: Power factor to apply an S-curve adjustment to the
                                  value/brightness channel around the 0.5 midpoint.
        brightness_target       : Target mean brightness value.
        input_color_space       : The color space of the input images ('rgb' or 'hsv').
                                  Defaults to "rgb".
        output_color_space      : The desired color space for the returned images ('rgb' or 'hsv').
                                  Defaults to "hsv".

    Returns:
        A tensor of processed images converted to the requested
        `output_color_space` with shape [B, 3, H, W] and range [0,1]
    """
    input_color_space  = input_color_space.lower().strip()
    output_color_space = output_color_space.lower().strip()

    # convert to HSV for internal processing
    if input_color_space == "rgb":
        hsv = kornia.color.rgb_to_hsv(images)
    elif input_color_space == "hsv":
        hsv = images
    else:
        raise ValueError(f"Unsupported input_color_space: {input_color_space}")

    # split the HSV channels
    h = hsv[:, 0:1, :, :]
    s = hsv[:, 1:2, :, :]
    v = hsv[:, 2:3, :, :]

    #-- HUE -------------------------------------

    # apply hue shift based on the 'value' component
    if hue_twist_factor != 0.0:
        hue_shift = hue_twist_factor * (v - 0.5)
        h = torch.remainder(h + hue_shift, 2 * 3.14159)

    #-- SATURATION ------------------------------

    # stretch saturation
    if saturation_stretch != 0.0:
        low_vals, high_vals = calculate_robust_range(s, 0.001, 0.999)
        s_stretched = (s - low_vals) / torch.clamp(high_vals - low_vals, min=1e-5)
        s_stretched.clamp_(min=0.0, max=1.0)
        # use `saturation_stretch` to calibrate (0.0 = original, 1.0 = fully stretched)
        s = torch.lerp(s, s_stretched, saturation_stretch)

    # apply power-law adjustment (gamma correction) to saturation
    # (this creates a curve that bows upward or downward)
    if saturation_gamma != 1.0 and saturation_gamma > 0.0:
        s = torch.pow(s, 1.0 / saturation_gamma)

    # linear scaling
    if saturation_factor != 1.0:
        s = s * saturation_factor

    # normalize saturation to target mean
    if saturation_target >= 0.0:
        s_mean = torch.mean(s, dim=(2, 3), keepdim=True) # [B, 1, 1, 1]
        s_mean = torch.clamp(s_mean, min=1e-5)
        s = s * (saturation_target / s_mean)

    # ensure saturation remains within valid HSV bounds
    s.clamp_(min=0.0, max=1.0)

    #-- VALUE/BRIGHTNESS ------------------------

    # stretch brightness
    if brightness_stretch != 0.0:
        low_vals, high_vals = calculate_robust_range(v, 0.001, 0.999)
        v_stretched = (v - low_vals) / torch.clamp(high_vals - low_vals, min=1e-5)
        v_stretched = torch.clamp(v_stretched, 0.0, 1.0)
        # use `brightness_stretch` to calibrate (0.0 = original, 1.0 = fully stretched)
        v = torch.lerp(v, v_stretched, brightness_stretch)

    # apply S-curve adjustment (gamma-like) to component 'v'
    if brightness_scurve_factor > 0.0 and brightness_scurve_factor != 1.0:

        # older version (without `brightness_scurve_pivot`):
        if brightness_scurve_pivot <= 0.0:
            v.sub_(0.5).mul_(2.0)
            v = torch.sign(v) * torch.pow(torch.abs(v), 1.0 / brightness_scurve_factor)
            v.div_(2.0).add_(0.5)

        # the new formula with `pivot` point
        # (the pivot is the inflexion point of the S-curve)
        else:
            pivot       = float(brightness_scurve_pivot)
            pivot_slope = float(brightness_scurve_factor)
            curvature   = 8.00

            # clamp parameters to safe ranges to avoid division by zero
            x0 = max(1e-6, min(1.0 - 1e-6, pivot))
            m  = pivot_slope
            k  = curvature

            # left branch (v <= x0): t = (x0 - v) / x0
            t = (x0 - v) / x0
            v_left = x0 - x0 * (m * t + (1.0 - m) * torch.pow(torch.clamp(t, min=0.0), k))

            # right branch (v > x0): u = (v - x0) / (1.0 - x0)
            u = (v - x0) / (1.0 - x0)
            v_right = x0 + (1.0 - x0) * (m * u + (1.0 - m) * torch.pow(torch.clamp(u, min=0.0), k))

            # blend left and right branches according to pivot threshold
            v = torch.where(v <= x0, v_left, v_right)

    # normalize brightness to target mean
    if brightness_target >= 0.0:
        v_mean = torch.mean(v, dim=(2, 3), keepdim=True) # [B, 1, 1, 1]
        v_mean = torch.clamp(v_mean, min=1e-5)
        v = v * (brightness_target / v_mean)

    # ensure brighness remains within valid HSV bounds
    v.clamp_(min=0.0, max=1.0)

    #--------------------------------------------

    # reconstruct HSV and convert back to requested output space
    hsv = torch.cat([h, s, v], dim=1)
    if output_color_space == "rgb":
        return kornia.color.hsv_to_rgb(hsv)
    elif output_color_space == "hsv":
        return hsv
    else:
        raise ValueError(f"Unsupported output_color_space: {output_color_space}")


def stretch_histogram(images: torch.Tensor,
                      *,
                      q_lower: float = 0.001,
                      q_upper: float = 0.999
                      ) -> torch.Tensor:
    """
    Expands the dynamic range of a batch of images by stretching the histogram.

    Args:
        images : A tensor containing a batch of images. Shape [B, C, H, W]
                    with values normalized in the range [0.0, 1.0].
        q_lower: The lower quantile to ignore (e.g., 0.001 for bottom 0.1%).
        q_upper: The upper quantile to ignore (e.g., 0.999 for top 0.1%).

    Returns:
        A tensor containing the batch of images with the dynamic range expanded.
    """
    b, c, h, w = images.shape

    # flatten H, W, C dimensions per batch image -> [B, C*H*W]
    flattened = images.view(b, -1)

    # calculate quantiles for each image independently;
    # torch.quantile returns the value at which a specific percentage of data falls;
    # dim=1 ensures independent calculation per image; reshape to [B,1,1,1] allows broadcasting
    low_vals  = torch.quantile(flattened, q_lower, dim=1, keepdim=True).view (b, 1, 1, 1)
    high_vals = torch.quantile(flattened, q_upper, dim=1, keepdim=True).view (b, 1, 1, 1)

    # calculate the range of values for each image and stretch it to [0,1]
    dynamic_range = (high_vals - low_vals).clamp(min=1e-7)
    images = (images - low_vals) / dynamic_range

    # clamp as outliers outside the quantiles will exceed the [0,1] range
    return torch.clamp(images, 0.0, 1.0)



def apply_dithering(images: torch.Tensor,
                    *,
                    amplitude_bits: float = 1.0
                    ) -> torch.Tensor:
    """
    Applies dithering to reduce banding by adding noise.

    Args:
        images        : A tensor containing a batch of images. Shape [B, C, H, W]
                        with values normalized in the range [0.0, 1.0].
        amplitude_bits: Amplitude of the noise relative to an 8-bit color step.
    Returns:

        A tensor containing the batch of images with dithering applied.
    """
    # the value of a single color step in an 8-bit space (1/255 ≈ 0.00392)
    STEP_SIZE: Final = 1.0 / 255.0

    # add uniform noise centered at zero with the desired amplitude
    noise = (torch.rand_like(images) - 0.5) * (amplitude_bits * STEP_SIZE)
    return torch.clamp(images + noise, 0.0, 1.0)


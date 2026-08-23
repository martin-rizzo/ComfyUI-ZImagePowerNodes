"""
File    : zsampler_turbo_1_advanced.py
Purpose : Node for denoising latent images with Z-Image Turbo (ZIT) using a set of custom sigmas,
          (this advanced version allows you to manually configure additional parameters)
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Feb 13, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

  ComfyUI V3 schema documentation can be found here:
  - https://docs.comfy.org/custom-nodes/v3_migration

_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
"""
from typing               import Any
from comfy_api.latest     import io
from ..widgets     import Separator
from ..core.progress_bar  import ProgressPreview
from ..core.zsampler_turbo_legacy_method import zsampler_turbo_legacy_method



class ZSamplerTurboAdvanced(io.ComfyNode):
    xTITLE         = "Z-Sampler Turbo v1 (Advanced)"
    xDESCRIPTION   = (
        'Efficiently denoises latent images, specifically tuned for the "Z-Image Turbo" model. '
        'This node takes a Z-Image Turbo model, an initial latent image, and conditioning parameters, '
        'and produces a denoised output ready for further processing or decoding.'
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
            inputs=[
                io.Model.Input       ("model",
                                      tooltip="The model used for generating the latent images.",
                                     ),
                io.Conditioning.Input("positive",
                                      tooltip="The conditioning used to guide the generation process toward the desired content.",
                                     ),
                io.Latent.Input      ("latent_input",
                                      tooltip="The initial latent image to be modified; typically an 'Empty Latent' for text-to-image or an encoded image for img2img.",
                                     ),
                io.Int.Input         ("seed", default=1, min=1, max=0xffffffffffffffff, control_after_generate=True,
                                      tooltip="The seed used for the random noise generator, ensuring the same result is produced with the same value.",
                                     ),
                io.Int.Input         ("steps", default=8, min=4, max=9, step=1,
                                      tooltip="The number of iterations to be performed during the sampling process.",
                                     ),
                io.Float.Input       ("denoise", default=1.0, min=0.00, max=1.00, step=0.01,
                                      tooltip="The amount of denoising applied, lower values will maintain the structure of the initial image allowing for image to image sampling.",
                                     ),

                Separator.Input("divider", mode="divider"),#=======================================

                io.Float.Input       ("initial_noise_calibration", default=0.00, min=0.00, max=1.00, step=0.05,
                                      tooltip="The amount of adjustment applied to the initial noise (0 means no adjustment). "
                                              "This typically enhances image contrast and saturation, "
                                              "higher values increase these effects more significantly."
                                     ),
                io.Combo.Input       ("noise_bias_estimation", default="experimental", options=["experimental", "accurate"],
                                      tooltip="Method used to estimate the bias in each channel of the initial noise. "
                                              "`experimental`: Calculate the bias by denoising a latent image with minimal noise. "
                                              "`accurate`: Calculate the bias by denoising a fully noisy latent image. "
                                     ),
                io.Combo.Input       ("noise_bias_sample_size", default="image_size", options=["image_size", "1024px", "512px", "256px"],
                                      tooltip="The size of the latent image used to calculate the bias. "
                                              "The smaller the image size, the faster the calculation of the first step. "
                                     ),
                io.Float.Input       ("noise_bias_scale", default=0.12, min=0.00, max=1.00, step=0.01,
                                      tooltip="The level of adjustament from the calculated noise bias "
                                              "to apply before the first denoising step. "
                                              "(0.0 means no bias adjustment; 1.0 means using the calculated bias).",
                                     ),
                io.Float.Input       ("noise_overdose", default=0.33, min=-1.00, max=1.00, step=0.01,
                                      tooltip="The amount of overamplitude in the initial noise generation. "
                                              "(negative values will reduce the amplitude)."
                                     ),
            ],
            outputs=[
                io.Latent.Output(display_name="latent_output", tooltip="The resulting denoised latent image, ready to be decoded by a VAE or passed to another sampler."),
            ]
        )

    #__ FUNCTION __________________________________________
    @classmethod
    def execute(cls,
                model,
                positive                 : list,
                latent_input             : dict[str, Any],
                seed                     : int,
                steps                    : int,
                denoise                  : float,
                initial_noise_calibration: float,
                noise_bias_estimation    : str,
                noise_bias_sample_size   : str | int | None,
                noise_bias_scale         : float,
                noise_overdose           : float,
                **kwargs
                ) -> io.NodeOutput:

        # create a progress bar from 0 to 100 (with progress preview)
        progress_preview = ProgressPreview.from_model( model )

        # run the legacy Z-Sampler Turbo process on the latent image
        latent_output = zsampler_turbo_legacy_method(
                                    latent_input, model, positive,
                                    seed                      = seed,
                                    steps                     = steps,
                                    denoise                   = denoise,
                                    initial_noise_calibration = initial_noise_calibration,
                                    noise_bias_estimation     = noise_bias_estimation,
                                    noise_bias_sample_size    = noise_bias_sample_size,
                                    noise_bias_scale          = noise_bias_scale,
                                    noise_overdose            = noise_overdose,
                                    progress_preview          = progress_preview,
                                    )
        return io.NodeOutput(latent_output)


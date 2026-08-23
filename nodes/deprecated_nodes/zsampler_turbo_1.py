"""
File    : zsampler_turbo_1.py
Purpose : Node for denoising latent images using a set of custom sigmas with Z-Image Turbo (ZIT)
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jan 16, 2026
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



class ZSamplerTurbo(io.ComfyNode):
    xTITLE         = "Z-Sampler Turbo v1"
    xDESCRIPTION   = (
        'Efficiently denoises the latent image, specifically tuned for the "Z-Image Turbo" model. '
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
                io.Int.Input         ("seed", default=1, min=0, max=0xffffffffffffffff, control_after_generate=True,
                                      tooltip="The seed used for the random noise generator, ensuring the same result is produced with the same value.",
                                     ),
                io.Int.Input         ("steps", default=9, min=4, max=9, step=1,
                                      tooltip="The number of iterations to be performed during the sampling process.",
                                     ),
                io.Float.Input       ("denoise", default=1.0, min=0.00, max=1.00, step=0.01,
                                      tooltip="The amount of denoising applied, lower values will maintain the structure of the initial image allowing for image to image sampling.",
                                     ),

                Separator.Input("divider", mode="divider"),#=======================================


                io.Combo.Input       ("initial_noise_calibration", default="off", options=["100%", "75%", "50%", "25%", "off"],
                                       tooltip="The amount of adjustment applied to the initial noise. "
                                               "This typically enhances image contrast and saturation, "
                                               "higher values increase these effects more significantly. "
                                     ),
                io.Boolean.Input     ("lowres_bias", default=False, label_on="yes", label_off="no",
                                      tooltip="When enabled, it use a smaller latent image to calculate the initial noise bias, "
                                              "accelerating the first step. Otherwise the full size of the input image is used. "
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
                positive    : list,
                latent_input: dict[str, Any],
                seed        : int,
                steps       : int,
                denoise     : float,
                initial_noise_calibration: str | float,
                lowres_bias              : bool,
                **kwargs
                ) -> io.NodeOutput:

        # hardcoded initial noise configuration for this node
        noise_bias_estimation = "experimental"
        noise_bias_scale      = 0.12
        noise_overdose        = 0.33

        # if the calibration level is a string with percentage format, it's converted to float
        if isinstance(initial_noise_calibration, str):
            initial_noise_calibration = initial_noise_calibration[:-1] if initial_noise_calibration[-1] == "%" else "0"
            initial_noise_calibration = float(initial_noise_calibration) / 100

        # create a progress bar from 0 to 100 (with progress preview)
        progress_preview = ProgressPreview.from_model( model )

        # run the legacy Z-Sampler Turbo process on the latent image
        latent_output = zsampler_turbo_legacy_method(latent_input, model, positive,
                                    seed                      = seed,
                                    steps                     = steps,
                                    denoise                   = denoise,
                                    initial_noise_calibration = initial_noise_calibration,
                                    noise_bias_estimation     = noise_bias_estimation,
                                    noise_bias_sample_size    = 256 if lowres_bias else "image_size",
                                    noise_bias_scale          = noise_bias_scale,
                                    noise_overdose            = noise_overdose,
                                    progress_preview          = progress_preview,
                                    )
        return io.NodeOutput(latent_output)

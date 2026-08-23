"""
File    : zsampler_turbo_2_laboratory.py
Purpose : Development node for experimenting with the `zsampler_turbo_core(..)` method.
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Mar 18, 2026
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
from typing                      import Any
from comfy_api.latest            import io
from ..widgets            import Separator
from ..core.progress_bar         import ProgressPreview
from ..core.zsampler_turbo_core  import zsampler_turbo_core


class ZSamplerTurbo2Laboratory(io.ComfyNode):
    xTITLE         = "Z-Sampler Turbo v2 (Laboratory)"
    xDESCRIPTION   = (
        'Efficiently denoises the latent image, specifically tuned for the "Z-Image Turbo" model. '
        'This node allows direct modification of internal parameters in the zsample_turbo_core(...) '
        'method, and was used during development for testing and calibration. '
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
                io.Int.Input         ("steps", default=8, min=3, max=20, step=1,
                                      tooltip="The number of iterations to be performed during the sampling process.",
                                     ),
                io.Float.Input       ("denoise", default=1.0, min=0.00, max=1.00, step=0.01,
                                      tooltip="The amount of denoising applied, lower values will maintain the structure of the initial image allowing for image to image sampling.",
                                     ),

                Separator.Input("divider1", mode="divider"),#======================================

                io.Float.Input       ("initial_noise_bias_level", default=1.0, min=0.0, max=10.0, step=0.2,
                                      tooltip="The level of adjustament from the calculated noise bias "
                                              "to apply before the first denoising step. "
                                              "(0.0 means no noise bias adjustment; 1.0 means using the calculated noise bias).",
                                     ),
                io.Float.Input       ("initial_noise_overdose", default=0.2, min=-1.0, max=1.0, step=0.1,
                                      tooltip="The amount of over-amplitude in the initial noise generation. "
                                              "(negative values ​​will reduce any excessive amplitude)."
                                     ),
                io.Combo.Input       ("noise_est_sample_size", default="image_size", options=["image_size", "1024px", "512px", "256px"],
                                      tooltip="The size of the latent image used to calculate the initial noise. "
                                              "The smaller the image size, the faster the calculation of the first step. "
                                     ),

                Separator.Input("divider2", mode="divider"),#======================================

                io.Int.Input         ("extra_noise_freq1", default=32, min=0, max=1024,
                                      tooltip="The frequency at which extra noise is injected into the latent during "
                                              "the first stage. A value of 1024 means noise in injected into every "
                                              "pixel, a value of 512 means noise is injected every second pixel, with "
                                              "intermediate pixels being interpolated. ",
                                     ),
                io.Float.Input       ("extra_noise_scale1", default=7.5, min=0.0, max=50.0, step=0.1,
                                      tooltip="The amount of noise to be injected into the latent image during the "
                                              "first stage. A value of 0 means that no noise will be injected. ",
                                     ),
                io.Int.Input         ("extra_noise_freq2", default=64, min=0, max=1024,
                                      tooltip="The frequency at which extra noise is injected into the latent during "
                                              "the second stage. A value of 1024 means noise in injected into every "
                                              "pixel, a value of 512 means noise is injected every second pixel, with "
                                              "intermediate pixels being interpolated. ",
                                     ),
                io.Float.Input       ("extra_noise_scale2", default=3.7, min=0.0, max=50.0, step=0.1,
                                      tooltip="The amount of noise to be injected into the latent image during the "
                                              "second stage. A value of 0 means that no noise will be injected. ",
                                     ),
                io.Int.Input         ("extra_noise_freq3", default=512, min=0, max=1024,
                                      tooltip="The frequency at which extra noise is injected into the latent during "
                                              "the third stage. A value of 1024 means noise in injected into every "
                                              "pixel, a value of 512 means noise is injected every second pixel, with "
                                              "intermediate pixels being interpolated. ",
                                     ),
                io.Float.Input       ("extra_noise_scale3", default=1.0, min=0.0, max=50.0, step=0.1,
                                      tooltip="The amount of noise to be injected into the latent image during the "
                                              "third stage. A value of 0 means that no noise will be injected. ",
                                     ),

                Separator.Input("divider3", mode="divider"),#======================================

                io.Int.Input         ("scramble_left_count", default=0, min=-16, max=16,
                                      tooltip="Number of times to scramble the latent image with left side fragments. "
                                              "A value of 0 means no scrambling will be done, while negative values "
                                              "enable random flipping."
                                     ),
                io.Int.Input         ("scramble_top_count", default=0, min=-16, max=16,
                                      tooltip="Number of times to scramble the latent image with top side fragments. "
                                              "A value of 0 means no scrambling will be done, while negative values "
                                              "enable random flipping."
                                     ),
                io.Int.Input         ("scramble_right_count", default=0, min=-16, max=16,
                                      tooltip="Number of times to scramble the latent image with right side fragments. "
                                              "A value of 0 means no scrambling will be done, while negative values "
                                              "enable random flipping."
                                     ),
                io.Int.Input         ("scramble_bottom_count", default=0, min=-16, max=16,
                                      tooltip="Number of times to scramble the latent image with bottom side fragments. "
                                              "A value of 0 means no scrambling will be done, while negative values "
                                              "enable random flipping."
                                     ),
                io.Int.Input         ("stage2_preproc_steps", default=0, min=0, max=3,
                                      tooltip="Number of extra steps to perform as pre-processing in the second stage, "
                                              "this can improve coherence and reduce hallucination. "
                                     ),

                Separator.Input("divider4", mode="divider"),#======================================

                io.Combo.Input       ("sigma_preset_name", default="bravo", options=["alpha", "bravo", "charlie"],
                                      tooltip="The set of predefined sigma values that are used during the denoise process. "
                                     ),
                io.Float.Input       ("sigma1_off", default=0.000, min=-1.000, max=1.000, step=0.001,
                                      tooltip="Offset that will be applied to the value of sigma1. ",
                                     ),
                io.Float.Input       ("sigma2_off", default=0.000, min=-1.000, max=1.000, step=0.001,
                                      tooltip="Offset that will be applied to the value of sigma2. ",
                                     ),
                io.Float.Input       ("sigma3_off", default=0.000, min=-1.000, max=1.000, step=0.001,
                                      tooltip="Offset that will be applied to the value of sigma3. ",
                                     ),
                io.Float.Input       ("sigma4_off", default=0.000, min=-1.000, max=1.000, step=0.001,
                                      tooltip="Offset that will be applied to the value of sigma4. ",
                                     ),
                io.Float.Input       ("sigma5_off", default=0.000, min=-1.000, max=1.000, step=0.001,
                                      tooltip="Offset that will be applied to the value of sigma5. ",
                                     ),
                io.Float.Input       ("sigma6_off", default=0.000, min=-1.000, max=1.000, step=0.001,
                                      tooltip="Offset that will be applied to the value of sigma6. ",
                                     ),
                io.Float.Input       ("sigma7_off", default=0.000, min=-1.000, max=1.000, step=0.001,
                                      tooltip="Offset that will be applied to the value of sigma7. ",
                                     ),
                io.Float.Input       ("sigma8_off", default=0.000, min=-1.000, max=1.000, step=0.001,
                                      tooltip="Offset that will be applied to the value of sigma8. ",
                                     ),
                io.Float.Input       ("sigma9_off", default=0.000, min=-1.000, max=1.000, step=0.001,
                                      tooltip="Offset that will be applied to the value of sigma9. ",
                                     ),
                io.Float.Input       ("sigma10_off", default=0.000, min=-1.000, max=1.000, step=0.001,
                                      tooltip="Offset that will be applied to the value of sigma10. ",
                                     ),
            ],
            outputs=[
                io.Latent.Output(display_name="latent_output",
                                 tooltip="The resulting denoised latent image, ready for decoding "
                                         "by a VAE or passed to another node for further processing. "
                                ),
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
                noise_est_sample_size    : str | int | None,
                initial_noise_bias_level : float,
                initial_noise_overdose   : float,
                extra_noise_freq1        : int,
                extra_noise_scale1       : float,
                extra_noise_freq2        : int,
                extra_noise_scale2       : float,
                extra_noise_freq3        : int,
                extra_noise_scale3       : float,
                scramble_left_count       : int,
                scramble_top_count        : int,
                scramble_right_count      : int,
                scramble_bottom_count     : int,
                stage2_preproc_steps     : int,
                sigma_preset_name        : str,
                sigma1_off               : float,
                sigma2_off               : float,
                sigma3_off               : float,
                sigma4_off               : float,
                sigma5_off               : float,
                sigma6_off               : float,
                sigma7_off               : float,
                sigma8_off               : float,
                sigma9_off               : float,
                sigma10_off              : float,
                **kwargs
                ) -> io.NodeOutput:

        # sets sigma limits when denoise is less than 1.0 (mostly when performing inpainting)
        sigma_limits = ( denoise**0.5 , 0 ) if denoise < 0.999 else None

        # creates a list of sigma offsets
        sigma_offsets = [sigma1_off, sigma2_off, sigma3_off, sigma4_off, sigma5_off, sigma6_off, sigma7_off, sigma8_off, sigma9_off, sigma10_off]

        # creates a list of noise frequencies and scales for injected noise
        # with values for each of the three stages
        extra_noise_freqs  = ( extra_noise_freq1 , extra_noise_freq2 , extra_noise_freq3  )
        extra_noise_scales = ( extra_noise_scale1, extra_noise_scale2, extra_noise_scale3 )

        # creates a list of counts for image scrambling before the sampler's "stage2"
        stage2_scramble_counts = (scramble_left_count, scramble_top_count, scramble_right_count, scramble_bottom_count)

        # run the Z-Sampler Turbo core method on the latent image
        latent_output = zsampler_turbo_core(latent_input, model, positive,
                                            seed                      = seed,
                                            steps                     = steps,
                                            initial_noise_bias_level  = initial_noise_bias_level,
                                            initial_noise_overdose    = initial_noise_overdose,
                                            noise_est_sample_size     = noise_est_sample_size,
                                            sigma_preset_name         = sigma_preset_name,
                                            sigma_offsets             = sigma_offsets,
                                            sigma_limits              = sigma_limits,
                                            stage2_scramble           = True,
                                            stage2_scramble_counts    = stage2_scramble_counts,
                                            stage2_preproc_steps      = stage2_preproc_steps,
                                            extra_noise_freqs         = extra_noise_freqs,
                                            extra_noise_scales        = extra_noise_scales,
                                            progress_preview = ProgressPreview.from_model( model ),
                                            )

        return io.NodeOutput(latent_output)

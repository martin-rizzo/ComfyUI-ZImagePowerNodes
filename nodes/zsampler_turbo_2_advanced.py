"""
File    : zsampler_turbo_2_advanced.py
Purpose : Node for denoising latent images using "Z-Sampler Turbo" (second generation)
          (this advanced version allows you to manually configure additional parameters)
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Mar 20, 2026
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
from typing                     import Any
from comfy_api.latest           import io
from .                          import widgets as zi
from .core.progress_bar         import ProgressPreview
from .core.zsampler_turbo_core  import zsampler_turbo_core
TURBO_CREATIVITY = {
    "off"              : (False, 0),
    "scrambled"        : (True , 0),
    "refined (1-step)" : (True , 1),
    "refined (2-steps)": (True , 2),
    "refined (3-steps)": (True , 3),
   #"only refining"    : (False, 1),
}



class ZSamplerTurbo2Advanced(io.ComfyNode):
    xTITLE         = "Z-Sampler Turbo v2 (Advanced)"
    xDESCRIPTION   = (
        'Efficiently denoises the latent image using a process specifically tuned for the "Z-Image Turbo". '
        'This node takes a Z-Image Turbo model, an initial latent image, and conditioning parameters, and '
        'produces a denoised latent output ready for decoding into the final image. This advanced version '
        'includes extra parameters for more precise control and chaining of samplers.'
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
                io.Latent.Input      ("latent_input",
                                      tooltip="The initial latent image to be denoised; usually an 'Empty Latent' for "
                                              "text-to-image tasks or an encoded image for image-to-image processing. ",
                                     ),
                io.Model.Input       ("model",
                                      tooltip="The Z-Image Turbo model used for denoising the latent image. "
                                     ),
                io.Conditioning.Input("positive",
                                      tooltip="The main prompt/conditioning used to guide the generation process "
                                              "toward the desired content. ",
                                     ),
                io.Conditioning.Input("positive_stg2",
                                      optional=True,
                                      tooltip="This input is optional and can remain disconennect. It allows "
                                              "specifying a different prompt/conditioning for the second stage "
                                              "of the denoising process. ",
                                     ),
                io.Conditioning.Input("positive_stg3",
                                      optional=True,
                                      tooltip="This input is optional and can remain disconennect. It allows "
                                              "specifying a different prompt/conditioning for the third stage "
                                              "of the denoising process. ",
                                     ),
                io.Boolean.Input     ("add_noise",
                                      default=True, label_on="yes", label_off="no",
                                      tooltip="Determines whether to add initial noise to the latent image. Recommended "
                                              "for most cases. Disabling this is useful for sampler chaining when the "
                                              "input latent already contains residual noise from a previous process. ",
                                     ),
                io.Int.Input         ("seed",
                                      default=1, min=1, max=0xffffffffffffffff, control_after_generate=True,
                                      tooltip="The seed used for the random noise generator, ensuring the same result "
                                              "is produced with the same value.",
                                     ),
                io.Int.Input         ("steps",
                                      default=8, min=3, max=20, step=1,
                                      tooltip="Number of iterations to perform during the denoising process.",
                                     ),
                io.Int.Input         ("start_at_step", default=0, min=0, max=100, step=1,
                                      tooltip="The step at which the sampling process should start, allowing for "
                                              "more precise control over the denoising process and enabling sampler "
                                              "chaining. ",
                                      ),
                io.Int.Input         ("end_at_step", default=100, min=0, max=100, step=1,
                                      tooltip="The step at which the sampling process should end. allowing for "
                                              "more precise control over the denoising process and enabling sampler "
                                              "chaining. ",
                                     ),
                io.Boolean.Input     ("force_final_denoising", default=True, label_on="yes", label_off="no",
                                      tooltip="Determines whether to force a full final denoising step, resulting "
                                              "in a output latent with no residual noise. Recommended for most cases. "
                                              "Disabling this is useful when residual noise is required for the next "
                                              "process in a sampler chain. ",
                                     ),

                zi.Separator.Input("divider", mode="divider"),#====================================

                io.Combo.Input       ("initial_sample_size",
                                      default="full_size",
                                      options=["256px", "512px", "full_size"],
                                      tooltip="The latent image size used for calculating the initial noise for "
                                              "intensity correction. While smaller sizes result in a faster first "
                                              "step, they can lead to a less accurate correction",
                                     ),

                zi.Separator.Input("divider2", mode="divider"),#===================================

                io.Float.Input       ("intensity",
                                      default=0.0, min=-1.0, max=1.0, step=0.1,
                                     tooltip="Initial noise amplitude used to enhance contrast and colors. A value "
                                             "of 0.0 is neutral; negative values create more muted images, while "
                                             "positive values increase contrast and saturation. This only takes "
                                             "effect when 'denoise' is set to 1.00 ",
                                     ),
                io.Float.Input       ("intensity_bias",
                                      default=0.0, min=-1.0, max=1.0, step=0.1,
                                      tooltip="Custom adjustment for the intensity noise bias. Usually kept at 0.0; "
                                              "used to fine-tune 'brightness'. Note that its effect depends heavily "
                                              "on the prompt and image style, so it may not always act as a simple "
                                              "brightness control. Adjust it within the positive or negative range "
                                              "until it seems right to you. ",
                                     ),
                io.Combo.Input       ("turbo_creativity",
                                      default="off", options=list(TURBO_CREATIVITY.keys()),
                                      tooltip="Boosts model creativity for more diverse compositions while maintaining "
                                              "the general style. Be aware that this can lead to hallucinations and "
                                              "isn't recommended for inpainting tasks. The refined options add extra "
                                              "steps to try to correct the hallucinations and bring coherence to the "
                                              "image ",
                                     ),
            ],
            outputs=[
                io.Latent.Output(display_name="latent_output",
                                 tooltip="The resulting denoised latent image, ready to be decoded "
                                         "by a VAE or passed to another node for further processing. ",
                                )
            ]
        )

    #__ FUNCTION __________________________________________
    @classmethod
    def execute(cls,
                latent_input          : dict[str, Any],
                model                 : Any,
                positive              : list,
                add_noise             : bool,
                seed                  : int,
                steps                 : int,
                start_at_step         : int,
                end_at_step           : int,
                force_final_denoising : bool,
                intensity             : float,
                intensity_bias        : float,
                initial_sample_size   : str,
                turbo_creativity      : str,
                *,
                positive_stg2         : list | None = None,
                positive_stg3         : list | None = None,
                **kwargs
                ) -> io.NodeOutput:

        # if the start/stop values restrict the number of steps,
        # apply that start/stop range using the `sigma_step_range` parameter
        sigma_step_range = None
        if start_at_step > 0 or end_at_step<steps:
            sigma_step_range = (start_at_step, end_at_step)

        # `intensity` determines the level of noise overdose and noise bias
        initial_noise_overdose   = (intensity-1.0) * 0.4
        initial_noise_bias_level = intensity*4-1
        initial_noise_bias_level = min(max(initial_noise_bias_level, 0.0), 4.0)

        # apply user-defined adjustment to the calculated noise bias level
        initial_noise_bias_level += 10 * intensity_bias
        initial_noise_bias_level = min(max(initial_noise_bias_level, -5.0), 14.0)

        # `turbo_creativity` triggers the scramble of the image in stage2 and
        # it also controls how many sampling steps are taken to achieve coherence
        stage2_scramble, stage2_preproc_steps = TURBO_CREATIVITY.get(turbo_creativity, (False,0))

        # little hack to determine the influence of stage 2 prompt when there are
        # separate prompts for stages 1 and 2 and "turbo creativity refined" is enabled:
        #
        #  - If `positive_stg3` is disconnected, it's considered weak stage 2 conditioning,
        #    and the pre-processing for stage 2 uses the prompt from STAGE-1
        #  - If `positive_stg3` is connected to stage2, it's considered strong stage 2 conditioning,
        #    and the pre-processing for stage 2 uses the prompt from STAGE-2.
        #
        strong_positive_stg2 = (positive_stg3 is not None)
        positive_stg2_preproc = positive_stg2 if strong_positive_stg2 else positive

        # run the Z-Sampler Turbo core method on the latent image
        latent_output = zsampler_turbo_core(latent_input, model, positive,
                                            seed                      = seed,
                                            steps                     = steps,
                                            initial_noise_bias_level  = initial_noise_bias_level,
                                            initial_noise_overdose    = initial_noise_overdose,
                                            noise_est_sample_size     = initial_sample_size,
                                            sigma_preset_name         = "bravo",
                                            sigma_step_range          = sigma_step_range,
                                            start_with_noise          = add_noise,
                                            end_with_denoise          = force_final_denoising,
                                            positive_stg2_preproc     = positive_stg2_preproc,
                                            positive_stg2             = positive_stg2,
                                            positive_stg3             = positive_stg3,
                                            stage2_scramble           = stage2_scramble,
                                            stage2_preproc_steps      = stage2_preproc_steps,
                                            progress_preview = ProgressPreview.from_model( model ),
                                            )

        return io.NodeOutput(latent_output)


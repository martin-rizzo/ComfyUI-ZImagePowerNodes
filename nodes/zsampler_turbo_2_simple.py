"""
File    : zsampler_turbo_simple.py
Purpose : Simplified node for denoising latent images with "Z-Sampler Turbo" (second generation)
          Designed for quick test image variations with a pair of simple parameters.
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Apr 24, 2026
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
from typing                    import Any
from comfy_api.latest          import io
from .                         import widgets as zi
from .core.progress_bar        import ProgressPreview
from .core.zsampler_turbo_core import zsampler_turbo_core



class ZSamplerTurbo2Simple(io.ComfyNode):
    xTITLE         = "Z-Sampler Turbo v2 (Simple)"
    xDESCRIPTION   = (
        'Simplified version of Z-Sampler Turbo (second generation), offering a streamlined interface '
        'for quick and easy use while retaining all of its features and capabilities. It takes a '
        'Z-Image Turbo model, an initial latent image, and prompt/conditioning to produce a denoised '
        'latent output, which can then be decoded into the final image.'
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
                                      tooltip="This input is optional and can remain disconnected. It allows "
                                              "specifying a different prompt/conditioning for the second stage "
                                              "of the denoising process. ",
                                     ),
                io.Conditioning.Input("positive_stg3",
                                      optional=True,
                                      tooltip="This input is optional and can remain disconnected. It allows "
                                              "specifying a different prompt/conditioning for the third stage "
                                              "of the denoising process. ",
                                     ),
                io.Int.Input         ("seed",
                                      default=1, min=1, max=0xffffffffffffffff, control_after_generate=True,
                                      tooltip="The seed used for the random noise generator, ensuring the same "
                                              "result is produced with the same value. ",
                                     ),
                io.Int.Input         ("steps",
                                      default=8, min=3, max=20, step=1,
                                      tooltip="Number of iterations to perform during the denoising process.",
                                     ),
                io.Float.Input       ("ibias",
                                      default=0.0, min=-1.0, max=1.0, step=0.2,
                                      tooltip="Custom adjustment for the intensity noise bias. Usually kept at 0.0; "
                                              "used to fine-tune 'brightness'. Note that its effect depends heavily "
                                              "on the prompt and image style, so it may not always act as a simple "
                                              "brightness control. Adjust it within the positive or negative range "
                                              "until it seems right to you. ",
                                     ),

                zi.Separator.Input("divider", mode="divider"),#====================================

                io.Boolean.Input     ("turbo_creativity",
                                      default=False, label_on="yes", label_off="no",
                                      tooltip="Enables turbo creativity. This scrambles the image to boost diversity "
                                              "in compositions while maintaining the general style and tone color. "
                                              "Be aware that this may lead to hallucinations. ",
                                     ),
                io.Boolean.Input     ("old_scheduler",
                                      default=False, label_on="yes", label_off="no",
                                      tooltip="Enables the legacy scheduler with a different set of sigmas. Although "
                                              "the new scheduler is optimized for general quality, this old version "
                                              "may produce better results in specific cases. ",
                                     ),
                io.Boolean.Input     ("noise_injection",
                                      default=False, label_on="yes", label_off="no",
                                      tooltip="Enables noise injection in the final stage. This can enhance fine "
                                              "details and realism, but may also generate artificial-looking color "
                                              "spots in smooth areas. ",
                                     ),
                io.Boolean.Input     ("alternative_refiner",
                                      default=False, label_on="yes", label_off="no",
                                      tooltip="Enables an alternative refiner using the DPM++ SDE sampler during the "
                                              "final stage. This enhances contrast and sharpness in fine details but "
                                              "increases overall processing time. ",
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
                latent_input         : dict[str, Any],
                model                : Any,
                positive             : list,
                seed                 : int,
                steps                : int,
                ibias                : float,
                turbo_creativity     : bool,
                old_scheduler        : bool,
                noise_injection      : bool,
                alternative_refiner  : bool,
                *,
                positive_stg2 : list | None = None,
                positive_stg3 : list | None = None,
                intensity     : float       = 0.5,
                denoise       : float       = 1.0,
                **kwargs
                ) -> io.NodeOutput:
        # set sigma limits when denoise is less than 1.0, typically used for inpainting
        sigma_limits = ( denoise**0.5 , 0 ) if denoise < 0.999 else None

        # `intensity` determines the level of noise overdose and noise bias
        # (intensity is hardcoded to 0.5 in this node)
        initial_noise_overdose   = intensity * 0.4                              #< overdose   = 0.2
        initial_noise_bias_level = (intensity+1)*4-1                            # = 5.0
        initial_noise_bias_level = min(max(initial_noise_bias_level, 0.0), 4.0) #< bias_level = 4.0

        # apply user-defined adjustment `ibias` to the calculated noise bias level
        initial_noise_bias_level += 10 * ibias
        initial_noise_bias_level = min(max(initial_noise_bias_level, -6.0), 14.0)

        # noise injection
        inject_noise_freqs  = None
        inject_noise_scales = None
        if noise_injection:
            inject_noise_freqs  = (  0,   0, 1024, 896, 448)
            inject_noise_scales = (0.0, 0.0,  0.7, 1.5, 1.0)

        # turbo_creativity enables stage2 scrambling + coherence step
        stage2_scramble       = False
        stage2_keep_coherence = False
        if turbo_creativity:
            # when the seed is a multiple of 3, turbo_creativity disables the
            # coherence pre-processing step that keeps coherence; this increases
            # hallucinations but also enhances creativity
            high_as_a_kite        = (seed % 3) == 0
            stage2_scramble       = True
            stage2_keep_coherence = False if high_as_a_kite else True

        # little hack to determine the influence of stage 2 prompt when there are
        # separate prompts for stages 1 and 2 and "turbo creativity + refined" is enabled:
        #
        #  - If `positive_stg3` is disconnected, it's considered weak stage 2 conditioning,
        #    and the coherence pre-processing for stage 2 uses the prompt from STAGE-1
        #  - If `positive_stg3` is connected, it's considered strong stage 2 conditioning,
        #    and the coherence pre-processing for stage 2 uses the prompt from STAGE-2.
        #
        weak_stg2_prompt_influence = (positive_stg3 is None)


        # run the Z-Sampler Turbo core method on the latent image
        latent_output = zsampler_turbo_core(
            latent_input,
            model,
            positive,
            seed          = seed,
            steps         = steps,
            initial_noise_bias_level  = initial_noise_bias_level,
            initial_noise_overdose    = initial_noise_overdose,
            noise_est_sample_size     = "full_size",
            sigma_preset_name         = "bravo" if not old_scheduler else "alpha",
            sigma_limits              = sigma_limits,
            positive_stg2_preproc     = positive if weak_stg2_prompt_influence else positive_stg2,
            positive_stg2             = positive_stg2,
            positive_stg3             = positive_stg3,
            stage2_scramble           = stage2_scramble,
            stage2_preproc_steps      = 1 if stage2_keep_coherence else 0,
            extra_noise_freqs         = inject_noise_freqs,
            extra_noise_scales        = inject_noise_scales,
            samplers             = ("euler", "euler",  "euler" if not alternative_refiner else "dpmpp_sde"),
            progress_preview = ProgressPreview.from_model(model),
        )

        return io.NodeOutput(latent_output)

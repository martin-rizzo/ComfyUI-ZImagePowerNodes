"""
File    : zsampler_turbo_X21.py
Purpose : Experimental version node for denoising latent images with "Z-Sampler Turbo" (second/third Gen).
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jun 6, 2026
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
from typing                        import Any
from comfy_api.latest              import io
from .custom_widgets               import Separator
from .core.progress_bar            import ProgressPreview
from .core.zsampler_turbo_core     import zsampler_turbo_core
from .core.zsampler_turbo_corehelp import EulerAss, DPMPP_SDEss
from .custom_widgets               import Separator
_SPECTRAL_TILTS_BY_NAME = {
    "none"       : (   "", ( 0.0,  0.0), 1.0),
    "stage3_H"   : (  "3", (-0.3, -0.3), 1.0),
    "stages12x_H": ("12x", ( 0.2, -0.9), 0.7),
    "stages12x_l": ("12x", ( 0.2, -2.0), 0.8),
    "stages123_H": ("123", ( 0.2, -0.9), 0.7),
}


class ZSamplerTurboX21(io.ComfyNode):
    xTITLE         = "Z-Sampler Turbo ^G2.1"
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
                "Experimental new version of Z-Sampler Turbo. It takes a Z-Image Turbo model, "
                "an initial latent image, and prompt/conditioning to produce a denoised latent "
                "output, which can then be decoded into the final image. "
                "Because this node is experimental, its parameters, behaviour, or existence "
                "may change or be removed entirely without prior notice. "
            ),
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
                io.Combo.Input       ("spectral_tilt",
                                      options=cls.spectral_tilts(),
                                      tooltip=""
                                     ),

                Separator.Input("divider1", mode="divider"),#======================================

                io.Boolean.Input     ("turbo_creativity",
                                      default=False, label_on="yes", label_off="no",
                                      tooltip="Enables turbo creativity. This scrambles the image to boost diversity "
                                              "in compositions while maintaining the general style and tone color. "
                                              "Be aware that this may lead to hallucinations. ",
                                     ),
                io.Boolean.Input     ("alternative_refiner",
                                      default=False, label_on="yes", label_off="no",
                                      tooltip="Enables an alternative refiner using the DPM++ SDE sampler during the "
                                              "final stage. This enhances contrast and sharpness in fine details but "
                                              "increases overall processing time. ",
                                     ),
                io.Boolean.Input     ("disable_ibias",
                                      default=False, label_on="yes", label_off="no",
                                      tooltip="Disables the custom adjustment for the intensity noise bias (ibias). "
                                              "When this option is selected, the ibias parameter is ignored and not "
                                              "calculated during the denoising process, saving a computation step. "
                                     ),
                io.Boolean.Input     ("old_scheduler",
                                      default=False, label_on="yes", label_off="no",
                                      tooltip="Enables the legacy scheduler with a different set of sigmas. Although "
                                              "the new scheduler is optimized for general quality, this old version "
                                              "may produce better results in specific cases. ",
                                     ),
            ],
            outputs=[
                io.Latent.Output(display_name="latent_output",
                                 tooltip="The resulting denoised latent image, ready for decoding "
                                         "by a VAE or passed to another node for further processing. "
                                ),
                io.Float.Output(display_name="pid_sigma",
                                 tooltip="The input sigma of the final denoising step. "
                                        "Connect to Merserk PiD Decode's sigma socket for a "
                                        "direct latent-to-image PiD decode. Also embedded in "
                                        "the latent dict as 'pid_sigma' for auto-passthrough. "
                               ),
            ]
        )

    #__ FUNCTION __________________________________________
    @classmethod
    def execute(cls,
                latent_input          : dict[str, Any],
                model                 : Any,
                positive              : list,
                seed                  : int,
                steps                 : int,
                ibias                 : float,
                spectral_tilt         : str,
                turbo_creativity      : bool,
                alternative_refiner   : bool,
                disable_ibias         : bool,
                old_scheduler         : bool,
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

        # define samplers for each stage;
        # when "Spectral Tilt" is enabled, a custom sampler is used (EulerAss)
        stilt_stages, alpha_tilting, spectral_tilt_sharpness = _SPECTRAL_TILTS_BY_NAME[spectral_tilt]
        samplers: list[str|object] = [ "euler" , "euler", "euler" ]
        if "1" in stilt_stages: samplers[0] = EulerAss(alpha_tilting, alpha_sharpness=spectral_tilt_sharpness)
        if "2" in stilt_stages: samplers[1] = EulerAss(alpha_tilting, alpha_sharpness=spectral_tilt_sharpness)
        if "3" in stilt_stages: samplers[2] = EulerAss(alpha_tilting, alpha_sharpness=spectral_tilt_sharpness)

        # if alternative refiner is selected -> set "dpmpp_sde" as the sampler for stage 3;
        # when "Spectral Tilt" is enabled, a custom sampler is used (DPMPP_SDEss)
        if alternative_refiner:
            samplers[2] = "dpmpp_sde"
            if "3" in spectral_tilt:
                samplers[2] = DPMPP_SDEss(alpha_tilting, alpha_sharpness=spectral_tilt_sharpness)

        # run the Z-Sampler Turbo core method on the latent image
        latent_output = zsampler_turbo_core(
            latent_input,
            model,
            positive,
            seed  = seed,
            steps = steps,
            initial_noise_bias_level = initial_noise_bias_level if not disable_ibias else 0,
            initial_noise_overdose   = initial_noise_overdose,
            noise_est_sample_size    = "full_size",
            sigma_preset_name        = "bravo" if not old_scheduler else "alpha",
            sigma_limits             = sigma_limits,
            positive_stg2_preproc    = positive if weak_stg2_prompt_influence else positive_stg2,
            positive_stg2            = positive_stg2,
            positive_stg3            = positive_stg3,
            stage2_scramble          = stage2_scramble,
            stage2_preproc_steps     = 1 if stage2_keep_coherence else 0,
            samplers                 = (*samplers,),
            progress_preview = ProgressPreview.from_model(model),
        )
        pid_sigma = latent_output.get("pid_sigma", 0.0)
        return io.NodeOutput(latent_output, pid_sigma)


    #__ internal functions ________________________________

    @staticmethod
    def spectral_tilts() -> list[str]:
        return list( _SPECTRAL_TILTS_BY_NAME.keys() )

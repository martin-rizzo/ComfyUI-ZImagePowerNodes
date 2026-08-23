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
from .                             import widgets as zi
from .core.progress_bar            import ProgressPreview
from .core.zsampler_turbo_core     import zsampler_turbo_core
from .core.zsampler_turbo_corehelp import EulerAss, DPMPP_SDEss
_SPECTRAL_TILTS_BY_NAME = {
    "none"       : (   "", ( 0.0,  0.0), 1.0),
    "stage3_H"   : (  "3", (-0.3, -0.3), 1.0),
    "stages12x_H": ("12x", ( 0.2, -0.9), 0.7),
    "stages12x_l": ("12x", ( 0.2, -2.0), 0.8),
    "stages123_H": ("123", ( 0.2, -0.9), 0.7),
}
_SAMPLING_SCALES_BY_NAME = {
    "none"       : (1.00, 1.00, 1.00),
    "max_speed"  : (0.25, 0.50, 0.75),
    "max_quality": (0.50, 0.75, 1.00),
}


class ZSamplerTurboX21(io.ComfyNode):
    xTITLE         = "Z-Sampler Turbo ^X2.1"
    xDESCRIPTION   = (
        "Experimental new version of Z-Sampler Turbo. It takes a Z-Image Turbo model, "
        "an initial latent image, and prompt/conditioning to produce a denoised latent "
        "output, which can then be decoded into the final image. "
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

                zi.Separator.Input("divider1", mode="divider"),#===================================

                io.Int.Input         ("steps",
                                      default=8, min=2, max=14, step=1,
                                      tooltip="Number of iterations to perform during the denoising process.",
                                     ),
                io.Float.Input       ("initial_bias",
                                      default=0.0, min=-0.5, max=0.5, step=0.1, round=0.1,
                                      tooltip="Custom adjustment for initial noise bias, usually kept at 0.0; "
                                              "Positive values amplify dominant prompt features (e.g., making bright "
                                              "scenes brighter or dark scenes darker), while negative values temper "
                                              "them. Keep in mind it reacts differently to every prompt, it's not a "
                                              "simple brightness control. ",
                                     ),
                io.Combo.Input       ("latent_scaling",
                                      options=cls.sampling_scales(),
                                      tooltip="Determines the resolution scale applied to latents during each "
                                              "sampling stage. 'Max Speed' uses lower internal scaling for faster "
                                              "generation, while 'Max Quality' employs higher scaling to preserve "
                                              "finer details and structural integrity at the cost of processing time. "
                                     ),
                io.Combo.Input       ("spectral_tilt",
                                      options=cls.spectral_tilts(),
                                      tooltip="Applies a frequency-based bias to the noise across sampling stages. "
                                              "Early stages amplify low-frequency noise to establish composition, "
                                              "while later stages shift focus to high-frequency components to sharpen "
                                              "fine details. Each preset defines which stages (1, 2, or 3) receive "
                                              "this spectral modification and the intensity of the adjustment. "
                                     ),
                io.Boolean.Input     ("turbo_creativity",
                                      default=False,
                                      tooltip="Enables turbo creativity. This scrambles the image to boost diversity "
                                              "in compositions while maintaining the general style and tone color. "
                                              "Be aware that this may lead to hallucinations. ",
                                     ),
                io.Boolean.Input     ("detailed_refiner",
                                      default=True,
                                      tooltip="Enables an alternative refiner using the DPM++ SDE sampler during the "
                                              "final stage. This enhances contrast and sharpness in fine details but "
                                              "increases overall processing time. ",
                                     ),
                io.Boolean.Input     ("new_scheduler",
                                      default=True,
                                      tooltip="Enables the optimized scheduler with an updated set of sigmas for superior "
                                              "general quality. Disabling this switches back to the legacy version, which "
                                              "may still perform better in specific edge cases.",
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
                latent_input    : dict[str, Any],
                model           : Any,
                positive        : list,
                seed            : int,
                steps           : int,
                initial_bias    : float,
                latent_scaling  : str,
                spectral_tilt   : str,
                turbo_creativity: bool,
                detailed_refiner: bool,
                new_scheduler   : bool,
                *,
                positive_stg2 : list | None = None,
                positive_stg3 : list | None = None,
                denoise       : float       = 1.0,
                **kwargs
                ) -> io.NodeOutput:
        # round the float inputs to a single decimal place
        initial_bias = round(initial_bias, 1)

        # set sigma limits when denoise is less than 1.0, typically used for inpainting
        sigma_limits = ( denoise**0.5 , 0 ) if denoise < 0.999 else None

        # configure the perturbation of the initial noise
        initial_noise_overdose   = 0.2  # (intensity * 0.4) with intensity fixed at 0.5
        initial_noise_bias_level = min(max(20 * initial_bias, -10.0), 10.0)

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

        # if the 'detailed refiner' is selected -> switch stage 3 to "dpmpp_sde".
        # if "Spectral Tilt" is also enabled for stage 3, use the custom "DPMPP_SDEss" sampler instead.
        if detailed_refiner:
            samplers[2] = "dpmpp_sde"
            if "3" in spectral_tilt:
                samplers[2] = DPMPP_SDEss(alpha_tilting, alpha_sharpness=spectral_tilt_sharpness)

        # resolve the latent size scale for each stage:
        #  scales[0] -> scale used during the initial (and optional) noise estimation
        #  scales[1] -> scale used during the first stage
        #  scales[2] -> scale used during the second stage
        latent_sample_scales = _SAMPLING_SCALES_BY_NAME.get(latent_scaling)

        # run the Z-Sampler Turbo core method on the latent image
        latent_output = zsampler_turbo_core(
            latent_input,
            model,
            positive,
            seed  = seed,
            steps = steps,
            initial_noise_bias_level = initial_noise_bias_level,
            initial_noise_overdose   = initial_noise_overdose,
            latent_sample_scales     = latent_sample_scales,
            sigma_preset_name        = "bravo" if new_scheduler else "alpha",
            sigma_limits             = sigma_limits,
            positive_stg2_preproc    = positive if weak_stg2_prompt_influence else positive_stg2,
            positive_stg2            = positive_stg2,
            positive_stg3            = positive_stg3,
            stage2_scramble          = stage2_scramble,
            stage2_preproc_steps     = 1 if stage2_keep_coherence else 0,
            samplers                 = (*samplers,),
            progress_preview = ProgressPreview.from_model(model),
        )

        return io.NodeOutput(latent_output)


    #__ internal functions ________________________________

    @staticmethod
    def spectral_tilts() -> list[str]:
        return list( _SPECTRAL_TILTS_BY_NAME.keys() )

    @staticmethod
    def sampling_scales() -> list[str]:
        return list( _SAMPLING_SCALES_BY_NAME.keys() )

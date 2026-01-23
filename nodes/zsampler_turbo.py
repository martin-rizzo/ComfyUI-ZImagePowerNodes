"""
File    : zsampler_turbo.py
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
import torch
import numpy as np
import comfy.utils
import comfy.sample
import comfy.samplers
from typing             import Any
from comfy_api.latest   import io
from .core.system       import logger
from .core.progress_bar import ProgressPreview


class ZSamplerTurbo(io.ComfyNode):
    xTITLE         = "ZSampler Turbo"
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
                'Efficiently denoises the latent image, specifically tuned for the "Z-Image Turbo" model. '
                'This node takes a Z-Image Turbo model, an initial latent image, and conditioning parameters, '
                'and produces a denoised output ready for further processing or decoding.'
            ),
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
                io.Int.Input         ("seed", default=0, min=0, max=0xffffffffffffffff, control_after_generate=True,
                                      tooltip="The seed used for the random noise generator, ensuring the same result is produced with the same value.",
                                     ),
                io.Int.Input         ("steps", default=9, min=4, max=9, step=1,
                                      tooltip="The number of iterations to be performed during the sampling process.",
                                     ),
                io.Float.Input       ("denoise", default=1.0, min=0.98, max=1.00, step=0.01,
                                      tooltip="The amount of denoising applied, lower values will maintain the structure of the initial image allowing for image to image sampling.",
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
                ) -> io.NodeOutput:

        # for now only the "euler" sampler has been tested with this technique
        sampler  = comfy.samplers.sampler_object("euler")

        # set the sigmas for each number of steps
        if steps>=9:
            sigmas1  = [0.991, 0.98, 0.92]
            sigmas2  = [0.935, 0.90, 0.875, 0.750, 0.0000]
            sigmas3  = [0.6582, 0.4556, 0.2000, 0.0000]

        elif steps==8:
            sigmas1  = [0.991, 0.98, 0.92]
            sigmas2  = [0.935, 0.90, 0.875, 0.750, 0.0000]
            sigmas3  = [0.6582, 0.3019, 0.0000]

        elif steps==7:
            sigmas1  = [0.991, 0.98, 0.92]
            sigmas2  = [0.9350, 0.8916, 0.7600, 0.0000]  # [0.9350, 0.8916, 0.7895, 0.0000],
            sigmas3  = [0.6582, 0.3019, 0.0000]

        elif steps==6:
            sigmas1 = [0.991, 0.980, 0.920]
            sigmas2 = [0.942, 0.780, 0.000]  # [0.935, 0.770, 0.000]
            sigmas3 = [0.6582, 0.3019, 0.0000]

        elif steps==5:
            sigmas1 = [0.991, 0.980, 0.920]
            sigmas2 = [0.942, 0.780, 0.000]
            sigmas3 = [0.6200, 0.0000]

        elif steps<=4:
            sigmas1 = [0.991, 0.980, 0.920]
            sigmas2 = [0.942, 0.000]
            sigmas3 = [0.790, 0.000]

        latent_output = cls.execute_3_steps_denoising(latent_input,
                                                        model    = model,
                                                        seed     = seed,
                                                        cfg      = 1.0,
                                                        positive = positive,
                                                        negative = positive,
                                                        sampler  = sampler,
                                                        sigmas1  = sigmas1,
                                                        sigmas2  = sigmas2,
                                                        sigmas3  = sigmas3,
                                                        )
        return io.NodeOutput(latent_output)



    #__ internal functions ________________________________

    @classmethod
    def execute_3_steps_denoising(cls,
                                  latent_image,
                                  model    : Any,
                                  seed     : int,
                                  cfg      : float,
                                  positive : list,
                                  negative : list,
                                  sampler  : comfy.samplers.KSAMPLER,
                                  sigmas1  : list | torch.Tensor,
                                  sigmas2  : list | torch.Tensor,
                                  sigmas3  : list | torch.Tensor,
                                  ):
        """
        Executes a three-step denoising process on the provided latent image.

        Args:
            latent_image: A dictionary containing the data about the latent image to be processed.
            model       : The ComfyUI model object to be used during denoising.
            seed        : Random seed for reproducibility.
            cfg         : classifier-free guidance scale that controls the strength of negative prompts.
                          (a value of 1.0 means that the negative prompt has no effect on generation)
            positive    : Positive prompts or conditions for the model.
            negative    : Negative prompts or conditions for the model.
            sampler     : The ComfyUI sampler object to use during denoising.
            sigmas1     : Sigma values for the first step of denoising.
            sigmas2     : Sigma values for the second step of denoising.
            sigmas3     : Sigma values for the third step of denoising.

        Returns:
            A dictionary with the latent image data after denoising.
        """

        # if sigmas is a list then convert it to pytorch tensor
        if isinstance(sigmas1, list):
            sigmas1 = torch.tensor(sigmas1, device='cpu')
        if isinstance(sigmas2, list):
            sigmas2 = torch.tensor(sigmas2, device='cpu')
        if isinstance(sigmas3, list):
            sigmas3 = torch.tensor(sigmas3, device='cpu')

        # calculate the progress level for each step
        prog0      = 0
        prog1      = prog0 + sigmas1.shape[-1] - 1
        prog2      = prog1 + sigmas2.shape[-1] - 1
        prog_total = prog2 + sigmas3.shape[-1] - 1
        progress = ProgressPreview.from_comfyui( model, prog_total )

        # three steps denoising
        latent_image = cls.execute_sampler_custom(model, True, seed, cfg, positive, negative, sampler,
                                                  sigmas           = sigmas1,
                                                  latent_image     = latent_image,
                                                  progress_preview = ProgressPreview( prog1-prog0, parent=(progress,prog0,prog1) ),
                                                  )
        latent_image = cls.execute_sampler_custom(model, False, seed, cfg, positive, negative, sampler,
                                                  sigmas           = sigmas2,
                                                  latent_image     = latent_image,
                                                  progress_preview = ProgressPreview( prog2-prog1 , parent=(progress,prog1,prog2) ),
                                                  )
        latent_image = cls.execute_sampler_custom(model, True, 696969, cfg, positive, negative, sampler,
                                                  sigmas           = sigmas3,
                                                  latent_image     = latent_image,
                                                  progress_preview = ProgressPreview( prog_total-prog2, parent=(progress,prog2,prog_total) ),
                                                  )
        return latent_image



    @classmethod
    def execute_sampler_custom(cls,
                               model,
                               add_noise,
                               noise_seed,
                               cfg,
                               positive,
                               negative,
                               sampler,
                               sigmas       : list | torch.Tensor,
                               latent_image : dict[str, Any],
                               *,
                               progress_preview: ProgressPreview | None = None,
                               ) -> dict[str, Any]:
        """
        Emulates the 'SamplerCustom' node from ComfyUI

        Args:
            model       : The ComfyUI model object to be used during denoising.
            add_noise   : Whether to add noise to the initial samples or not.
            noise_seed  : The seed used to generate random noise.
            cfg         : Classifier-free guidance scale that controls the strength of negative prompts.
                          A value of 1.0 means the negative prompt has no effect on generation.
            positive    : Positive prompts or conditions for the model.
            negative    : Negative prompts or conditions for the model.
            sampler     : The ComfyUI sampler object to use during denoising.
            sigmas      : Sigma values used in the denoising process. Can be a list or torch.Tensor.
            latent_image: Dictionary containing the data about the initial latent image to denoise.
            progress_preview (ProgressPreview | None): Optional callback for tracking progress.

        Returns:
            A dictionary with the updated latent image data after denoising.
        """
        # if sigmas is a list then convert it to pytorch tensor
        if isinstance(sigmas, list):
            sigmas = torch.tensor(sigmas, device='cpu')

        # extract all the info that comes packaged in the `latent_image` dictionary
        latent      = latent_image.copy()
        samples     = comfy.sample.fix_empty_latent_channels(model, latent["samples"])
        noise_mask  = latent.get("noise_mask")
        batch_index = latent.get("batch_index")
        if not add_noise:
            noise = torch.zeros(samples.shape, dtype=samples.dtype, layout=samples.layout, device="cpu")
        else:
            noise = comfy.sample.prepare_noise(samples, noise_seed, batch_index)

        disable_pbar = not comfy.utils.PROGRESS_BAR_ENABLED
        samples = comfy.sample.sample_custom(model, noise, cfg, sampler, sigmas, positive, negative, samples, noise_mask=noise_mask, callback=progress_preview, disable_pbar=disable_pbar, seed=noise_seed)

        out = latent_image.copy()
        out["samples"] = samples
        return out


# ============================================================================
# EXPERT SIGMA INTERPOLATION (for ZSamplerTurboCurve)
# ============================================================================
# The core idea: treat the hardcoded discrete values as sample points from a
# "mother space" and use mathematical interpolation to build a continuous function.
# This transforms isolated experimental data into continuous generation rules.

# "Gold standard" master curves extracted from the best 9-step configuration
_MASTER_SIGMAS_S1 = [0.991, 0.98, 0.92]                  # Stage 1: Foundation (fixed, critical for composition)
_MASTER_SIGMAS_S2 = [0.935, 0.90, 0.875, 0.750, 0.000]   # Stage 2: Main body
_MASTER_SIGMAS_S3 = [0.6582, 0.4556, 0.2000, 0.0000]     # Stage 3: Details


def _get_enhanced_stage1_sigmas(structure: float) -> list:
    """
    Generate Stage 1 sigmas with structure enhancement using interpolation.

    Extends the original master curve by adding a higher starting point,
    then interpolates to preserve the original "slow-then-fast" rhythm.

    Args:
        structure: 0.0 (normal, 3 steps) to 1.0 (enhanced, 6 steps)
                   - 0.0: Use original [0.991, 0.98, 0.92]
                   - 0.5: 5 steps, start at 0.995
                   - 1.0: 6 steps, start at 0.999

    Returns:
        List of sigma values for Stage 1
    """
    if structure <= 0.0:
        return _MASTER_SIGMAS_S1.copy()

    # Extend master curve by adding higher starting point
    # This preserves the original rhythm while extending the range
    base_max = 0.991 + (0.008 * structure)  # 0.991 -> 0.999
    extended_master = [base_max] + _MASTER_SIGMAS_S1  # [0.999, 0.991, 0.98, 0.92]

    # Map structure to steps: normal=3, medium=5, strong=6
    # Using 3 * structure (not 4) to cap at 6 steps, avoiding "dirty" textures
    num_steps = int(3 + (3 * structure))

    return _interpolate_expert_sigmas(extended_master, num_steps)


def _interpolate_expert_sigmas(master_sigmas: list, num_steps: int, tension: float = 1.0) -> list:
    """
    Interpolate expert sigma values from master curve to generate arbitrary step counts.

    This preserves the "non-linear gradient" - e.g., the slow descent from 0.935 to 0.90
    and the rapid drop from 0.75 to 0.0, maintaining the "slow-start, fast-finish"
    suppression rhythm that Karras formulas cannot provide.

    Args:
        master_sigmas: The reference sigma values (gold standard)
        num_steps: The desired number of steps to generate
        tension: Curve tension control (1.0 = follow interpolation exactly,
                 >1.0 = stay longer at low values for more detail,
                 <1.0 = descend faster for more contrast)

    Returns:
        Interpolated sigma values as a list
    """
    if num_steps <= 1:
        return [master_sigmas[-1]]

    # Create index mapping for master curve [0, 1]
    xp = np.linspace(0, 1, len(master_sigmas))
    # Apply tension to evaluation points (affects curve shape)
    eval_points = np.linspace(0, 1, num_steps)
    if tension != 1.0:
        # tension > 1: slower descent (more time at high sigmas)
        # tension < 1: faster descent (rush through high sigmas)
        eval_points = np.power(eval_points, 1.0 / tension)
    # Use numpy interpolation for smooth results
    return np.interp(eval_points, xp, master_sigmas).tolist()


def _get_expert_sigmas(total_steps: int, tension: float = 1.0, structure: float = 0.0) -> tuple[list, list, list]:
    """
    Generate three-stage expert sigma values for any step count.

    Stage allocation strategy:
    - Stage 1: Variable steps based on structure (3-7 steps)
    - Stage 2 & 3: Remaining steps distributed proportionally

    This ensures:
    1. The "0.92 -> 0.935" re-sampling jump is always preserved
    2. Smooth transitions as step count changes (no jarring jumps)
    3. Inherited "slow-start, fast-finish" rhythm from master curves

    Args:
        total_steps: Total number of denoising steps requested
        tension: Curve tension control for stages 2 and 3
        structure: Structure enhancement (0.0=normal, 1.0=enhanced composition)

    Returns:
        Tuple of (sigmas1, sigmas2, sigmas3) as lists
    """
    # Stage 1: use enhanced generator if structure > 0
    sigmas1 = _get_enhanced_stage1_sigmas(structure)
    steps_s1 = len(sigmas1)

    # Calculate remaining steps for stages 2 and 3
    # Note: +2 because stage transitions overlap at endpoints
    remaining = max(2, total_steps - steps_s1 + 2)

    # Distribute remaining steps: stage 2 gets slightly more (main body work)
    steps_s2 = (remaining * 3) // 5 + 1  # ~60% for stage 2
    steps_s3 = remaining - steps_s2 + 1  # ~40% for stage 3

    # Ensure minimum steps per stage
    steps_s2 = max(2, steps_s2)
    steps_s3 = max(2, steps_s3)

    # Adjust Stage 2 start point based on structure enhancement
    # More structure -> bigger jump (0.935 -> 0.945) for better re-sampling
    master_s2 = _MASTER_SIGMAS_S2.copy()
    if structure > 0.0:
        s2_start_boost = 0.01 * structure
        master_s2[0] = min(0.95, master_s2[0] + s2_start_boost)

    # Interpolate stages 2 and 3 from master curves
    sigmas2 = _interpolate_expert_sigmas(master_s2, steps_s2, tension)
    sigmas3 = _interpolate_expert_sigmas(_MASTER_SIGMAS_S3, steps_s3, tension)

    return sigmas1, sigmas2, sigmas3


class ZSamplerTurboCurve(io.ComfyNode):
    """
    Experimental variant of ZSamplerTurbo using interpolated expert curves.

    Instead of hardcoded sigma values for each step count, this node uses
    mathematical interpolation to generate smooth sigma curves for any step count.
    This allows for:
    - Arbitrary step counts (not limited to 4-9)
    - Smooth transitions when adjusting steps (no jarring quality jumps)
    - Preserved "slow-start, fast-finish" rhythm from expert tuning
    - Optional tension control for fine-tuning the curve shape
    """
    xTITLE         = "ZSampler Turbo Curve"
    xCATEGORY      = ""
    xCOMFY_NODE_ID = ""
    xDEPRECATED    = False

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            display_name  = cls.xTITLE,
            category      = cls.xCATEGORY,
            node_id       = cls.xCOMFY_NODE_ID,
            is_deprecated = cls.xDEPRECATED,
            description   = (
                'Experimental variant using interpolated expert curves. '
                'Supports arbitrary step counts with smooth sigma transitions. '
                'Use this alongside ZSampler Turbo for A/B comparison testing.'
            ),
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
                io.Int.Input         ("seed", default=0, min=0, max=0xffffffffffffffff, control_after_generate=True,
                                      tooltip="The seed used for the random noise generator, ensuring the same result is produced with the same value.",
                                     ),
                io.Int.Input         ("steps", default=9, min=4, max=20, step=1,
                                      tooltip="The number of iterations (now supports 4-20 steps via interpolation).",
                                     ),
                io.Float.Input       ("tension", default=1.0, min=0.5, max=2.0, step=0.05,
                                      tooltip="Curve tension: 1.0=normal, >1.0=more detail (slower descent), <1.0=more contrast (faster descent).",
                                     ),
                io.Combo.Input       ("structure", options=["normal", "medium", "strong"],
                                      default="normal",
                                      tooltip="Structure enhancement for Stage 1: "
                                              "normal=3 steps, medium=5 steps, strong=6 steps. "
                                              "Higher values improve composition stability for complex scenes.",
                                     ),
                io.Float.Input       ("denoise", default=1.0, min=0.98, max=1.00, step=0.01,
                                      tooltip="The amount of denoising applied, lower values will maintain the structure of the initial image allowing for image to image sampling.",
                                     ),
            ],
            outputs=[
                io.Latent.Output(display_name="latent_output", tooltip="The resulting denoised latent image, ready to be decoded by a VAE or passed to another sampler."),
            ]
        )

    # Structure option to numeric value mapping
    STRUCTURE_VALUES = {"normal": 0.0, "medium": 0.5, "strong": 1.0}

    @classmethod
    def execute(cls,
                model,
                positive    : list,
                latent_input: dict[str, Any],
                seed        : int,
                steps       : int,
                tension     : float,
                structure   : str,
                denoise     : float,
                ) -> io.NodeOutput:

        # for now only the "euler" sampler has been tested with this technique
        sampler = comfy.samplers.sampler_object("euler")

        # Map structure option to numeric value
        structure_value = cls.STRUCTURE_VALUES.get(structure, 0.0)

        # Generate sigmas using expert curve interpolation with structure enhancement
        sigmas1, sigmas2, sigmas3 = _get_expert_sigmas(steps, tension, structure_value)

        # Log the generated sigmas for debugging/comparison
        logger.debug(f"ZSamplerTurboCurve: steps={steps}, tension={tension}, structure={structure}")
        logger.debug(f"  sigmas1={[f'{s:.4f}' for s in sigmas1]}")
        logger.debug(f"  sigmas2={[f'{s:.4f}' for s in sigmas2]}")
        logger.debug(f"  sigmas3={[f'{s:.4f}' for s in sigmas3]}")

        latent_output = ZSamplerTurbo.execute_3_steps_denoising(
            latent_input,
            model    = model,
            seed     = seed,
            cfg      = 1.0,
            positive = positive,
            negative = positive,
            sampler  = sampler,
            sigmas1  = sigmas1,
            sigmas2  = sigmas2,
            sigmas3  = sigmas3,
        )
        return io.NodeOutput(latent_output)

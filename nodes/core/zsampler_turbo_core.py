"""
File    : zsampler_turbo_core.py
Purpose : The core method for the "Z-Sampler Turbo" process.
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Mar 16, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
"""
import torch
import torch.nn.functional as F
import comfy.utils
import comfy.sample
import comfy.samplers
import comfy.sampler_helpers
from comfy.samplers import KSAMPLER
from typing         import Any, TypeAlias, cast
from .progress_bar  import ProgressPreview
from .zsampler_turbo_corehelp import EulerAss, \
                                     sampler_from_name, \
                                     generate_noise, \
                                     inject_freq_noise, \
                                     truncate_sigmas_by_step_range, \
                                     truncate_sigmas_by_value_range, \
                                     refine_sigma_sequence, \
                                     merge_sigmas, \
                                     scramble_tensor
ComfyLatent      : TypeAlias = dict[str, Any]
ComfyModel       : TypeAlias = Any
ComfyConditioning: TypeAlias = list[ tuple[torch.Tensor,dict] ]
_DEFAULT_INJECT_NOISE_FREQS     = (  0,   0,   0)
_DEFAULT_INJECT_NOISE_SCALES    = (0.0, 0.0, 0.0)
_SCRAMBLE_COUNTS_DISABLED       = ( 0,  0,  0,  0)
_SCRAMBLE_COUNTS_DEFAULT        = ( 1,  0,  1,  0)
_SCRAMBLE_COUNTS_EVEN_SEED      = ( 2, -1,  2, -1)
_SCRAMBLE_COUNTS_MULTIPLE_OF_10 = (-2, -2, -2, -2)



def zsampler_turbo_core(latent_input             : ComfyLatent,
                        model                    : ComfyModel,
                        positive                 : ComfyConditioning,
                        *,
                        seed                     : int,
                        steps                    : int,
                        initial_noise_bias_level : float                                   = 0.0,
                        initial_noise_overdose   : float                                   = 0.0,
                        noise_est_sample_size    : str | int | None                        = None,
                        sigma_preset_name        : str | None                              = None,
                        sigma_offsets            : list[float] | None                      = None,
                        sigma_limits             : tuple[float,float] | list[float] | None = None,
                        sigma_step_range         : tuple[int,int] | list[int] | None       = None,
                        start_with_noise         : bool                                    = True,
                        end_with_denoise         : bool                                    = True,
                        positive_stg2_preproc    : ComfyConditioning | None                = None,
                        positive_stg2            : ComfyConditioning | None                = None,
                        positive_stg3            : ComfyConditioning | None                = None,
                        stage2_scramble          : bool                                    = False,
                        stage2_scramble_counts   : tuple[int,int,int,int] | None           = None,
                        stage2_preproc_steps     : int                                     = 0,
                        extra_noise_freqs        : tuple[int  ,...] | None                 = None,
                        extra_noise_scales       : tuple[float,...] | None                 = None,
                        samplers                 : tuple[str|object, ...] | None           = None,
                        progress_preview         : ProgressPreview
                        ) -> dict[str, Any]:
    """
    Perform the three-stage denoising process on a latent input.

    Args:
        latent_input            : ComfyUI LATENT dict containing the initial latent tensor to be denoised.
                                   Includes keys like "samples" and optional "noise_mask", "batch_index".
        model                   : ComfyUI MODEL obj representing the model to use for denoising.
        positive                : Positive conditioning for the denoising process.
        seed                    : Seed for the deterministic RNG used throughout the sampler.
        steps                   : The total number of denoising steps. This value will
                                   be used internally to determine the sigmas values.
        initial_noise_bias_level: The proportion of the estimated noise bias to apply before the first
                                   denoising step.
                                   0.0 = no noise bias applied
                                   1.0 = using 100% of the estimated noise bias
        initial_noise_overdose  : The level of over-amplitude in the initial noise scale.
                                   0.0 = default noise scale;
                                   positive values will increase the noise scale, e.g: 0.1 = 10% increment;
                                   negative values will reduce the noise scale, e.g: -0.1 = 10% decrement.
        noise_est_sample_size   : Size in pixels of the sample for initial noise estimation.
                                   A string can be used to specify the size in pixels, e.g: "512px".
                                   If `None`, the size of the latent input will be used.
        sigma_preset_name       : Name of a predefined sigma schedule (e.g. "alpha", "bravo").
                                  If `None` the default schedule is used.
        sigma_offsets           : Optional list of offsets to be added to the calculated sigma values.
        sigma_limits            : Optional tuple with minimum and maximum limits for sigma values.
        sigma_step_range        : Optional tuple with the range of steps that will actually be performed.
        start_with_noise        : If `True` (default), begins the denoising process by injecting noise.
                                   Set to `False` to preserve noise from a previous process (chaining samplers).
        end_with_denoise        : If `True` (default), ends the denoising process by zeroing out residual noise.
                                   Set to `False` to preserve noise for a next process (chaining samplers).
        positive_stg2_preproc   : Optional positive conditioning to be used in the second stage pre-processing.
                                   If `None` (default), the main positive conditioning will be used.
        positive_stg2           : Optional positive conditioning to be used in the second stage.
                                   If `None` (default), the main positive conditioning will be used.
        positive_stg3           : Optional positive conditioning to be used in the third stage.
                                   If `None` (default), the second stage positive conditioning will be used.
        stage2_scramble         : Optional boolean to enable scrambling the latent image at the start of stage2.
                                   This increases the model's creativity, generating images with more varied
                                   compositions without altering the style.
        stage2_scramble_counts  : Optional tuple of four signed integers (left, top, right, bottom) that determine
                                   the amount of steps for the latent scrambling. Zero values mean "skip that side",
                                   positive values add normal fragments from that side, while negative values add
                                   randomly flipped fragments.
                                   If this parameter is (0,0,0,0), no scrambling is performed even if `stage2_scramble=True`.
                                   If this parameter is None (default), the amount of steps is pseudo-randomly
                                   determined when `stage2_scramble=True`.
        stage2_preproc_steps    : Optional number of steps to be performed as preprocessing in the second stage.
                                   This can improve coherence and reduce hallucinations.
                                   If zero (default), no preprocessing is performed.
        extra_noise_freqs       : Optional frequencies at which additional noise is injected into the latent image
                                   during each stage. The first two values correspond to stage1 and stage2, while all
                                   following values correspond to stage3. If `None` (default), no extra noise is injected.
                                   These frequencies determine the granularity of noise injection.
                                   For example, a value of 1024 means noise is injected into every pixel, while a
                                   value of 512 means noise is injected every second pixel, with intermediate pixels
                                   being interpolated. Lower frequency values result in smoother noise transitions
                                   across the image.
        extra_noise_scales      : Optional scales for extra noise injected into the latent image in each stage.
                                   The first two values correspond to stage1 and stage2, while all following
                                   values correspond to stage3. If `None` (default), no extra noise is injected.
        samplers                : Optional tuple of KSAMPLERs (or strings with the names of the samplers) to be
                                  used in each stage. If `None` (default) then "euler" is used in all stages.
        progress_preview        : A `ProgressPreview` object for displaying progress during the denoising process.

    Returns:
        A ComfyUI LATENT object with the denoised latent output.
    """

    # z-image turbo is a cfg-distilled model requiring CFG=1.0, which discard
    # negative conditioning, here we set it to `positive` for simplicity
    negative = positive

    ## if no sampler was specified, we use "euler" in each stage
    if samplers is None:
       samplers = ("euler", "euler", "euler")

    # convert sampler names to sampler objects,
    # ensuring that at least three samplers were provided
    sampler_objs = tuple( sampler_from_name(s) if isinstance(s,str) else cast(KSAMPLER,s) for s in samplers )
    if len(sampler_objs) < 3:
        raise ValueError("If `samplers` parameter is specified, it should contain at least three valid samplers.")

    # validate `inject_noise_freqs/scales`
    if extra_noise_freqs is not None:
        if not isinstance(extra_noise_freqs,tuple) or len(extra_noise_freqs) < 3:
            raise ValueError("`inject_noise_freqs` must be None or a tuple of at least 3 ints.")
    if extra_noise_scales is not None:
        if not isinstance(extra_noise_scales,tuple) or len(extra_noise_scales) < 3:
            raise ValueError("`inject_noise_scales` must be None or a tuple of at least 3 floats")

    # validate `stage2_scramble_counts`
    if stage2_scramble_counts is not None:
        if not isinstance(stage2_scramble_counts,tuple) or len(stage2_scramble_counts) != 4:
            raise ValueError("`stage2_scramble_counts` must be None or a tuple of 4 integers")

    # validate sigma_limits & sigma_step_range
    if sigma_limits is not None:
        if not isinstance(sigma_limits, (tuple,list)) or len(sigma_limits)<2:
            raise ValueError("sigma_limits must be a tuple or list with at least two float values")
    if sigma_step_range is not None:
        if not isinstance(sigma_step_range, (tuple,list)) or len(sigma_step_range)<2:
            raise ValueError("sigma_step_range must be a tuple or list with at least two integer values")

    # force `inject_noise_freqs/scales` to be tuples of 3 elements
    if extra_noise_freqs is None:
        extra_noise_freqs  = _DEFAULT_INJECT_NOISE_FREQS
    if extra_noise_scales is None:
        extra_noise_scales = _DEFAULT_INJECT_NOISE_SCALES

    # force `stage2_scramble_counts` to be a tuple of 4 integers
    if not stage2_scramble:
        stage2_scramble_counts = _SCRAMBLE_COUNTS_DISABLED
    elif stage2_scramble_counts is None:
        stage2_scramble_counts = _SCRAMBLE_COUNTS_MULTIPLE_OF_10 if (seed % 10) == 0 else \
                                 _SCRAMBLE_COUNTS_EVEN_SEED      if (seed %  2) == 0 else \
                                 _SCRAMBLE_COUNTS_DEFAULT


    # get the sigmas for the 3 stages from the preset name ("alpha" or "bravo")
    sigma_preset = SIGMA_PRESETS_BY_NAME.get(sigma_preset_name) if sigma_preset_name else None
    if not sigma_preset:
        sigma_preset = SIGMA_PRESETS_BY_NAME["alpha"]
    if len(sigma_preset) != 7:
        raise ValueError(f"Sigma presets must have 7 elements but the \"{sigma_preset_name}\" preset has {len(sigma_preset)} elements")
    index   = min(max( 3, steps), 9 ) - 3
    sigmas1 = list(sigma_preset[index][0])
    sigmas2 = list(sigma_preset[index][1])
    sigmas3 = list(sigma_preset[index][2])

    # when the number of steps is greater than 9, the same 9-step sigma
    # sequence is used, but the Stage 2 and Stage 3 are refined to match
    # the required number of steps
    if steps>9:
        additional_steps = (steps-9)
        n1 = int( 0.4 + 0.6 * additional_steps )
        n2 = additional_steps - n1
        sigmas2 = refine_sigma_sequence(sigmas2, n1)
        sigmas3 = refine_sigma_sequence(sigmas3, n2)

    # add the values of sigmas_offset to each sigma in the 3 lists
    if sigma_offsets:
        offset_iter = iter(sigma_offsets)
        if isinstance(sigmas1, list):
            for i in range( len(sigmas1) ):
                sigmas1[i] += next(offset_iter, 0.0)
        if isinstance(sigmas2, list):
            for i in range(len(sigmas2) - 1):
                sigmas2[i] += next(offset_iter, 0.0)
        if isinstance(sigmas3, list):
            for i in range(len(sigmas3) - 1):
                sigmas3[i] += next(offset_iter, 0.0)

    # `sample_size` is noise_est_sample_size converted to integer/pixels
    # or None if "full_size" option was selected
    sample_size : int | None = None
    if isinstance(noise_est_sample_size, str) and noise_est_sample_size.endswith("px"):
        sample_size = int(noise_est_sample_size[:-2])
    elif isinstance(noise_est_sample_size, (int,float)):
        sample_size = int(noise_est_sample_size)

    # execute the 3-stage denoising process
    return execute_3_stage_denoising(latent_input, model, positive, negative,
                                     seed                     = seed,
                                     cfg                      = 1.0,
                                     samplers                 = sampler_objs,
                                     sigmas1                  = sigmas1,
                                     sigmas2                  = sigmas2,
                                     sigmas3                  = sigmas3,
                                     sigma_limits             = sigma_limits,
                                     sigma_step_range         = sigma_step_range,
                                     start_with_noise         = start_with_noise,
                                     end_with_denoise         = end_with_denoise,
                                     positive_stg2_preproc    = positive_stg2_preproc,
                                     positive_stg2            = positive_stg2,
                                     positive_stg3            = positive_stg3,
                                     initial_noise_bias_level = initial_noise_bias_level,
                                     initial_noise_overdose   = initial_noise_overdose,
                                     noise_est_sample_size    = sample_size,
                                     extra_noise_scales       = extra_noise_scales,
                                     extra_noise_freqs        = extra_noise_freqs,
                                     stage2_scramble_counts   = stage2_scramble_counts,
                                     stage2_preproc_steps     = stage2_preproc_steps,
                                     progress_preview = progress_preview,
                                     )


def execute_3_stage_denoising(comfy_latent: ComfyLatent,
                              model       : ComfyModel,
                              positive    : ComfyConditioning,
                              negative    : ComfyConditioning,
                              *,
                              seed                    : int,
                              cfg                     : float,
                              samplers                : tuple[KSAMPLER, ...],
                              sigmas1                 : torch.Tensor | list | tuple | None,
                              sigmas2                 : torch.Tensor | list | tuple | None,
                              sigmas3                 : torch.Tensor | list | tuple | None,
                              sigma_limits            : tuple[float,float] | list[float] | None = None,
                              sigma_step_range        : tuple[int,int]     | list[int]   | None = None,
                              start_with_noise        : bool                                    = True,
                              end_with_denoise        : bool                                    = True,
                              positive_stg2_preproc   : ComfyConditioning | None                = None,
                              positive_stg2           : ComfyConditioning | None                = None,
                              positive_stg3           : ComfyConditioning | None                = None,
                              initial_noise_bias_level: float                                   = 0.0,
                              initial_noise_overdose  : float                                   = 0.0,
                              noise_est_sample_size   : tuple[int,int] | int | None             = None,
                              extra_noise_freqs       : tuple[int  ,...]                        = (  0,   0,   0),
                              extra_noise_scales      : tuple[float,...]                        = (0.0, 0.0, 0.0),
                              stage2_scramble_counts  : tuple[int,int,int,int]                  = (0,0,0,0),
                              stage2_preproc_steps    : int                                     = 0,
                              progress_preview        : ProgressPreview,
                              ):
    """
    Executes a three-stage denoising process on the provided latent image.

    Args:
        comfy_latent            : ComfyUI LATENT dict containing the initial latent tensor to be denoised.
                                   Includes keys like "samples" and optional "noise_mask", "batch_index".
        model                   : ComfyUI MODEL obj representing the model to use for denoising.
        positive                : Positive prompt/conditioning applied to the model during denoising.
        negative                : Negative prompt/conditioning applied to the model during denoising.
        seed                    : Seed for the deterministic RNG used throughout the denoising process.
        cfg                     : Classifier-free guidance scale that controls the influence of negative prompts.
                                   A value of 1.0 means the negative prompt has no effect on generation.
        sampler                 : ComfyUI object representing the sampler used for each denoising step.
        sigmas1                 : Sigma values for the first stage of denoising. Can be a tensor, list, or None.
        sigmas2                 : Sigma values for the second stage of denoising. Can be a tensor, list, or None.
        sigmas3                 : Sigma values for the third stage of denoising. Can be a tensor, list, or None.
        sigma_limits            : The range of sigma values where the denoising process should be performed.
                                   Steps with sigmas outside this range will be ignored.
                                   Can be a tuple or list of two floats, or None if all steps should be processed.
        sigma_step_range        : The range of steps to be processed. Steps outside this range will be ignored.
                                   Can be a tuple or list of two integers, or None if all steps should be processed.
        start_with_noise        : If `True` (default), begins the denoising process by injecting noise.
                                   Set to `False` to preserve noise from a previous process (chaining samplers).
        end_with_denoise        : If `True` (default), ends the denoising process by zeroing out residual noise.
                                   Set to `False` to preserve noise for a next process (chaining samplers).
        positive_stg2_preproc   : Optional positive conditioning to be used in the second stage pre-processing.
                                   If `None` (default), the main positive conditioning will be used.
        positive_stg2           : Optional positive conditioning to be used in the second stage.
                                   If `None` (default), the main positive conditioning will be used.
        positive_stg3           : Optional positive conditioning to be used in the third stage.
                                   If `None` (default), the second stage positive conditioning will be used.
        initial_noise_bias_level: The proportion of the estimated noise bias to apply before the first denoising step.
                                   0.0 = no noise bias applied
                                   1.0 = using 100% of the estimated noise bias
        initial_noise_overdose  : The level of over-amplitude in the initial noise scale.
                                   0.0 = default noise amplitud scale;
                                   positive values will increase the noise scale, e.g: 0.1 = 10% increment;
                                   negative values will reduce the noise scale, e.g: -0.1 = 10% decrement.
        noise_est_sample_size   : Size in pixels of the sample for initial noise estimation.
                                   Can be a tuple (width, height) or integer for square sizes.
                                   If `None`, the size of the latent input will be used.
        extra_noise_freqs       : Optional frequencies at which additional noise is injected into the latent image
                                   during each stage. The first two values correspond to stage1 and stage2, while all
                                   following values correspond to stage3.
                                   These frequencies determine the granularity of noise injection.
                                   For example, a value of 1024 means noise is injected into every pixel, while a
                                   value of 512 means noise is injected every second pixel, with intermediate pixels
                                   being interpolated. Lower frequency values result in smoother noise transitions
                                   across the image.
        extra_noise_scales      : Optional scales for extra noise injected into the latent image in each stage.
                                   The first two values correspond to stage1 and stage2, while all following
                                   values correspond to stage3.
        stage2_scramble_counts  : Optional tuple of four signed integers (left, top, right, bottom) that determine
                                   the amount of steps for the latent scrambling. Zero values mean "skip that side",
                                   positive values add normal fragments from that side, while negative values add
                                   randomly flipped fragments.
                                   If this parameter is (0,0,0,0) (default), no scrambling is performed.
        stage2_preproc_steps    : Optional number of steps to be performed as preprocessing in the second stage.
                                   This can improve coherence and reduce hallucinations.
                                   If zero (default), no preprocessing is performed.
        progress_preview        : A `ProgressPreview` object for displaying progress during the denoising process.
    Returns:
        A dictionary with the updated latent image data after all three denoising stages.
    """
    SIGMA_START     = 1.0
    DEFAULT_SAMPLER = samplers[0] #<< should `DEFAULT_SAMPLER` be fixed to euler?

    # force all conditioning to be valid
    #  - if positive cond for stage-2-preprocessing is not provided, it will be the same as main conditioning
    #  - if positive cond for stage-2 is not provided, it will be the same as main conditioning
    #  - if positive cond for stage-3 is not provided, it will be the same as the stage-2
    positive_stg2_preproc = _valid_conditioning(positive_stg2_preproc, default=positive)
    positive_stg2         = _valid_conditioning(positive_stg2        , default=positive)
    positive_stg3         = _valid_conditioning(positive_stg3        , default=positive_stg2)

    # force each `sigma` to be a tensor
    if isinstance(sigmas1, (list,tuple)):
        sigmas1 = torch.tensor(sigmas1, device='cpu')
    if isinstance(sigmas2, (list,tuple)):
        sigmas2 = torch.tensor(sigmas2, device='cpu')
    if isinstance(sigmas3, (list,tuple)):
        sigmas3 = torch.tensor(sigmas3, device='cpu')

    # enable scrambling and coherence pre-processing only when non-empty counts are provided
    is_stg2_scramble_enabled = any(stage2_scramble_counts)
    is_stg2_preproc_enabled  = stage2_preproc_steps > 0

    # typically, stage1 and stage2 should operate as a single continuous
    # denoising process; however, a full denoise is required between these
    # stages if any "creativity" feature is enabled, as these processes must
    # be applied to a noise-free latent
    force_denoise_stg1_stg2 = is_stg2_scramble_enabled or is_stg2_preproc_enabled


    # store the stage1 & stage3 sigmas to later evaluate if it was truncated
    original_sigmas1 = sigmas1
    original_sigmas3 = sigmas3

    # truncate the sigmas to the specified range of steps. [start_step, end_step)
    if isinstance(sigma_step_range, (list,tuple)):
        i0 = 0
        i1 = i0 + _num_steps(sigmas1)
        i2 = i1 + _num_steps(sigmas2)
        sigmas1 = truncate_sigmas_by_step_range(sigmas1, sigma_step_range, first_sigma_step=i0)
        sigmas2 = truncate_sigmas_by_step_range(sigmas2, sigma_step_range, first_sigma_step=i1)
        sigmas3 = truncate_sigmas_by_step_range(sigmas3, sigma_step_range, first_sigma_step=i2)

    # truncate the sigmas to the specified range of values. [lower_value, upper_value]
    if isinstance(sigma_limits, (list,tuple)):
        sigmas1 = truncate_sigmas_by_value_range(sigmas1, sigma_limits)
        sigmas2 = truncate_sigmas_by_value_range(sigmas2, sigma_limits)
        sigmas3 = truncate_sigmas_by_value_range(sigmas3, sigma_limits)

    # after truncation,
    # check if stage1 and stage3 still start from the beginning of the sigma table
    stage1_starts_from_beginning = False
    if (sigmas1 is not None) and (original_sigmas1 is not None):
        stage1_starts_from_beginning = bool( sigmas1[0] == original_sigmas1[0] )
    stage3_start_from_beginning = False
    if (sigmas3 is not None) and (original_sigmas3 is not None):
        stage3_start_from_beginning = bool( sigmas3[0] == original_sigmas3[0] )


    # verify if inpainting is being performed by checking if the maximum value
    # in `sigma_limits` is less than 1.0
    # if inpainting is detected, combine stage1 and stage2 into stage1.
    # this action eliminates all stage2 processes including turbo creativity
    if isinstance(sigma_limits, (list,tuple)) and max(sigma_limits[0],sigma_limits[1]) < 1.0:
        sigmas1 = merge_sigmas(sigmas1, sigmas2)
        sigmas2 = None


    # calculate the progress level for each step
    progE = 0
    prog1 = progE + 1
    prog2 = prog1 + _num_steps(sigmas1)
    prog3 = prog2 + _num_steps(sigmas2)
    total = prog3 + _num_steps(sigmas3)


    #-- ESTIMATE THE INITIAL NOISE -----------------------

    initial_noise_scale = 1.0
    initial_noise_bias  = 0.0

    # the initial noise scale is directly controlled by the user through the
    # `initial_noise_overdose` parameter; adding extra noise at the beginning
    # generally helps generate images with more vivid colors or pronounced contrasts.
    initial_noise_scale += initial_noise_overdose

    # estimate the initial noise bias, which represents a shift in the mean noise values;
    # since any sigma sequence in this sampler starts with values below 1.0, using this
    # modified initial noise bias can introduce low-frequency components necessary for
    # the denoising process to be effective.
    # this calculation is performed only if the generation starts from pure noise and the
    # user has specified a non-zero level for the initial noise bias.
    if stage1_starts_from_beginning and (initial_noise_bias_level != 0):
        if sigmas1 is not None:
            bias, scale = estimate_initial_noise_features(
                            comfy_latent, model, positive, negative,
                            seed         = seed,
                            sampler      = samplers[0] if len(samplers) > 0 else DEFAULT_SAMPLER,
                            sigmas       = [SIGMA_START, sigmas1[0]],
                            sample_size  = noise_est_sample_size,
                            sample_bias  = 0.0,
                            sample_scale = 1.0,
                            progress_preview = ProgressPreview( 100,
                                parent=(progress_preview, 100*progE//total, 100*prog1//total) ),
                            )
            initial_noise_bias = (bias / scale).clamp(-0.005, 0.005)
            initial_noise_bias *= initial_noise_bias_level

    #-- THREE-STAGE PROCESS -------------------------------
    if sigmas1 is not None:
        is_first_stage = True
        is_last_stage  = (sigmas2 is None and sigmas3 is None)
        comfy_latent = _stage1_core(comfy_latent, model, positive, negative,
                        cfg                 = cfg,
                        sigmas              = sigmas1,
                        sampler             = samplers[0] if len(samplers) > 0 else DEFAULT_SAMPLER,
                        add_noise           = (is_first_stage and start_with_noise),
                        force_final_denoise = (is_last_stage  and end_with_denoise) or force_denoise_stg1_stg2,
                        noise_seed          = seed,
                        noise_scale         = initial_noise_scale,
                        noise_bias          = initial_noise_bias,
                        extra_noise_freqs   = extra_noise_freqs [0],
                        extra_noise_scales  = extra_noise_scales[0],
                        progress_preview = ProgressPreview( 100,
                            parent=(progress_preview, 100*prog1//total, 100*prog2//total)),
                        )

    if sigmas2 is not None:
        is_first_stage = (sigmas1 is None)
        is_last_stage  = (sigmas3 is None)
        comfy_latent = _stage2_core(comfy_latent, model, positive_stg2, negative,
                        cfg                 = cfg,
                        sigmas              = sigmas2,
                        sampler             = samplers[1] if len(samplers) > 1 else DEFAULT_SAMPLER,
                        add_noise           = (is_first_stage and start_with_noise) or force_denoise_stg1_stg2,
                        force_final_denoise = (is_last_stage  and end_with_denoise),
                        noise_seed          = seed+16,
                        noise_scale         = initial_noise_scale,
                        noise_bias          = initial_noise_bias,
                        extra_noise_freqs   = extra_noise_freqs [1],
                        extra_noise_scales  = extra_noise_scales[1],
                        scramble_counts     = stage2_scramble_counts if is_stg2_scramble_enabled else (0,0,0,0),
                        preproc_steps       = stage2_preproc_steps  if is_stg2_preproc_enabled else 0,
                        preproc_positive    = positive_stg2_preproc,
                        progress_preview = ProgressPreview( 100,
                            parent=(progress_preview, 100*prog2//total, 100*prog3//total)),
                        )

    if sigmas3 is not None:
        is_first_stage = (sigmas1 is None and sigmas2 is None)
        is_last_stage  = True
        comfy_latent = _stage3_core(comfy_latent, model, positive_stg3, negative,
                        cfg                 = cfg,
                        sigmas              = sigmas3,
                        sampler             = samplers[2] if len(samplers) > 2 else DEFAULT_SAMPLER,
                        add_noise           = (is_first_stage and start_with_noise) or stage3_start_from_beginning,
                        force_final_denoise = (is_last_stage  and end_with_denoise),
                        noise_seed          = 696969,
                        noise_scale         = 1.0,
                        noise_bias          = 0,
                        extra_noise_freqs   = extra_noise_freqs [2:],
                        extra_noise_scales  = extra_noise_scales[2:],
                        progress_preview = ProgressPreview( 100,
                            parent=(progress_preview, 100*prog3//total, 100*total//total)),
                        )
    _pid_sigmas = (sigmas3 if sigmas3 is not None else
                   sigmas2 if sigmas2 is not None else
                   sigmas1)
    if _pid_sigmas is not None and _pid_sigmas.numel() >= 2:
        comfy_latent["pid_sigma"] = float(_pid_sigmas[-2].item())

    return comfy_latent


#============================ Z-SAMPLER STAGES =============================#

def _stage1_core(comfy_latent : ComfyLatent,
                 model        : ComfyModel,
                 positive     : ComfyConditioning,
                 negative     : ComfyConditioning,
                 *,
                 cfg                 : float,
                 sigmas              : torch.Tensor,
                 sampler             : comfy.samplers.KSAMPLER,
                 add_noise           : bool,
                 force_final_denoise : bool,
                 noise_seed          : int,
                 noise_scale         : torch.Tensor | float | int = 1.0,
                 noise_bias          : torch.Tensor | float | int = 0.0,
                 extra_noise_freqs   : tuple[int,...  ] | int     = 0,
                 extra_noise_scales  : tuple[float,...] | float   = 0,
                 progress_preview    : ProgressPreview | None     = None,
                 ) -> ComfyLatent:

    latents       : torch.Tensor        = comfy_latent["samples"]
    noise_mask    : torch.Tensor | None = comfy_latent.get("noise_mask")
    batch_subseeds: list[int]| None     = comfy_latent.get("batch_index")

    latents = _iterative_denoising(latents, model, positive, negative,
                                   cfg                 = cfg,
                                   sigmas              = sigmas,
                                   sampler             = sampler,
                                   noise_scale         = noise_scale if add_noise else 0,
                                   noise_bias          = noise_bias  if add_noise else 0,
                                   noise_mask          = noise_mask,
                                   noise_seed          = noise_seed,
                                   batch_subseeds      = batch_subseeds,
                                   extra_noise_freqs   = extra_noise_freqs,
                                   extra_noise_scales  = extra_noise_scales,
                                   fix_empty_latent    = True,
                                   keep_masked_area    = True,
                                   force_final_denoise = force_final_denoise,
                                   progress_preview = progress_preview
                                   )

    comfy_latent = comfy_latent.copy()
    comfy_latent["samples"] = latents
    return comfy_latent


def _stage2_core(comfy_latent : ComfyLatent,
                 model        : ComfyModel,
                 positive     : ComfyConditioning,
                 negative     : ComfyConditioning,
                 *,
                 cfg                 : float,
                 sigmas              : torch.Tensor,
                 sampler             : comfy.samplers.KSAMPLER,
                 add_noise           : bool,
                 force_final_denoise : bool,
                 noise_seed          : int,
                 noise_scale         : torch.Tensor | float | int = 1.0,
                 noise_bias          : torch.Tensor | float | int = 0.0,
                 extra_noise_freqs   : tuple[int,...  ] | int     = 0,
                 extra_noise_scales  : tuple[float,...] | float   = 0,
                 scramble_counts     : tuple[int,int,int,int]     = (0, 0, 0, 0),
                 preproc_steps       : int                        = 0,
                 preproc_positive    : ComfyConditioning | None   = None,
                 preproc_negative    : ComfyConditioning | None   = None,
                 progress_preview    : ProgressPreview | None     = None,
                 ) -> ComfyLatent:

    latents       : torch.Tensor        = comfy_latent["samples"]
    noise_mask    : torch.Tensor | None = comfy_latent.get("noise_mask")
    batch_subseeds: list[int]| None     = comfy_latent.get("batch_index")

    original_noise_scale = noise_scale
    original_noise_bias  = noise_bias

    # force positive/negative pre-process conditioning to defaults if not provided by user
    if preproc_positive is None:
        preproc_positive = positive
    if preproc_negative is None:
        preproc_negative = negative

    # calculate the step progression to set the progress bar speed
    prog  = [ 0, *( i+1 for i in range(preproc_steps)), preproc_steps+_num_steps(sigmas) ]
    total = prog[-1]

    # == PRE-PROCESSING 1 ==
    # if requested, scramble the input latent image as a first process
    if any(scramble_counts):
        latents = scramble_tensor(latents, scramble_counts, seed=noise_seed)

    # == PRE-PROCESSING 2 ==
    # if requested, run preprocess sampling steps with high sigmas (0.949)
    # to try and give more coherence to the image
    for i in range(preproc_steps):
        latents = _iterative_denoising(latents, model, preproc_positive, preproc_negative,
                                       cfg                 = cfg,
                                       sigmas              = torch.tensor( (0.949, 0.000 ) ) if i==0 else sigmas[:2],
                                       sampler             = sampler,
                                       noise_scale         = original_noise_scale if add_noise else 0,
                                       noise_bias          = original_noise_bias  if add_noise else 0,
                                       noise_mask          = noise_mask,
                                       noise_seed          = noise_seed + i,
                                       batch_subseeds      = batch_subseeds,
                                       extra_noise_freqs   = 1024 if i==0 else 0,  # 64
                                       extra_noise_scales  =  0.8 if i==0 else 0,  # 4.0
                                       fix_empty_latent    = True,
                                       keep_masked_area    = True,
                                       force_final_denoise = True,
                                       progress_preview    = ProgressPreview(100,
                                            parent=(progress_preview, 100*prog[i]/total, 100*prog[i+1]/total))
                                       )
        # after the first iteration,
        # all other iterations (including the one outside the loop) should add noise
        add_noise   = True
        noise_scale = 1.0
        noise_bias  = noise_bias

    # == DEFAULT SAMPLING ==
    # always run the sampler using the original sigmas
    latents = _iterative_denoising(latents, model, positive, negative,
                                    cfg                 = cfg,
                                    sigmas              = sigmas,
                                    sampler             = sampler,
                                    noise_scale         = noise_scale if add_noise else 0,
                                    noise_bias          = noise_bias  if add_noise else 0,
                                    noise_mask          = noise_mask,
                                    noise_seed          = noise_seed + preproc_steps,
                                    batch_subseeds      = batch_subseeds,
                                    extra_noise_freqs   = extra_noise_freqs,
                                    extra_noise_scales  = extra_noise_scales,
                                    fix_empty_latent    = True,
                                    keep_masked_area    = True,
                                    force_final_denoise = force_final_denoise,
                                    progress_preview    = ProgressPreview(100,
                                            parent=(progress_preview, 100*prog[-2]/total, 100*prog[-1]/total))
                                    )
    out = comfy_latent.copy()
    out["samples"] = latents
    return out


def _stage3_core(comfy_latent : ComfyLatent,
                 model        : ComfyModel,
                 positive     : ComfyConditioning,
                 negative     : ComfyConditioning,
                 *,
                 cfg                 : float,
                 sigmas              : torch.Tensor,
                 sampler             : comfy.samplers.KSAMPLER,
                 add_noise           : bool,
                 force_final_denoise : bool,
                 noise_seed          : int,
                 noise_scale         : torch.Tensor | float | int = 1.0,
                 noise_bias          : torch.Tensor | float | int = 0.0,
                 extra_noise_freqs   : tuple[int,...  ] | int     = 0,
                 extra_noise_scales  : tuple[float,...] | float   = 0,
                 progress_preview    : ProgressPreview | None     = None,
                 ) -> ComfyLatent:

    latents       : torch.Tensor        = comfy_latent["samples"]
    noise_mask    : torch.Tensor | None = comfy_latent.get("noise_mask")
    batch_subseeds: list[int] | None    = comfy_latent.get("batch_index")

    latents = _iterative_denoising(latents, model, positive, negative,
                                   cfg                 = cfg,
                                   sigmas              = sigmas,
                                   sampler             = sampler,
                                   noise_scale         = noise_scale if add_noise else 0,
                                   noise_bias          = noise_bias  if add_noise else 0,
                                   noise_mask          = noise_mask,
                                   noise_seed          = noise_seed,
                                   batch_subseeds      = batch_subseeds,
                                   extra_noise_freqs   = extra_noise_freqs,
                                   extra_noise_scales  = extra_noise_scales,
                                   fix_empty_latent    = False,
                                   keep_masked_area    = True,
                                   force_final_denoise = force_final_denoise,
                                   progress_preview = progress_preview
                                   )
    comfy_latent = comfy_latent.copy()
    comfy_latent["samples"] = latents
    return comfy_latent


def _iterative_denoising(latents     : torch.Tensor,
                         model       : ComfyModel,
                         positive    : ComfyConditioning,
                         negative    : ComfyConditioning,
                         *,
                         cfg                 : float,
                         sigmas              : torch.Tensor,
                         sampler             : comfy.samplers.KSAMPLER,
                         noise_scale         : torch.Tensor | float | int | None = None,
                         noise_bias          : torch.Tensor | float | int | None = None,
                         noise_mask          : torch.Tensor | None               = None,
                         noise_seed          : int,
                         batch_subseeds      : list[int] | None                  = None,
                         extra_noise_freqs   : tuple[int,...] | int              = 0,
                         extra_noise_scales  : tuple[float,...] | float          = 0,
                         fix_empty_latent    : bool                              = True,
                         keep_masked_area    : bool                              = False,
                         force_final_denoise : bool                              = False,
                         progress_preview    : ProgressPreview | None            = None,
                         ) -> torch.Tensor:
    """
    Sampler function for iterative denoising of latent images using the provided sigmas.

    Args:
        latents             : Tensor containing latent images, shape: [batch_size, channels, height, width]
        model               : ComfyUI MODEL obj representing the model to use for denoising.
        positive            : Positive prompt/conditioning applied to the model during denoising.
        negative            : Negative prompt/conditioning applied to the model during denoising.
        cfg                 : Classifier-free guidance scale that controls the strength of negative prompts.
                               A value of 1.0 means the negative prompt has no effect on generation.
        sigmas              : Sigma values for each diffusion process step (can be list or torch.Tensor).
        sampler             : ComfyUI object representing the sampler used for each denoising step.
        noise_scale         : The scale factor applied to the initial noise.
                               (where 0.0 = no-noise; 1.0 = standard deviation; None = standard deviation)
                               Can be a tensor, scalar, or None.
                               If tensor, it must have shape [batch_size, channels, 1, 1].
        noise_bias          : The constant bias applied to the initial noise.
                               (where 0.0 = no-bias; 1.0 = are you creazy??!; None = no-bias)
                               Can be a tensor, scalar, or None.
                               If tensor, it must have shape [batch_size, channels, 1, 1].
        noise_mask          : Optional tensor containing the inpainting mask.
        noise_seed          : The seed used to generate random noise.
        batch_subseeds      : Optional list of small integers (0, 1, 2, …) that act as virtual seeds
                               for every image in the batch. Repetitions are allowed; repeated indices
                               yield identical noise for those images. If `None` or empty, every sample
                               receives independent noise.
        extra_noise_freq    : Optional frequency at which additional noise is injected into the latent image.
                               These frequencies determine the granularity of noise injection. For example, a
                               value of 1024 means noise is injected into every pixel, while a value of 512
                               means noise is injected every second pixel, with intermediate pixels being
                               interpolated. Lower frequency values result in smoother noise transitions
                               across the image. A value of zero means no noise is injected.
        extra_noise_scale   : Optional scale of the extra noise injected into the latent image. A value
                               of 0.0 means no noise is injected.
        fix_empty_latent    : If True, fixes empty latent images to have the shape required for the model,
        keep_masked_area    : If True, the masked area of the latent image will be kept unchanged.
                               Comfyui tries to keep masked area unchanged when there's a mask active
                               but activating this flag we're sure that no change will happen at all.
        force_final_denoise : If `True`, forces the final denoising step to zero out residual noise,
                               use `False` (default) for chaining samplers to preserve noise for the next stage.
        progress_preview    : Optional callback for tracking progress. Defaults to None.

    Returns:
        A tensor with the updated latent image data after denoising,

    Notes:
        - The noise initially added has the amplitude of `noise_scale` and the bias from `noise_bias`.
          If noise_scale and noise_bias are both 0.0, no noise will be added.
    """

    # if sigmas is a list then convert it to tensor
    if isinstance(sigmas, (list,tuple)):
        sigmas = torch.tensor(sigmas, device='cpu')

    # if `noise_bias` is a torch.Tensor
    # then it should have shape [batch_size, channels, 1, 1]
    if isinstance(noise_bias, torch.Tensor):
        if noise_bias.ndim != 4 or noise_bias.shape[2:] != (1, 1):
            raise ValueError(f"Invalid `noise_bias` shape: expected [batch_size, channels, 1, 1], "
                                f"but got {list(noise_bias.shape)}")

    # if `noise_scale` is a torch.Tensor
    # then it should have shape [batch_size, channels, 1, 1]
    if isinstance(noise_scale, torch.Tensor):
        if noise_scale.ndim != 4 or noise_scale.shape[2:] != (1, 1):
            raise ValueError(f"Invalid `noise_scale` shape: expected [batch_size, channels, 1, 1], "
                                f"but got {list(noise_scale.shape)}")

    # if `noise_bias` or `noise_scale` is zero scalar then ignore it
    if isinstance(noise_bias, (float,int)) and noise_bias == 0:
        noise_bias = None
    if isinstance(noise_scale, (float,int)) and noise_scale == 1:
        noise_scale = None

    # adjust any empty latent to have the shape required by the model
    if fix_empty_latent:
        latents = comfy.sample.fix_empty_latent_channels(model, latents)

    # store original values in case the user is doing inpainting with a mask
    original_samples : torch.Tensor | None = latents
    original_mask    : torch.Tensor | None = noise_mask

    # apply extra noise injection if it was required
    if extra_noise_scales and extra_noise_freqs:
        latents = inject_freq_noise(latents,
                                    seed         = noise_seed,
                                    noise_freqs  = extra_noise_freqs,
                                    noise_scales = extra_noise_scales,
                                    )

    # force a full denoising (with the last sigma to zero) if it was required
    if force_final_denoise and sigmas[-1] != 0:
        sigmas = sigmas.clone()
        sigmas[-1] = 0


    # generate the noise needed by `comfy.sample.sample_custom(..)`;
    # if both `noise_scale` and `noise_bias` are 0, then no noise is generated
    if isinstance(noise_scale, (float,int)) and noise_scale == 0 and noise_bias is None:
        comfy_noise = torch.zeros(latents.shape,
                                  dtype   = latents.dtype,
                                  layout  = latents.layout,
                                  device  = "cpu")
    else:
        comfy_noise = generate_noise(noise_seed, latents.shape,
                                     noise_bias     = noise_bias,
                                     noise_scale    = noise_scale,
                                     batch_subseeds = batch_subseeds,
                                     dtype          = latents.dtype,
                                     layout         = latents.layout,
                                     device         = "cpu")


    # this wrapper modifies the progress report sent by comfyui
    # to show an external progress from 0 to 100
    steps = _num_steps(sigmas)
    progress_wrapper = ProgressPreview( steps+1, parent=(progress_preview, 100/(steps+2), 100) )

    # generates the denoised latent using a native function from comfyui
    disable_pbar = not comfy.utils.PROGRESS_BAR_ENABLED
    latents = comfy.sample.sample_custom(model, comfy_noise, cfg, sampler, sigmas, positive, negative,
                                         latents, noise_mask=noise_mask, callback=progress_wrapper,
                                         disable_pbar=disable_pbar, seed=noise_seed)

    # when there's an inpainting mask, it seems like comfyui does not merge the
    # original image at the end of `sample_custom(..)`, so we manually merge it here
    if keep_masked_area and (original_mask is not None) and (original_samples is not None):
        original_mask = comfy.sampler_helpers.prepare_mask( original_mask, original_samples.shape, original_samples.device)
        if original_mask is not None:
            latents = latents * original_mask + ( 1.0 - original_mask ) * original_samples

    return latents


#============================ NOISE PROCESSING =============================#

def estimate_initial_noise_features(comfy_latent : ComfyLatent,
                                    model        : ComfyModel,
                                    positive     : ComfyConditioning,
                                    negative     : ComfyConditioning,
                                    *,
                                    seed         : int,
                                    sampler      : comfy.samplers.KSAMPLER,
                                    sigmas       : list | torch.Tensor,
                                    sample_bias  : float = 0.0,
                                    sample_scale : float = 0.1,
                                    sample_size  : tuple[int, int] | int | None = None,
                                    progress_preview: ProgressPreview
                                    ) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Calculates bias and scale of the resultant latent image after denoising.

    The bias and scale are determined by denoising a pure noise sample with the
    provided sigma values, then calculating the mean and standard deviation
    across each channel of the resulting latent image.

    Args:
        latent_image : Dictionary containing information about the initial latent image,
                       only its width and height are used.
        model        : ComfyUI object representing the model to use for denoising.
        seed         : The seed used to generate random noise.
        positive     : Positive prompts or conditioning applied to the model during denoising.
        negative     : Negative prompts or conditioning applied to the model during denoising.
        sampler      : ComfyUI object representing the sampler used for each denoising step.
        sigmas       : Sigma values for each diffusion process step (can be list or torch.Tensor).
        sample_size  : The size in pixels of the sample. If `None`, the size of the latent image is used.
        sample_bias  : The bias of the pure noise sample before denoising.
        sample_scale : The scale of the pure noise sample before denoising.
        progress_preview: An object for reporting progress.

    Returns:
        A tuple containing two tensors:
        - The calculated noise bias, tensor of shape [batch_size, channels, 1, 1].
        - The calculated noise scale, tensor of shape [batch_size, channels, 1, 1].
    """
    latents: torch.Tensor | None = comfy_latent.get("samples")
    if latents is None:
        raise ValueError("comfy_latent must contain 'samples' key")

    # force sigmas to be a torch.Tensor
    if isinstance(sigmas, list):
        sigmas = torch.tensor(sigmas, device='cpu')

    # if sample_size is an integer, it is assumed to be a square image
    if isinstance(sample_size, int):
        sample_size = (sample_size, sample_size)

    # if sample_size is supplied,
    # the 'latents' is replaced by an empty one of the specified size
    if isinstance(sample_size, (tuple,list)) and len(sample_size)>=2:
        width, height = sample_size[0], sample_size[1]
        if width>=8 and height>=8:
            latents_shape = latents.shape[:-2] + ( int(height//8), int(width//8) )
            latents = torch.zeros(latents_shape, dtype=latents.dtype, layout=latents.layout, device="cpu")

    # run the sampler on pure noise and calculate the mean of the result
    latents = _iterative_denoising(latents, model, positive, negative,
                                   cfg                 = 1.0,
                                   sigmas              = sigmas,
                                   sampler             = sampler,
                                   noise_scale         = sample_scale,
                                   noise_bias          = sample_bias,
                                   noise_seed          = seed,
                                   force_final_denoise = False,
                                   progress_preview = progress_preview
                                   )
    bias  = latents.mean(dim=[2, 3], keepdim=True)
    scale = latents.std (dim=[2, 3], keepdim=True)
    return bias, scale


#================================= HELPERS =================================#

def _num_steps(sigmas: torch.Tensor | None) -> int:
    """Returns the number of sampling steps represented in the sigmas tensor."""
    return sigmas.shape[-1]-1 if sigmas is not None else 0


def _valid_conditioning(conditioning: ComfyConditioning | None, *,
                        default     : ComfyConditioning
                        ) -> ComfyConditioning:
    """
    Returns the provided comfyui conditioning if it is valid, otherwise returns the default.
    Args:
        conditioning        : The conditioning to be validated.
        default_conditioning: The fallback conditioning to use if the provided one is invalid.
    Returns:
        A valid comfyui conditioning, either from the input or the default.
    """
    if isinstance(conditioning,(list,tuple)) and len(conditioning) > 0:
        return conditioning
    return default

# def _is_empty_conditioning(comfy_conditioning: ComfyConditioning | None) -> bool:
#     """Returns True if the conditioning tensor is empty or None."""
#     if comfy_conditioning is None:
#         return True
#     if isinstance(comfy_conditioning,(list,tuple)) and len(comfy_conditioning) == 0:
#         return True
#     return False


#============================== SIGMA PRESETS ==============================#

# Sigmas are divided into 3 stages:
#
#   Stages 1 and 2 combined function similarly to a standard denoising process,
#   but with two key conditions:
#     - stage 1 always has fixed sigmas regardless of the total number of steps used.
#     - there's a jump-back in sigmas between stage 1 and stage 2, there's no continuity.
#       I'm not sure why it works, but after hundreds of tests where the final image
#       consistently had better quality, I had to accept that this was a rule and it
#       needed to be this way.
#
#   Once stages 1 and 2 are complete (acting as a standard denoising process), stage 3 begins.
#   This is essentially a refining stage, where we go back with the sigmas, add the corresponding
#   noise, and then do denoising from there.
#
#   Since the penultimate sigma of Stage 2 is always larger than the first sigma of Stage 3,
#   the transition from Stage 2 to Stage 3 can also be thought of as applying an "Euler-ancestral"
#   sampling method instead of the standard "Euler", but only for that single step between stages.
#
BRAVO_SIGMA_PRESET = (
    (###3steps
        (0.991, 0.920),                             #< +1 step
        (0.942, 0.000),                             #< +1 step  | = 2 generation steps
        (0.710, 0.000),                             #< +1 step  | + 1 refiner step
    ),(#4steps
        (0.991, 0.920),                             #< +1 step
        (0.935, 0.789, 0.000),                      #< +2 steps | = 3 generation steps
        (0.710, 0.000),                             #< +1 step  | + 1 refiner step
    ),(#5steps
        (0.991, 0.920),                             #< +1 step
        (0.935, 0.789, 0.000),                      #< +2 steps | = 3 generation steps
        (0.658, 0.302, 0.000),                      #< +2 steps | + 2 refiner steps
    ),(#6steps
        (0.991, 0.920),                             #< +1 step
        (0.935, 0.770, 0.690, 0.000),               #< +3 steps | = 4 generation steps
        (0.658, 0.302, 0.000),                      #< +2 steps | + 2 refiner steps
    ),(#7steps
        (0.991, 0.920),                             #< +1 step
        (0.935, 0.900, 0.875, 0.800, 0.000),        #< +4 steps | = 5 generation steps
        (0.658, 0.302, 0.000),                      #< +2 steps | + 2 refiner steps
    ),(#8steps
        (0.991, 0.920),                             #< +1 step
        (0.935, 0.900, 0.875, 0.820, 0.750, 0.000), #< +5 steps | = 6 generation steps
        (0.658, 0.302, 0.000),                      #< +2 steps | + 2 refiner steps
    ),(#9steps
        (0.991, 0.920),                             #< +1 step
        (0.935, 0.900, 0.875, 0.820, 0.750, 0.000), #< +5 steps | = 6 generation steps
        (0.658, 0.4556, 0.200, 0.000),              #< +3 steps | + 3 refiner steps
    )
)
ALPHA_SIGMA_PRESET = (
    (###3steps
        (0.991, 0.980, 0.920),                      #< +2 steps
        (0.942, 0.000),                             #< +1 step  | = 3 generation steps
        None,                                       #< (no refiner)
    ),(#4steps
        (0.991, 0.980, 0.920),                      #< +2 steps
        (0.942, 0.000),                             #< +1 step  | = 3 generation steps
        (0.790, 0.000),                             #< +1 step  | + 1 refiner step
    ),(#5steps
        (0.991, 0.980, 0.920),                      #< +2 steps
        (0.942, 0.780, 0.000),                      #< +2 steps | = 4 generation steps
        (0.620, 0.000),                             #< +1 step  | + 1 refiner step
    ),(#6steps
        (0.991, 0.980, 0.920),                      #< +2 steps
        (0.942, 0.780, 0.000),                      #< +2 steps | = 4 generation steps
        (0.658, 0.302, 0.000),                      #< +2 steps | + 2 refiner steps
    ),(#7steps
        (0.991, 0.980, 0.920),                      #< +2 steps
        (0.935, 0.892, 0.760, 0.000),               #< +3 steps | = 5 generation steps
        (0.658, 0.302, 0.000),                      #< +2 steps | + 2 refiner steps
    ),(#8steps
        (0.991, 0.980, 0.920),                      #< +2 steps
        (0.935, 0.900, 0.875, 0.750, 0.000),        #< +4 steps | = 6 generation steps
        (0.658, 0.302, 0.000),                      #< +2 steps | + 2 refiner steps
    ),(#9steps
        (0.991, 0.980, 0.920),                      #< +2 steps
        (0.935, 0.900, 0.875, 0.750, 0.000),        #< +4 steps | = 6 generation steps
        (0.658, 0.456, 0.200, 0.000),               #< +3 steps | + 3 refiner steps
    )
)

SIGMA_PRESETS_BY_NAME = {
    "alpha"  : ALPHA_SIGMA_PRESET,
    "bravo"  : BRAVO_SIGMA_PRESET,
}

#=== DISCARDED SIGMA PRESETS ===
#
# C_SIGMA_PRESET = (
#     (   (0.992, 0.977, 0.917),                #< 2 steps
#         (0.948, 0.000),                       #< 1 step  (=3 generation steps)
#         None,                                 #< (no refiner)
#     ),(
#         (0.992, 0.977, 0.917),                #< 2 steps
#         (0.948, 0.000),                       #< 1 step  (=3 generation steps)
#         (0.700, 0.000),                       #< 1 step  (+1 refiner step)
#     ),(
#         (0.992, 0.977, 0.917),                #< 2 steps
#         (0.948, 0.740, 0.000),                #< 2 steps (=4 generation steps)
#         (0.700, 0.000),                       #< 1 step  (+1 refiner step)
#     ),(
#         (0.992, 0.977, 0.917),                #< 2 steps
#         (0.948, 0.828, 0.570, 0.000),         #< 3 steps (=5 generation steps)
#         (0.700, 0.000),                       #< 1 step  (+1 refiner step)
#     ),(
#         (0.992, 0.977, 0.917),                #< 2 steps
#         (0.948, 0.828, 0.570, 0.000),         #< 3 steps (=5 generation steps)
#         (0.700, 0.280, 0.000),                #< 2 steps (+2 refiner steps)
#     ),(
#         (0.992, 0.977, 0.917),                #< 2 steps
#         (0.948, 0.858, 0.725, 0.540, 0.000),  #< 4 steps (=6 generation steps)
#         (0.700, 0.280, 0.000),                #< 2 steps (+2 refiner steps)
#     ),(
#         (0.992, 0.977, 0.917),                #< 2 steps
#         (0.948, 0.858, 0.725, 0.540, 0.000),  #< 4 steps (=6 generation steps)
#         (0.708, 0.586, 0.270, 0.000),         #< 3 steps (+3 refiner steps)
#     )
#)
#
# D_SIGMA_PRESET = (
#     (
#         (0.990, 0.981, 0.911),                #< 2 steps
#         (0.943, 0.850, 0.775, 0.640, 0.000),  #< 4 steps (=6 generation steps)
#         (0.608, 0.486, 0.270, 0.000),         #< 3 steps (+3 refiner steps)
#     )
# )
# E_SIGMA_PRESET = (
#     (
#         (0.990, 0.980, 0.913),                #< 2 steps
#         (0.941, 0.858, 0.725, 0.540, 0.000),  #< 4 steps (=6 generation steps)
#         (0.708, 0.586, 0.270, 0.000),         #< 3 steps (+3 refiner steps)
#     )
# )
#
# Alternative 8/7-step sigma sequences discarded in the early stages of development
# if steps==8:
#     sigma0  = 1.000
#     sigmas1 = [0.991, 0.980, 0.920]
#     sigmas2 = [0.935, 0.8916, 0.7895, 0.000],
#     sigmas3 = [0.6582, 0.3019, 0.0000]
# if steps==7:
#     sigma0  = 1.000
#     sigmas1 = [0.991, 0.980, 0.920]
#     sigmas2 = [0.935, 0.770, 0.000]
#     sigmas3 = [0.6582, 0.3019, 0.0000]
#

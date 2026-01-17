"""
File    : zsampler_turbo.py
Purpose : Node for denoising latent images using a set of custom sigmas with Z-Image Turbo (ZIT)
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jan 16, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImageNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                              ComfyUI-ZImageNodes
             Experimental ComfyUI nodes for the Z-Image model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

  ComfyUI V3 schema documentation can be found here:
  - https://docs.comfy.org/custom-nodes/v3_migration

_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
"""
import torch
import comfy.utils
import comfy.sample
import comfy.samplers
from typing             import Any
from comfy_api.latest   import io
from .core.system       import logger
from .core.progress_bar import ProgressPreview


class ZSamplerTurbo(io.ComfyNode):
    xTITLE         = "ZSampler Turbo"
    xCATEGORY      = None
    xCOMFY_NODE_ID = None
    xDEPRECATED    = None

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
                io.Model.Input       ("model"       , tooltip="The model used for generating the latent images."),
                io.Conditioning.Input("positive"    , tooltip="The conditioning used to guide the generation process toward the desired content."),
                io.Latent.Input      ("latent_input", tooltip="The initial latent image to be modified; typically an 'Empty Latent' for text-to-image or an encoded image for img2img."),
                io.Int.Input         ("seed"        , tooltip="The seed used for the random noise generator, ensuring the same result is produced with the same value.",
                                                      default=0, min=0, max=0xffffffffffffffff, control_after_generate=True),
                io.Int.Input         ("steps"       , tooltip="The number of iterations to be performed during the sampling process.",
                                                      default=9, min=4, max=9, step=1),
                io.Float.Input       ("denoise"     , tooltip="The amount of denoising applied, lower values will maintain the structure of the initial image allowing for image to image sampling.",
                                                      default=1.0, min=0.98, max=1.00, step=0.01),
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
                latent_input: dict[str, any],
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
                               latent_image : dict[str, any],
                               *,
                               progress_preview: ProgressPreview | None = None,
                               ) -> dict[str, any]:
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

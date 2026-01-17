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
            inputs=[
                io.Model.Input       ("model"       , tooltip="The model used for generating the latent images."),
                io.Conditioning.Input("positive"    , tooltip="The conditioning used to guide the generation process toward the desired content."),
                io.Latent.Input      ("latent_input", tooltip="The initial latent image to be modified; typically an 'Empty Latent' for text-to-image or an encoded image for img2img."),
                io.Int.Input         ("seed"        , tooltip="The seed used for the random noise generator, ensuring the same result is produced with the same value.",
                                                      default=0, min=0, max=0xffffffffffffffff, control_after_generate=True),
                io.Int.Input         ("steps"       , tooltip="The number of iterations to be performed during the sampling process.",
                                                      default=9, min=7, max=9, step=1),
                io.Float.Input       ("denoise"     , tooltip="The amount of denoising applied, lower values will maintain the structure of the initial image allowing for image to image sampling.",
                                                      default=1.0, min=0.0, max=1.0, step=0.01),
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

        sampler  = comfy.samplers.sampler_object("euler")
        progress = ProgressPreview.from_comfyui(model, 9)
        latent_output = cls.execute_sampler_custom(model, True, seed, 1.0, positive, positive, sampler,
                                                   sigmas           = [0.991, 0.98, 0.92],
                                                   latent_image     = latent_input,
                                                   progress_preview = ProgressPreview(2, parent=(progress,0,2)),
                                                   )
        latent_output = cls.execute_sampler_custom(model, False, seed, 1.0, positive, positive, sampler,
                                                   sigmas           = [0.935, 0.90, 0.875, 0.750, 0.0000],
                                                   latent_image     = latent_output,
                                                   progress_preview = ProgressPreview(4, parent=(progress,2,6)),
                                                   )
        latent_output = cls.execute_sampler_custom(model, True, 696969, 1.0, positive, positive, sampler,
                                                   sigmas           = [0.6582, 0.4556, 0.2000, 0.0000],
                                                   latent_image     = latent_output,
                                                   progress_preview = ProgressPreview(3, parent=(progress,6,9)),
                                                   )
        return io.NodeOutput(latent_output)



    #__ internal functions ________________________________

    @classmethod
    def execute_sampler_custom(cls,
                               model,
                               add_noise,
                               noise_seed,
                               cfg,
                               positive,
                               negative,
                               sampler,
                               sigmas,
                               latent_image : dict[str, any],
                               *,
                               progress_preview: ProgressPreview | None = None,
                               ) -> dict[str, any]:

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

            #x0_output = {}
            #callback = latent_preview.prepare_callback(model, sigmas.shape[-1] - 1, x0_output)

            disable_pbar = not comfy.utils.PROGRESS_BAR_ENABLED
            samples = comfy.sample.sample_custom(model, noise, cfg, sampler, sigmas, positive, negative, samples, noise_mask=noise_mask, callback=progress_preview, disable_pbar=disable_pbar, seed=noise_seed)

            out = latent_image.copy()
            out["samples"] = samples
            return out

            # if "x0" in x0_output:
            #     x0_out = model.model.process_latent_out(x0_output["x0"].cpu())
            #     if samples.is_nested:
            #         latent_shapes = [x.shape for x in samples.unbind()]
            #         x0_out = comfy.nested_tensor.NestedTensor(comfy.utils.unpack_latents(x0_out, latent_shapes))
            #     out_denoised = latent.copy()
            #     out_denoised["samples"] = x0_out
            # else:
            #     out_denoised = out
            # return (out, out_denoised)


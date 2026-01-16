"""
File    : zsampler.py
Purpose : Node for denoising latent images with a set of custom sigmas.
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jan 16, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImageNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                              ComfyUI-ZImageNodes
             Experimental ComfyUI nodes for the Z-Image model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

    The V3 schema documentation can be found here:
    - https://docs.comfy.org/custom-nodes/v3_migration

"""
from comfy_api.latest import io
from .core.system     import logger


class ZSampler(io.ComfyNode):
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
                io.Conditioning.Input("positive"    , tooltip="The conditional text prompts to embed in the latent image."),
                io.Latent.Input      ("latent_input", tooltip="The latent image to denoise."),
                io.Int.Input         ("seed"        , tooltip="The seed to use for the random number generator."),
            ],
            outputs=[
                io.Latent.Output(display_name="latent_output", tooltip="The latent image after denoising."),
            ]
        )

    #__ FUNCTION __________________________________________
    @classmethod
    def execute(cls, model, positive, latent_input, seed) -> io.NodeOutput:
        return io.NodeOutput(latent_input)


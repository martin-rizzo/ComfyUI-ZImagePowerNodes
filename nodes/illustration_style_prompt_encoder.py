"""
File    : illustration_style_prompt_encoder.py
Purpose : Node that converts a text prompt into an embedding, automatically
          adaptando el prompt to the selected illustrative style.
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
from comfy_api.latest            import io
from .core.system                import logger
from .styles.base                import apply_style_to_prompt
from .styles.illustration_styles import ILLUSTRATION_STYLES


class IllustrationStylePromptEncoder(io.ComfyNode):
    xTITLE         = "Illustration-Style Prompt Encoder"
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
                "Transforms a text prompt into an embedding, adapted to the selected illustrative style. "
                "This node takes a prompt, adjusts its visual style according to the chosen option, and "
                "then encodes it using the provided text encoder to generate an embedding that will guide "
                "image generation."
            ),
            inputs=[
                io.Clip.Input  ("clip"      , tooltip="The CLIP model used for encoding the text."),
                io.Combo.Input ("style_name", options=cls.style_names(), tooltip="The style you want for your image."),
                io.String.Input("text"      , multiline=True, dynamic_prompts=True, tooltip="The prompt to encode."),
            ],
            outputs=[
                io.Conditioning.Output(tooltip="The encoded text used to guide the image generation."),
            ]
        )

    #__ FUNCTION __________________________________________
    @classmethod
    def execute(cls, clip, style_name: str, text: str) -> io.NodeOutput:

        prompt = text
        if style_name in ILLUSTRATION_STYLES:
            prompt = apply_style_to_prompt(prompt, ILLUSTRATION_STYLES[style_name], spicy_impact_booster=False)

        if clip is None:
            raise RuntimeError("ERROR: clip input is invalid: None\n\nIf the clip is from a checkpoint loader node your checkpoint does not contain a valid clip or text encoder model.")
        tokens = clip.tokenize(prompt)
        return io.NodeOutput( clip.encode_from_tokens_scheduled(tokens) )


    @classmethod
    def style_names(cls) -> list[str]:
        return ["none"] + ILLUSTRATION_STYLES.get_style_names()


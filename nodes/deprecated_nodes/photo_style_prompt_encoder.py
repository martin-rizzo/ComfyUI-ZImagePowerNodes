"""
File    : photo_style_prompt_encoder.py
Purpose : Node that converts a text prompt into an embedding, automatically
          adapting the prompt to match the selected photographic style.
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jan 16, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

    The V3 schema documentation can be found here:
    - https://docs.comfy.org/custom-nodes/v3_migration

"""
from typing                    import Final
from functools                 import cache
from comfy_api.latest          import io
from ..core.style              import StyleSet
from ..data.predefined_styles  import PREDEFINED_STYLES
_STL_VERSION: Final[str] = "0.8.0" #< the version of style definitions this node uses


class PhotoStylePromptEncoder(io.ComfyNode):
    xTITLE         = "Photo-Style Prompt Encoder"
    xDESCRIPTION   = (
        "Transforms a text prompt into an embedding, adapted to the selected photographic style. "
        "This node takes a prompt, adjusts its visual style according to the chosen option, and "
        "then encodes it using the provided text encoder to generate an embedding that will guide "
        "image generation."
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
                io.Clip.Input  ("clip",
                                tooltip="The CLIP model used for encoding the text."
                               ),
                io.String.Input("customization", optional=True, multiline=True, force_input=True,
                                tooltip=(
                                  'An optional multi-line string to customize existing styles. '
                                  'Each style definition must start with ">>>" followed by the style name, and then include '
                                  'its description on the next lines. The description should incorporate "{$@}" where the '
                                  'main text prompt will be inserted.'),
                               ),
                io.Combo.Input ("style_to_apply", options=cls.style_names(),
                                tooltip="The style you want for your image.",
                               ),
                io.String.Input("text", multiline=True, dynamic_prompts=True,
                                tooltip="The prompt to encode.",
                               ),
            ],
            outputs=[
                io.Conditioning.Output(tooltip="The encoded text used to guide the image generation."),
                io.String.Output(tooltip="The prompt after applying the selected photographic style."),
            ]
        )

    #__ FUNCTION __________________________________________
    @classmethod
    def execute(cls, clip, style_to_apply: str, text: str, customization: str = "") -> io.NodeOutput:
        prompt        = text
        style         = style_to_apply if isinstance(style_to_apply, str) else "none"
        custom_styles = StyleSet.from_string(customization)

        # try to find the definition of the style selected by the user,
        # first search inside the custom styles that the user has defined (if any),
        # if not found, then try to find it in the predefined styles
        style_obj = custom_styles.get(style)
        if not style_obj:
            style_obj = PREDEFINED_STYLES.by_version(_STL_VERSION).get(style)

        # if the style was found, apply it to the prompt
        if style_obj:
            prompt = style_obj.apply_to_prompt(prompt)

        # generate the embeddings and output them
        tokens = clip.tokenize(prompt)
        return io.NodeOutput( clip.encode_from_tokens_scheduled(tokens), prompt )


    @staticmethod
    @cache
    def style_names() -> list[str]:
        return (
            ["none"]
            + list( PREDEFINED_STYLES.by_version(_STL_VERSION).by_category("photo").names() )
        )


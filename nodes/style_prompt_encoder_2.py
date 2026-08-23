"""
File    : style_prompt_encoder_2.py
Purpose : Node to get conditioning embeddings from a given style + prompt (version 2)
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jan 16, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

 ComfyUI V3 Schema oficial documentation:
 - https://docs.comfy.org/custom-nodes/v3_migration

"""
from typing                   import Final
from functools                import cache
from comfy_api.latest         import io
from .core.style              import StyleSet
from .data.predefined_styles  import PREDEFINED_STYLES
from .                        import widgets as zi
_STL_VERSION: Final[str] = "1.0.0" #< the version of style definitions this node uses


class StylePromptEncoder2(io.ComfyNode):
    xTITLE         = "Style & Prompt Encoder"
    xDESCRIPTION   = (
        "Transforms a text prompt into embeddings, automatically adapting the prompt to match "
        "the selected style. This node takes a prompt, adjusts its visual style according to "
        "the chosen option, and then encodes it using the provided text encoder (clip) to "
        "generate an embedding that will guide image generation."
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
                io.Clip.Input           ("clip",
                                         tooltip="The CLIP model used for encoding the text."
                                        ),
                io.String.Input         ("customization",
                                         optional=True, multiline=True, force_input=True,
                                         tooltip="An optional multi-line string to customize existing styles. "
                                                 "Each style definition must start with '>>>' followed by the "
                                                 "style name, and then include its description on the next lines. "
                                                 "The description should incorporate '{$@}' where the main text "
                                                 "prompt will be inserted.",
                                        ),
                io.Combo.Input          ("style",
                                         options=cls.style_names(),
                                         tooltip="The style you want for your image.",
                                        ),
                zi.StyleGalleryButton.Input("gallery",
                                         version="1.0", dialog_title="Select Style",
                                         tooltip="Open the style gallery to see all available styles."
                                        ),

                zi.Separator.Input("spacer", mode="spacer"),#======================================

                io.String.Input("text",
                                multiline=True, dynamic_prompts=True,
                                tooltip="The prompt to encode.",
                               ),
            ],
            outputs=[
                io.Conditioning.Output(tooltip="The encoded text used to guide the image generation."),
                io.String.Output(tooltip="The prompt after applying the selected visual style."),
            ]
        )

    #__ FUNCTION __________________________________________
    @classmethod
    def execute(cls,
                clip,
                style         : str,
                text          : str,
                customization : str = "",
                **kwargs
                ) -> io.NodeOutput:
        prompt        = text
        custom_styles = StyleSet.from_string(customization)

        # try to find the definition of the style selected by the user,
        # first search inside the custom styles that the user has defined (if any),
        # if not found, then try to find it in the predefined styles
        style_obj = custom_styles.get(style)
        if not style_obj:
            style_obj = PREDEFINED_STYLES.by_version(_STL_VERSION).get(style)

        # apply the style template to the prompt
        if style_obj:
            prompt = style_obj.apply_to_prompt(prompt, spicy_impact_booster=False)

        # encode the prompt using the provided text encoder (clip)
        tokens = clip.tokenize(prompt)
        return io.NodeOutput( clip.encode_from_tokens_scheduled(tokens), prompt )


    #__ VALIDATION ________________________________________
    @classmethod
    def validate_inputs(cls, **kwargs) -> bool | str:
        return True


    #__ internal functions ________________________________

    @staticmethod
    @cache
    def style_names() -> list[str]:
        """Returns all available style names."""
        return (
            ["none"]
            + list( PREDEFINED_STYLES.by_version(_STL_VERSION).quoted_names() )
        )



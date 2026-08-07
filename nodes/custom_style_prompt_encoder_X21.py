"""
File    : custom_style_prompt_encoder_X21.py
Purpose : Experimental node to get conditioning embeddings from a given CUSTOM style + color + prompt
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jul 27, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

 ComfyUI V3 Schema oficial documentation:
 - https://docs.comfy.org/custom-nodes/v3_migration

"""
from typing                    import Final
from functools                 import cache
from comfy_api.latest          import io
from .core.style               import StyleSet
from .data.predefined_styles   import PREDEFINED_STYLES
from .data.predefined_palettes import PREDEFINED_PALETTES
from .custom_widgets           import CustomStyleSelector, PaletteSelector
_STL_VERSION: Final[str] = "2.0.0" #< the version of style definitions this node uses
_PAL_VERSION: Final[str] = "2.0.0" #< the version of palette definitions this node uses


class CustomStylePromptEncoderX21(io.ComfyNode):
    xTITLE         = "Custom Style + Prompt Encoder ^G2.1"
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
                "Transforms a text prompt into embeddings, automatically adapting the prompt to match "
                "the selected style and, optionally, a chosen colour palette. This node takes a prompt, "
                "adjusts its visual style according to the chosen option (applying the palette if "
                "provided), and then encodes it using the supplied CLIP model to generate an embedding "
                "that will guide image generation. "
                "Because this node is experimental, its parameters, behaviour, or existence "
                "may change or be removed entirely without prior notice. "
            ),
            inputs=[
                io.Clip.Input            ("clip",
                                          tooltip="The CLIP model used for encoding the text."
                                         ),
                io.String.Input          ("custom_styles",
                                          optional=False, multiline=True, force_input=True,
                                          tooltip="An optional multi-line string to customize existing styles. "
                                                  "Each style definition must start with '>>>' followed by the "
                                                  "style name, and then include its description on the next lines. "
                                                  "The description should incorporate '{$@}' where the main text "
                                                  "prompt will be inserted.",
                                         ),
                CustomStyleSelector.Input("custom_style",
                                          options=['Custom 1', 'Custom 2', 'Custom 3', 'Custom 4', 'Custom 5'],
                                          tooltip="The customized visual style to apply to the prompt. "
                                         ),
                PaletteSelector.Input    ("palette",
                                          version=_PAL_VERSION, allow_variants=False, dialog_title="Color Palettes | ⚗️ experimental",
                                          dialog_size="small", dialog_view_mode="list", dialog_icon="mdi.mdi-palette-outline",
                                          tooltip="The color palette to use for enhancing the prompt. "
                                         ),
                io.String.Input          ("prompt",
                                          multiline=True, dynamic_prompts=True,
                                          tooltip="The base text prompt to be encoded and styled. "
                                         ),
            ],
            outputs=[
                io.Conditioning.Output(tooltip="Final encoded text that will guide the image generation process."),
                io.String.Output("PROMPT", tooltip="Final prompt after applying the selected visual style and color palette."),
                io.String.Output("style_name"     , tooltip="Name of the visual style that was applied to the prompt."),
                io.String.Output("palette_name"   , tooltip="Name of the color palette that was applied to the prompt."),
                io.String.Output("original_prompt", tooltip="The original text input before any modifications or style adaptations."),

            ]
        )

    #__ FUNCTION __________________________________________
    @classmethod
    def execute(cls,
                clip,
                custom_style  : str,
                palette       : str,
                prompt        : str,
                custom_styles : str = "",
                **kwargs
                ) -> io.NodeOutput:
        custom_styles_obj = StyleSet.from_string(custom_styles)

        # try to find the definition of the style selected by the user,
        # first search inside the custom styles that the user has defined (if any),
        # if not found, then try to find it in the predefined styles
        style_obj = custom_styles_obj.get(custom_style)
        if not style_obj:
            style_obj = PREDEFINED_STYLES.by_version(_STL_VERSION).get(custom_style)

        # find the palette that the user has selected
        palette_obj = PREDEFINED_PALETTES.by_version(_PAL_VERSION).get(palette)

        # apply the style template to the prompt
        if style_obj:
            prompt = style_obj.apply_to_prompt(prompt, palette=palette_obj, spicy_impact_booster=False)

        # encode the prompt using the provided text encoder (clip)
        tokens = clip.tokenize(prompt)
        return io.NodeOutput( clip.encode_from_tokens_scheduled(tokens), prompt, custom_style, palette, prompt )


    #__ VALIDATION ________________________________________
    @classmethod
    def validate_inputs(cls, **kwargs) -> bool | str:
        return True


    #__ internal functions ________________________________


"""
File    : style_prompt_encoder_X22_advanced.py
Purpose : Experimental node to get conditioning embeddings from a given style + color + prompt (second/third Gen).
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Aug 21, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

 ComfyUI V3 Schema oficial documentation:
 - https://docs.comfy.org/custom-nodes/v3_migration

"""
from comfy_api.latest  import io
from .core.style       import Style, StyleSet
from .core.palette     import Palette, PaletteSet
from .                 import widgets as zi


class StylePromptEncoderX22Advanced(io.ComfyNode):
    xTITLE         = "Style + Prompt Encoder ^X2.2 (Advanced)"
    xDESCRIPTION   = (
        "Transforms a text prompt into embeddings, automatically adapting the "
        "prompt to match the selected style and chosen color palette. "
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
                io.Clip.Input   ("clip",
                                 tooltip="The CLIP model used for encoding the text."
                                ),
                io.String.Input ("user_styles",
                                 optional=True, multiline=True, force_input=True,
                                 tooltip="An optional multi-line string to customize existing styles. "
                                         "Each style definition must start with '>>>' followed by the "
                                         "style name, and then include its description on the next lines. "
                                         "The description should incorporate '{$@}' where the main text "
                                         "prompt will be inserted.",
                                ),
                io.String.Input ("user_palettes",
                                 optional=True, multiline=True, force_input=True,
                                 tooltip="An optional multi-line string to customize existing styles. "
                                         "Each style definition must start with '>>>' followed by the "
                                         "style name, and then include its description on the next lines. "
                                         "The description should incorporate '{$@}' where the main text "
                                         "prompt will be inserted.",
                                ),
                zi.Style.Input  ("style",
                                 user_input="user_styles", style_marker=">>>", include_none=True,
                                 tooltip="The visual style to be applied to the input prompt. "
                                ),
                zi.Palette.Input("palette",
                                 user_input="user_palettes", palette_marker=">>>", include_none=True,
                                 tooltip="The visual style to be applied to the input prompt. "
                                ),
                io.String.Input ("prompt",
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
                prompt       : str,
                style        : str | Style      | None = None,
                palette      : str | Palette    | None = None,
                user_styles  : str | StyleSet   | None = None,
                user_palettes: str | PaletteSet | None = None,
                ) -> io.NodeOutput:

        # if style is a name (instead of a Style object),
        # resolve it from the provided user styles
        if isinstance(style, str):
            # resolve the `StyleSet` based on the type of user_styles
            if   isinstance(user_styles, StyleSet): style_set = user_styles
            elif isinstance(user_styles, str):      style_set = StyleSet.from_string(user_styles)
            else:                                   style_set = StyleSet()
            style = style_set.get(style)

        # if palette is a name (instead of a Palette object),
        # resolve it from the provided user palettes
        if isinstance(palette, str):
            # resolve the `PaletteSet` based on the type of user_palettes
            if   isinstance(user_palettes, PaletteSet): palette_set = user_palettes
            elif isinstance(user_palettes, str):        palette_set = PaletteSet.from_string(user_palettes)
            else:                                       palette_set = PaletteSet()
            palette = palette_set.get(palette)

        # apply the style template to the prompt
        if isinstance(style, Style):
            prompt = style.apply_to_prompt(prompt, palette=palette)

        # encode the prompt using the provided text encoder (clip)
        tokens = clip.tokenize(prompt)
        return io.NodeOutput( clip.encode_from_tokens_scheduled(tokens), prompt, style, palette, prompt )


    #__ VALIDATION ________________________________________
    @classmethod
    def validate_inputs(cls, **kwargs) -> bool | str:
        return True



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
from typing                     import Final
from comfy_api.latest           import io
from ..core.style               import StyleSet
from ..core.palette             import Palette
from ..data.predefined_styles   import PREDEFINED_STYLES
from ..data.predefined_palettes import PREDEFINED_PALETTES
from ..                         import widgets as zi
_STL_VERSION: Final[str] = "2.0.0" #< the version of style definitions this node uses
_PAL_VERSION: Final[str] = "2.0.0" #< the version of palette definitions this node uses


class CustomStylePromptEncoderX21(io.ComfyNode):
    xTITLE         = "Custom Style + Prompt Encoder ^X2.1"
    xDESCRIPTION   = (
        "Encodes a text prompt into embeddings by automatically adapting it to a selected "
        "custom style (and an optional colour palette), which are then processed by a "
        "CLIP model to generate the conditioning that guides image generation. "
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
            search_aliases=["text", "prompt", "text prompt", "positive prompt", "encode text",
                            "text encoder", "encode prompt", "styles", "custom styles"],
            inputs=[
                io.Clip.Input             ("clip",
                                           tooltip="The CLIP model used for encoding the text."
                                          ),
                io.String.Input           ("custom_styles",
                                           optional=False, multiline=True, force_input=True,
                                           tooltip="A multi-line string defining custom styles. Each definition must "
                                                   "start with '>>>' followed by the style name, and then the style "
                                                   "description on the next lines. Include '{$@}' in the description "
                                                   "where the base prompt should be inserted.",
                                          ),
                zi.CustomStyle.Input      ("custom_style",
                                           user_input="custom_styles",
                                           tooltip="The visual style to be applied to the input prompt. "
                                          ),
                zi.PredefinedPalette.Input("palette",
                                           version=_PAL_VERSION, force_input=True, optional=True,
                                           tooltip="An optional color palette to use to enhance the prompt's visual description.",
                                          ),
                io.String.Input           ("prompt",
                                           multiline=True, dynamic_prompts=True,
                                           tooltip="The base text prompt to be encoded and styled. "
                                          ),
            ],
            outputs=[
                io.Conditioning.Output(tooltip="The final encoded conditioning that will guide the image generation process."),
                io.String.Output("PROMPT"         , tooltip="The processed prompt after applying the selected visual style and color palette."),
                io.String.Output("style_name"     , tooltip="The name of the visual style applied."),
                io.String.Output("palette_name"   , tooltip="The name of the color palette applied."),
                io.String.Output("original_prompt", tooltip="The original text input before any modifications."),
            ]
        )

    #__ FUNCTION __________________________________________
    @classmethod
    def execute(cls,
                clip,
                custom_style : str,
                prompt       : str,
                custom_styles: str,
                palette      : str | Palette | None = None,
                **kwargs
                ) -> io.NodeOutput:
        custom_styles_obj = StyleSet.from_string(custom_styles)

        # try to find the definition of the style selected by the user,
        # first search inside the custom styles that the user has defined (if any),
        # if not found, then try to find it in the predefined styles
        style_obj = custom_styles_obj.get(custom_style)
        if not style_obj:
            style_obj = PREDEFINED_STYLES.by_version(_STL_VERSION).get(custom_style)

        # if palette is just a name, get the object from the predefined palettes
        if isinstance(palette, str):
            palette = PREDEFINED_PALETTES.by_version(_PAL_VERSION).get(palette)

        # apply the style template to the prompt
        if style_obj:
            prompt = style_obj.apply_to_prompt(prompt, palette=palette, spicy_impact_booster=False)

        # encode the prompt using the provided text encoder (clip)
        tokens = clip.tokenize(prompt)
        return io.NodeOutput(clip.encode_from_tokens_scheduled(tokens),
                             prompt,
                             custom_style,
                             palette.name if palette else "none",
                             prompt
                             )


    #__ VALIDATION ________________________________________
    @classmethod
    def validate_inputs(cls, **kwargs) -> bool | str:
        return True


    #__ internal functions ________________________________


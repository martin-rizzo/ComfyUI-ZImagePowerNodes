"""
File    : style_string_injector_2.py
Purpose : Inject a visual style into a prompt. (version 2)
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jan 22, 2026
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
from .data.predefined_styles  import PREDEFINED_STYLES
from .                        import widgets as zi
_STL_VERSION: Final[str] = "1.0.0" #< the version of style definitions this node uses


class StyleStringInjector2(io.ComfyNode):
    xTITLE         = "Style String Injector"
    xDESCRIPTION   = (
        "Injects a style to your prompt. This node takes a text prompt and modifies it "
        "according to the selected style"
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
                io.Combo.Input          ("style",
                                         options=cls.style_names(),
                                         tooltip="The visual style you want for your image.",
                                        ),
                zi.StyleGalleryButton.Input("gallery",
                                         version="1.0", dialog_title="Select Style",
                                         tooltip="Open the style gallery to see all available styles."
                                        ),
                io.String.Input         ("string",
                                         multiline=True, dynamic_prompts=True, force_input=True,
                                         tooltip="The prompt to modify.",
                                        ),
            ],
            outputs=[
                io.String.Output(tooltip="The prompt after applying the selected style."),
            ]
        )

    #__ FUNCTION __________________________________________
    @classmethod
    def execute(cls, style: str, string: str, **kwargs) -> io.NodeOutput:
        style_obj = PREDEFINED_STYLES.by_version(_STL_VERSION).get(style)

        # apply the style template to the prompt
        prompt = string
        if style_obj:
            prompt = style_obj.apply_to_prompt(prompt)

        return io.NodeOutput( prompt )


    #__ VALIDATION ________________________________________
    @classmethod
    def validate_inputs(cls, **kwargs) -> bool | str:
        return True



    #__ internal functions ________________________________

    @staticmethod
    @cache
    def style_names() -> list[str]:
        """Returns all available style names."""
        return PREDEFINED_STYLES.by_version(_STL_VERSION).quoted_names()



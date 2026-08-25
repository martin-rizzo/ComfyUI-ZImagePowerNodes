"""
File    : style_string_injector.py
Purpose : 
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
from typing                    import Final
from functools                 import cache
from comfy_api.latest          import io
from ..data.predefined_styles  import PREDEFINED_STYLES
_STL_VERSION: Final[str] = "0.9.0" #< the version of style definitions this node uses


class StyleStringInjector(io.ComfyNode):
    xTITLE         = "Style String Injector (old version)"
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
                io.Combo.Input ("category", options=cls.category_names(),
                                tooltip="The category of styles you want to select from.",
                               ),
                io.Combo.Input ("style", options=cls.style_names(), default=cls.default_style_name(),
                                tooltip="The style you want for your image.",
                               ),
                io.String.Input("string", multiline=True, dynamic_prompts=True, force_input=True,
                                tooltip="The prompt to modify.",
                               ),
            ],
            outputs=[
                io.String.Output(tooltip="The prompt after applying the selected style."),
            ]
        )

    #__ FUNCTION __________________________________________
    @classmethod
    def execute(cls,
                category      : str,
                style         : str,
                string        : str,
                ) -> io.NodeOutput:
        prompt    = string
        style_obj = PREDEFINED_STYLES.by_version(_STL_VERSION).get(style)

        # apply the style template to the prompt
        if style_obj:
            prompt = style_obj.apply_to_prompt(prompt)

        return io.NodeOutput( prompt )


    #__ VALIDATION ________________________________________
    @classmethod
    def validate_inputs(cls, **kwargs) -> bool | str:
        if kwargs["category"] not in cls.category_names():
            return f"The category name '{kwargs['style_type']}' is invalid. May be the node is from an older version."
        return True



    #__ internal functions ________________________________

    @staticmethod
    @cache
    def category_names() -> list[str]:
        """Returns all available category names."""
        return PREDEFINED_STYLES.by_version(_STL_VERSION).categories()


    @staticmethod
    @cache
    def style_names() -> list[str]:
        """Returns all available style names."""
        return (
            ["none"]
            + list( PREDEFINED_STYLES.by_version(_STL_VERSION).quoted_names() )
        )


    @staticmethod
    @cache
    def default_style_name() -> str:
        """Returns the default style name (the first one that is not 'none')."""
        style_names = StyleStringInjector.style_names()
        return style_names[1 if len(style_names)>1 else 0]


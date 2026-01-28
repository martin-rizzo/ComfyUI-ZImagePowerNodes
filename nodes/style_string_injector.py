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
from comfy_api.latest           import io
from .lib.style_group           import StyleGroup
from .styles.predefined_styles  import PREDEFINED_STYLE_GROUPS


class StyleStringInjector(io.ComfyNode):
    xTITLE         = "Style String Injector"
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
                "Injects a style to your prompt. This node takes a text prompt and modifies it "
                "according to the selected style"
            ),
            inputs=[
                io.Combo.Input ("category", options=cls.category_names(), default=cls.default_category_name(),
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
        style_to_apply = None
        prompt         = string

        if isinstance(style, str) and style != "none":
            style_to_apply = cls.get_predefined_style(style)

        # if the style was found, apply it to the prompt
        if style_to_apply:
            prompt = StyleGroup.apply_style_template(prompt, style_to_apply, spicy_impact_booster=False)

        return io.NodeOutput( prompt )


    #__ VALIDATION ________________________________________
    @classmethod
    def validate_inputs(cls, **kwargs) -> bool | str:
        if kwargs["category"] not in cls.category_names():
            return f"The category name '{kwargs['style_type']}' is invalid. May be the node is from an older version."
        return True



    #__ internal functions ________________________________

    @classmethod
    def category_names(cls) -> list[str]:
        """Returns all available category names."""
        return [ group.category for group in PREDEFINED_STYLE_GROUPS ]


    @classmethod
    def style_names(cls) -> list[str]:
        """Returns all available style names."""
        names = ["none"]
        for style_group in PREDEFINED_STYLE_GROUPS:
            names.extend( style_group.get_names(quoted=True) )
        return names


    @classmethod
    def default_category_name(cls) -> str:
        return PREDEFINED_STYLE_GROUPS[0].category


    @classmethod
    def default_style_name(cls) -> str:
        return PREDEFINED_STYLE_GROUPS[0].get_names(quoted=True)[0]


    @classmethod
    def get_predefined_style(cls, style_name: str) -> str:
        """Returns a predefined style content by its name, searching inside all category groups."""
        for style_group in PREDEFINED_STYLE_GROUPS:
            style = style_group.get_style_template(style_name)
            if style:
                return style
        return ""


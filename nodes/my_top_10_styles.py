"""
File    : my_top_10_styles.py
Purpose : Node that lets users select a visual style from their personal top-10.
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jan 31, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

The V3 schema documentation can be found here:
 - https://docs.comfy.org/custom-nodes/v3_migration

"""
from typing                   import Final
from comfy_api.latest         import io
from .core.style              import append_style_to_text, remove_style_from_text
from .data.predefined_styles  import PREDEFINED_STYLES
from .                        import widgets as zi
_STL_VERSION: Final[str] = "1.0.0" #< the version of style definitions this node uses


class MyTop10Styles(io.ComfyNode):
    xTITLE         = "My Top-10 Styles"
    xDESCRIPTION   = (
        "Allows you to select a visual style from your personalized top 10 list. "
        "This node relies on 'My Top-10 Style Editor' to provide the list of your favorite styles."
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
                io.String.Input("input" , optional=True, multiline=True, force_input=True, dynamic_prompts=False,
                                tooltip="Input to chain ther top styles nodes to this one.",
                                ),
                io.Custom("TOP_STYLES").Input( "top_styles", optional=True,
                                tooltip="Configuration with your personal top-10 styles to show in this node.",
                                ),
                io.Boolean.Input( "style_1" , display_name="-", default=False, ),
                io.Boolean.Input( "style_2" , display_name="-", default=False, ),
                io.Boolean.Input( "style_3" , display_name="-", default=False, ),
                io.Boolean.Input( "style_4" , display_name="-", default=False, ),
                io.Boolean.Input( "style_5" , display_name="-", default=False, ),
                io.Boolean.Input( "style_6" , display_name="-", default=False, ),
                io.Boolean.Input( "style_7" , display_name="-", default=False, ),
                io.Boolean.Input( "style_8" , display_name="-", default=False, ),
                io.Boolean.Input( "style_9" , display_name="-", default=False, ),
                io.Boolean.Input( "style_10", display_name="-", default=False, ),

                zi.Separator.Input("divider", mode="divider"),#====================================

                io.Combo.Input( "control_after_generate", options=["fixed", "next"], default="fixed", ),
                io.Combo.Input( "output_to", options=cls.channels(), ),
            ],
            outputs=[
                io.String.Output("output", tooltip="The prompt after applying the selected style."),
            ]
        )

    #__ FUNCTION __________________________________________
    @classmethod
    def execute(cls, /,*, output_to: str, top_styles: list[str], input: str = "", **kwargs) -> io.NodeOutput:

        text    = input
        channel = output_to[len("custom_"):] if output_to.startswith("custom_") else "1"

        # checks which style is active (may not be any)
        selected_index = -1
        for i in range(0, 100):
            if kwargs.get(f"style_{i+1}", False):
                selected_index = i
                break

        # get the selected style name
        selected_name = top_styles[selected_index] if 0 <= selected_index < len(top_styles) else ""

        # adds the selected style template to the input text
        style = PREDEFINED_STYLES.by_version(_STL_VERSION).get(selected_name)
        if style:
            text = remove_style_from_text(text, f"Custom {channel}")
            text = append_style_to_text  (text, f"Custom {channel}", style.template)
        return io.NodeOutput( text )


    #__ VALIDATION ________________________________________
    @classmethod
    def validate_inputs(cls, **kwargs) -> bool | str:
        return True


    #__ internal functions ________________________________

    @classmethod
    def channels(cls) -> list[str]:
        return ["custom_1", "custom_2", "custom_3", "custom_4"]

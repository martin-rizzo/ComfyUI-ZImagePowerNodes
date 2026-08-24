"""
File    : palette_library_v10.py
Purpose : Node to select one of the predefined visual styles (predefined library v1.0)
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Aug 8, 2026
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
from comfy_api.latest         import io
from .core.style              import Style
from .data.predefined_styles  import PREDEFINED_STYLES
from .                        import widgets as zi
_STL_VERSION: Final[str] = "1.0"  # < The version of visual styles that this node provides to the user


class StyleLibraryV10(io.ComfyNode):
    xTITLE         = "Style Library v1.0"
    xDESCRIPTION   = (
        "Provides a selection interface to choose from a wide library of predefined visual styles."
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
            search_aliases=["styles", "visual styles", "predefined style"],
            inputs=[
                zi.PredefinedStyle.Input("style",
                                         version=_STL_VERSION, allow_variants=False,
                                         dialog_title = "Style Library v1.0 | ⚗️experimental",
                                         images_url   = "/zi_power/styles/samples?file={slug}.jpg&size={size}&cb={cachebuster}",
                                         tooltip      = "The visual style to apply to the prompt. "
                                        ),
            ],
            outputs=[
                zi.CustomStyle.Output(tooltip="The selected visual style."),
            ]
        )

    # __ FUNCTION __________________________________________
    @classmethod
    def execute(cls,
                style: str | Style | None,
                ) -> io.NodeOutput:

        # if style is just a name, get the object from the predefined styles collection
        if isinstance(style, str):
            output = PREDEFINED_STYLES.by_version(_STL_VERSION).get(style)

        # if style is already a Style instance, use it directly
        elif isinstance(style, Style):
            output = style

        # anything else is invalid
        else:
            output = None

        return io.NodeOutput( output )


    #__ VALIDATION ________________________________________
    @classmethod
    def validate_inputs(cls, **kwargs) -> bool | str:
        return True


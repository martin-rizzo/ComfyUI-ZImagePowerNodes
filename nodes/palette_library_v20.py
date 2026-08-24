"""
File    : palette_library_v20.py
Purpose : Node to select one of the predefined palettes of colors (predefined library v2.0)
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
from typing                    import Final
from comfy_api.latest          import io
from .core.palette             import Palette
from .data.predefined_palettes import PREDEFINED_PALETTES
from .                         import widgets as zi
_PAL_VERSION: Final[str] = "2.0" #< The version of color palettes that this node provides to the user


class PaletteLibraryV20(io.ComfyNode):
    xTITLE         = "Palette Library v2.0"
    xDESCRIPTION   = (
        "Provides a selection interface to choose from a wide(?) library of predefined color palettes."
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
            search_aliases=["palettes", "colors", "predefined palette", "color palettes"],
            inputs=[
                zi.PredefinedPalette.Input("palette",
                                           version=_PAL_VERSION, allow_variants=False,
                                           dialog_title = "Palette Library v2.0 | ⚗️experimental",
                                           tooltip      = "The color palette to use to enhance the prompt's visual description. ",
                                          ),
            ],
            outputs=[
                zi.CustomPalette.Output(tooltip="The selected color palette."),
            ]
        )

    #__ FUNCTION __________________________________________
    @classmethod
    def execute(cls,
                palette: str | Palette | None,
                ) -> io.NodeOutput:

        # if palette is just a name, get the object from the predefined palettes
        if isinstance(palette, str):
            output = PREDEFINED_PALETTES.by_version(_PAL_VERSION).get(palette)

        # if palette is already a Palette instance, use it directly
        elif isinstance(palette, Palette):
            output = palette

        # anything else is invalid
        else:
            output = None

        return io.NodeOutput( output )


    #__ VALIDATION ________________________________________
    @classmethod
    def validate_inputs(cls, **kwargs) -> bool | str:
        return True



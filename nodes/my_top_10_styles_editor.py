"""
File    : my_top_10_styles_editor.py
Purpose : Node that lets users edit their personal top-10 visual styles.
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
from functools                import cache
from comfy_api.latest         import io
from .data.predefined_styles  import PREDEFINED_STYLES
from .                        import widgets as zi
_STL_VERSION: Final[str] = "1.0.0" #< the version of style definitions this node uses


class MyTop10StylesEditor(io.ComfyNode):
    xTITLE         = "My Top-10 Styles (Editor)"
    xDESCRIPTION   = (
        "Allows you to create a personalized list of your top 10 visual styles, "
        "selecting from all available options to build your ideal collection. "
        "This node is designed to work alongside 'My Top-10 Styles' to define "
        "and utilize your preferred styles."
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
                io.Combo.Input( "style_1" , options=cls.style_names(), ),
                zi.StyleGalleryButton.Input("gallery_1", version="1.0", dialog_title="Select Style 1"),
                zi.Separator.Input("spacer_1", mode="spacer"),#====================================

                io.Combo.Input( "style_2" , options=cls.style_names(), ),
                zi.StyleGalleryButton.Input("gallery_2", version="1.0", dialog_title="Select Style 2"),
                zi.Separator.Input("spacer_2", mode="spacer"),#====================================

                io.Combo.Input( "style_3" , options=cls.style_names(), ),
                zi.StyleGalleryButton.Input("gallery_3", version="1.0", dialog_title="Select Style 3"),
                zi.Separator.Input("spacer_3", mode="spacer"),#====================================

                io.Combo.Input( "style_4" , options=cls.style_names(), ),
                zi.StyleGalleryButton.Input("gallery_4", version="1.0", dialog_title="Select Style 4"),
                zi.Separator.Input("spacer_4", mode="spacer"),#====================================

                io.Combo.Input( "style_5" , options=cls.style_names(), ),
                zi.StyleGalleryButton.Input("gallery_5", version="1.0", dialog_title="Select Style 5"),
                zi.Separator.Input("spacer_5", mode="spacer"),#====================================

                io.Combo.Input( "style_6" , options=cls.style_names(), ),
                zi.StyleGalleryButton.Input("gallery_6", version="1.0", dialog_title="Select Style 6"),
                zi.Separator.Input("spacer_6", mode="spacer"),#====================================

                io.Combo.Input( "style_7" , options=cls.style_names(), ),
                zi.StyleGalleryButton.Input("gallery_7", version="1.0", dialog_title="Select Style 7"),
                zi.Separator.Input("spacer_7", mode="spacer"),#====================================

                io.Combo.Input( "style_8" , options=cls.style_names(), ),
                zi.StyleGalleryButton.Input("gallery_8", version="1.0", dialog_title="Select Style 8"),
                zi.Separator.Input("spacer_8", mode="spacer"),#====================================

                io.Combo.Input( "style_9" , options=cls.style_names(), ),
                zi.StyleGalleryButton.Input("gallery_9", version="1.0", dialog_title="Select Style 9"),
                zi.Separator.Input("spacer_9", mode="spacer"),#====================================

                io.Combo.Input( "style_10", options=cls.style_names(), ),
                zi.StyleGalleryButton.Input("gallery_10", version="1.0", dialog_title="Select Style 10"),
            ],
            outputs=[
                io.Custom("TOP_STYLES").Output("TOP_STYLES",
                                               tooltip="Comma-separated string of 10 top styles.",
                                               ),
            ]
        )

    #__ FUNCTION __________________________________________
    @classmethod
    def execute(cls, **kwargs) -> io.NodeOutput:

        # collect the top styles selected by the user
        top_styles = []
        for i in range(0, 100):

            # build the name of the input widget
            input_id = f"style_{i+1}"
            if input_id not in kwargs:
                break

            # get the name of the selected style
            style_name = kwargs[input_id]
            if not isinstance(style_name,str):
                continue

            # remove quotes from the style name
            if style_name.startswith('"') and style_name.endswith('"'):
                style_name = style_name[1:-1]

            # add the style name to the top-10 styles array
            top_styles.append( style_name )


        # output the top styles as a array of strings
        return io.NodeOutput( top_styles )


    #__ VALIDATION ________________________________________
    @classmethod
    def validate_inputs(cls, **kwargs) -> bool | str:
        #if kwargs["category"] not in cls.category_names():
        #    return f"The category name '{kwargs['style_type']}' is invalid. May be the node is from an older version."
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



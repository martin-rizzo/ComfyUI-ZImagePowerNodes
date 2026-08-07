"""
File    : custom_widgets.py
Purpose : Custom ComfyUI widgets implemented specifically for this project.
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : May 11, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

  The custom types section in the V3 schema documentation can be found here:
   - https://docs.comfy.org/custom-nodes/v3_migration#custom-types

"""
from enum               import Enum
from typing             import cast, Any
from comfy_api.latest   import io

_ALLOWED_DIALOG_SIZES      = ("small", "default")
_ALLOWED_DIALOG_VIEW_MODES = ("grid", "list")

def _get_styles_endpoint(version: str) -> str:
    return f"/zi_power/styles/by_version?v={version}"

def _get_palettes_endpoint(version: str) -> str:
    return f"/zi_power/palettes/by_version?v={version}"

def _prune_dict(d: dict):
    return {k: v for k,v in d.items() if v is not None}


#========================= PALETTE SELECTOR WIDGET =========================#

@io.comfytype(io_type="ZIPN_PALETTE_SELECTOR")
class PaletteSelector:
    #Type = str

    class Input(io.Input):

        def __init__(self,
                     id              : str, *,
                     version         : str  | None = None,
                     endpoint        : str  | None = None,
                     height          : int  | None = None,
                     dialog_title    : str  | None = None,
                     dialog_icon     : str  | None = None,
                     dialog_size     : str  | None = None,
                     dialog_view_mode: str  | None = None,
                     allow_variants: bool | None = None,
                     tooltip         : str  | None = None,
                     ):
            """
            <hr>A color palette selector widget.

            Args:
                id (str):               A unique identifier for the input component.
                version (str):          The version of the palette database to load (e.g., "1.0").
                endpoint (str):         The endpoint to use for loading the palette database.
                                        (if specified then `version` will not be taken into account.)
                height (int):           The height of the widget in pixels.
                dialog_title (str):     The title of the dialog window displayed for palette selection.
                dialog_icon (str):      The icon to display as a prefix of the dialog title.
                                        * For PrimeIcons   : Use "pi.[icon name]" e.g., "pi.pi-image"; (see https://primevue.org/icons/#list)
                                        * For Pictogrammers: Use "mdi.[icon name]" e.g., "mdi.mdi-image"; (see https://pictogrammers.com/library/mdi)
                                        * An empty string removes the icon from the title
                dialog_size (str):      The size of the dialog window. Supported values: "small" or "default".
                dialog_view_mode (str): The view mode for the dialog window. Supported values: "grid" or "list".
                                        If provided, the user cannot change the view mode.
                allow_variants (bool):  If True, the widget treats "//" as a separator in palette names.
                                        The left part is considered the primary name, and the right part
                                        is considered its variation.
                tooltip (str):          A tooltip description for the widget.
            """
            if not version and not endpoint:
                raise ValueError("Either version or endpoint must be specified.")
            if not dialog_title:
                dialog_title = "Select Palette"

            extra_dict: dict[str,Any] = {
                "dialog": {}
            }

            if version is not None:
                default_endpoint = _get_palettes_endpoint(version)
                extra_dict["endpoint"]           = default_endpoint
                extra_dict["dialog"]["endpoint"] = default_endpoint

            if endpoint is not None:
                extra_dict["endpoint"]           = endpoint
                extra_dict["dialog"]["endpoint"] = endpoint

            if height is not None:
                extra_dict["height"] = height

            if dialog_title is not None:
                extra_dict["dialog"]["title"] = dialog_title

            if dialog_icon is not None:
                extra_dict["dialog"]["icon"] = dialog_icon

            if dialog_size is not None:
                extra_dict["dialog"]["size"] = dialog_size
                if dialog_size not in _ALLOWED_DIALOG_SIZES:
                    raise ValueError(f"Invalid dialog size '{dialog_size}'. Allowed values are {_ALLOWED_DIALOG_SIZES}")

            if dialog_view_mode is not None:
                extra_dict["dialog"]["view_mode"] = dialog_view_mode
                if dialog_view_mode not in _ALLOWED_DIALOG_VIEW_MODES:
                    raise ValueError(f"Invalid dialog view '{dialog_view_mode}'. Allowed values are {_ALLOWED_DIALOG_VIEW_MODES}")

            if allow_variants is not None:
                extra_dict["allow_variants"]           = allow_variants
                extra_dict["dialog"]["allow_variants"] = allow_variants

            super().__init__(id, extra_dict=extra_dict, tooltip=cast(str, tooltip))


    class Output(io.Output):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)



#========================== STYLE SELECTOR WIDGET ==========================#
#Type = str

@io.comfytype(io_type="ZIPN_STYLE_SELECTOR")
class StyleSelector:

    class Input(io.Input):

        def __init__(self,
                     id              : str, *,
                     version         : str  | None = None,
                     endpoint        : str  | None = None,
                     images_url      : str  | None = None,
                     height          : int  | None = None,
                     dialog_title    : str  | None = None,
                     dialog_icon     : str  | None = None,
                     dialog_size     : str  | None = None,
                     dialog_view_mode: str  | None = None,
                     allow_variants  : bool | None = None,
                     tooltip         : str  | None = None,
                     ):
            """
            <hr>A visual style selector widget.

            Args:
                id (str):               A unique identifier for the input component.
                version (str):          The version of the style database to load (e.g., "1.0").
                endpoint (str):         The endpoint to use for loading the style database.
                                        (if specified then `version` will not be taken into account.)
                images_url (str):       The template for building the URL of each style preview image.
                height (int):           The height of the widget in pixels.
                dialog_title (str):     The title of the dialog window displayed for style selection.
                dialog_size (str):      The size of the dialog window. Supported values: "small" or "default".
                dialog_view_mode (str): The view mode for the dialog window. Supported values: "grid" or "list".
                                        (if provided, the user cannot change the view mode.)
                allow_variants (bool):  If True, the widget treats "//" as a separator in style names.
                                        The left part is considered the primary name, and the right part
                                        is considered its variation.
                tooltip (str):          A tooltip description for the widget.
            """
            if not version and not endpoint:
                raise ValueError("Either `version` or `endpoint` must be specified.")
            if not images_url:
                raise ValueError("The `images_url` parameter must be specified.")
            if not dialog_title:
                dialog_title = "Select Style"

            extra_dict: dict[str,Any] = {
                "dialog": {}
            }

            if version is not None:
                default_endpoint = _get_styles_endpoint(version)
                extra_dict["endpoint"]           = default_endpoint
                extra_dict["dialog"]["endpoint"] = default_endpoint

            if endpoint is not None:
                extra_dict["endpoint"]           = endpoint
                extra_dict["dialog"]["endpoint"] = endpoint

            if images_url is not None:
                extra_dict["images_url"] = images_url

            if height is not None:
                extra_dict["height"] = height

            if dialog_title is not None:
                extra_dict["dialog"]["title"] = dialog_title

            if dialog_icon is not None:
                extra_dict["dialog"]["icon"] = dialog_icon

            if dialog_size is not None:
                extra_dict["dialog"]["size"] = dialog_size
                if dialog_size not in _ALLOWED_DIALOG_SIZES:
                    raise ValueError(f"Invalid dialog size '{dialog_size}'. Allowed values are {_ALLOWED_DIALOG_SIZES}")

            if dialog_view_mode is not None:
                extra_dict["dialog"]["view_mode"] = dialog_view_mode
                if dialog_view_mode not in _ALLOWED_DIALOG_VIEW_MODES:
                    raise ValueError(f"Invalid dialog view '{dialog_view_mode}'. Allowed values are {_ALLOWED_DIALOG_VIEW_MODES}")

            if allow_variants is not None:
                extra_dict["allow_variants"]           = allow_variants
                extra_dict["dialog"]["allow_variants"] = allow_variants

            super().__init__(id, extra_dict=extra_dict, tooltip=cast(str, tooltip))



    class Output(io.Output):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)


#========================== CUSTOM STYLE SELECTOR ==========================#

@io.comfytype(io_type="ZIPN_CUSTOM_STYLE_SELECTOR")
class CustomStyleSelector:
    Type = str
    class Input(io.WidgetInput):
        """Combo input (dropdown) with auto syncronization of Custom Styles"""
        def __init__(self,
                     id          : str,
                     *,
                     options     : list[str] | list[int] | type[Enum] | None = None,
                     display_name: str  | None              = None,
                     optional    : bool                     = False,
                     tooltip     : str  | None              = None,
                     lazy        : bool | None              = None,
                     default     : str  | int | Enum | None = None,
                    #  control_after_generate: bool | ControlAfterGenerate=None,
                     socketless: bool | None = None,
                     raw_link  : bool | None = None,
                     advanced  : bool | None = None,
                     extra_dict = None,
                    ):

            # extract enum values from `options` and `default`
            if isinstance(options, type) and issubclass(options, Enum):
                options = [v.value for v in options]
            if isinstance(default, Enum):
                default = default.value

            super().__init__(id,
                             display_name = cast(str,display_name),
                             optional     = optional,
                             tooltip      = cast(str,tooltip),
                             lazy         = cast(bool,lazy),
                             default      = default,
                             socketless   = cast(bool,socketless),
                             raw_link     = cast(bool,raw_link),
                             advanced     = cast(bool,advanced),
                             extra_dict   = extra_dict,
                             )
            self.multiselect            = False
            self.options                = options
            self.control_after_generate = None # control_after_generate


        def as_dict(self) -> dict:
            return super().as_dict() | _prune_dict({
                "multiselect"           : self.multiselect,
                "options"               : self.options,
                "control_after_generate": self.control_after_generate,
            })


#============================ SEPARATOR WIDGET =============================#

@io.comfytype(io_type="ZIPN_SEPARATOR")
class Separator:
    #Type = str

    class Input(io.Input):

        def __init__(self,
                     id       : str,
                     mode     : str | None = None,
                     color    : str | None = None,
                     height   : int | None = None,
                     thickness: int | None = None,
                     **kwargs
                     ):
            """
            <hr>A separator widget.

            Args:
                id (str):                  A unique identifier for the input component.
                mode (str, optional):      The visual style of the separator `"spacer"`, `"divider"`, `"dotted"`, `"bold"`.
                                            Defaults to 'spacer'.
                color (str, optional):     The color of the separator. Accepts a hexadecimal color string.
                                            Defaults to '#555555'.
                height (int, optional):    The height of the separator. Defaults to `20`.
                thickness (int, optional): The thickness of the separator. Defaults to `2`.
            """
            ALLOWED_MODES = ("spacer", "divider", "dotted", "bold")
            extra_dict = {}

            if mode is not None:
                if mode not in ALLOWED_MODES:
                    raise ValueError(f"Invalid mode: {mode}. Must be one of {ALLOWED_MODES}")
                extra_dict["mode"] = mode

            if color is not None:
                extra_dict["color"] = color

            if height is not None:
                extra_dict["height"] = height

            if thickness is not None:
                extra_dict["thickness"] = thickness

            super().__init__(id, extra_dict=extra_dict, **kwargs)



    class Output(io.Output):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)


#==================== STYLE GALLERY BUTTON [DEPRECATED] ====================#

@io.comfytype(io_type="ZIPN_STYLE_GALLERY_BUTTON")
class StyleGalleryButton:
    #Type = str

    class Input(io.Input):

        def __init__(self,
                     id              : str,
                     version         : str  | None = None,
                     endpoint        : str  | None = None,
                     dialog_title    : str  | None = None,
                     dialog_icon     : str  | None = None,
                     dialog_size     : str  | None = None,
                     dialog_view_mode: str  | None = None,
                     allow_variants  : bool | None = None,
                     tooltip         : str  | None = None,
                     ):
            """
            <hr>A button that launches the style gallery.

            The selected style by the user within the style gallery
            will be applied to the combobox immediately above this button.

            Args:
                id (str):                A unique identifier for the input component.
                version (str):           The version of the style database to load (e.g., "1.0").
                endpoint (str):          The endpoint to use for loading the style database.
                                         (if specified then `version` will not be taken into account.)
                dialog_title (str):      The title of the dialog window displayed for style selection.
                dialog_icon (str):       The icon to display as a prefix of the dialog title.
                                         * For PrimeIcons   : Use "pi.[icon name]" e.g., "pi.pi-image"; (see https://primevue.org/icons/#list)
                                         * For Pictogrammers: Use "mdi.[icon name]" e.g., "mdi.mdi-image"; (see https://pictogrammers.com/library/mdi)
                                         * An empty string removes the icon from the title
                dialog_size (str):       The size of the dialog window. Supported values: "small" or "default".
                dialog_view_mode (str):  The view mode for the dialog window. Supported values: "grid" or "list".
                                         (if provided, the user cannot change the view mode.)
                allow_variants (bool):   If True, the widget treats "//" as a separator in style names.
                                         The left part is considered the primary name, and the right part
                                         is considered its variation.
                tooltip (str):           A tooltip description for the widget.
            """
            if not version and not endpoint:
                raise ValueError("Either version or endpoint must be specified.")

            extra_dict: dict[str,Any] = {
                "title"     : "Select Style",
                "dialog"    : {},
                "images_url": "/zi_power/styles/samples?file={slug}.jpg&cb={cachebuster}"
            }

            if version is not None:
                version_endpoint = _get_styles_endpoint(version)
                extra_dict["endpoint"] = version_endpoint
                extra_dict["dialog"]["endpoint"] = version_endpoint

            if endpoint is not None:
                extra_dict["endpoint"] = endpoint
                extra_dict["dialog"]["endpoint"] = endpoint

            if dialog_title is not None:
                extra_dict["title"] = dialog_title

            if dialog_title is not None:
                extra_dict["dialog"]["title"] = dialog_title

            if dialog_icon is not None:
                extra_dict["dialog"]["icon"] = dialog_icon

            if dialog_size is not None:
                extra_dict["dialog"]["size"] = dialog_size
                if dialog_size not in _ALLOWED_DIALOG_SIZES:
                    raise ValueError(f"Invalid dialog size '{dialog_size}'. Allowed values are {_ALLOWED_DIALOG_SIZES}")

            if dialog_view_mode is not None:
                extra_dict["dialog"]["view_mode"] = dialog_view_mode
                if dialog_view_mode not in _ALLOWED_DIALOG_VIEW_MODES:
                    raise ValueError(f"Invalid dialog view '{dialog_view_mode}'. Allowed values are {_ALLOWED_DIALOG_VIEW_MODES}")

            if allow_variants is not None:
                extra_dict["dialog"]["allow_variants"] = allow_variants

            super().__init__(id, extra_dict=extra_dict, tooltip=cast(str, tooltip))




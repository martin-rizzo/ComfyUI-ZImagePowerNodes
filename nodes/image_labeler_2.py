"""
File    : image_labeler_2.py
Purpose : Node to label an image with text.
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Aug 12, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

  ComfyUI V3 schema documentation can be found here:
  - https://docs.comfy.org/custom-nodes/v3_migration

_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
"""
import torch
import numpy as np
from PIL                 import Image, ImageDraw, ImageFont
from comfy_api.latest    import io
from .core.helpers_text  import TextBox, load_font
from .                   import widgets as zi


class ImageLabeler2(io.ComfyNode):
    xTITLE         = "Image Labeler"
    xDESCRIPTION   = "Adds a label with custom text to the image."
    xCATEGORY      = ""
    xCOMFY_NODE_ID = ""
    xDEPRECATED    = False

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            display_name  = cls.xTITLE,
            description   = cls.xDESCRIPTION,
            category      = cls.xCATEGORY,
            node_id       = cls.xCOMFY_NODE_ID,
            is_deprecated = cls.xDEPRECATED,
            inputs=[
                io.Image.Input  ("image",
                                 tooltip="Input image to which the label will be added. ",
                                ),
                io.Boolean.Input("enable_label",
                                 tooltip="When enabled, applies the label configuration to the image. "
                                         "If disabled, the image will be displayed without label.",
                                ),

                zi.Separator.Input("divider1", mode="divider"),#===================================

                io.String.Input ("text",
                                 placeholder="label text", multiline=False,
                                 tooltip="Text to be displayed in the label. ",
                                ),
                io.String.Input ("text_color",
                                 default="#FF0000",
                                 tooltip="Color of the label text in hexadecimal format (e.g. #FFFFFF for white). ",
                                ),
                io.String.Input ("background_color",
                                 default="#FFFFFF",
                                 tooltip="Background color of the label in hexadecimal format (e.g. #000000 for black). ",
                                ),
                io.Combo.Input  ("font_name",
                                 default="roboto_slab", options=["roboto_slab", "open_sans"],
                                 tooltip="The font to be used for the label text. ",
                                ),
                io.Int.Input    ("font_size",
                                 default=64, min=8, max=256, step=1,
                                 tooltip="Size of the font used for the label text, the final size will be adjusted "
                                         "automatically in relation to the image height. ",
                                ),
                io.Combo.Input  ("font_scale",
                                 default="none", options=["none", "by_image_width", "by_image_height"],
                                 tooltip="Position of the label on the image, specifying the corner or edge alignment. ",
                                ),
                io.Combo.Input  ("label_position",
                                 default="bottom_right", options=["bottom_left", "bottom_center", "bottom_right"],
                                 tooltip="Position of the label on the image, specifying the corner or edge alignment. ",
                                ),
                io.Int.Input    ("label_padding",
                                 default=-1, min=-1, max=100, step=1,
                                 tooltip="Padding around the label text, measured in pixels. "
                                         "Set this value to -1 for automatic padding adjustment based on font size. ",
                                ),
                io.Int.Input    ("min_label_width",
                                 default=0, min=0, step=16,
                                 tooltip="Minimum width of the label area in pixels, ensuring the label "
                                         "has enough width even if the text is so short. ",
                                ),
                io.Int.Input    ("min_label_height",
                                 default=0, min=0, step=16,
                                 tooltip="Minimum height of the label area in pixels, ensuring the label "
                                         "has enough height even if the font is so small. ",
                                ),
            ],
            outputs=[
                io.Image.Output(
                    tooltip="Output image with the added label containing the specified text. ",
                ),
            ],
        )

    @classmethod
    def execute(cls,
                image           : torch.Tensor,
                enable_label    : bool,
                text            : str,
                text_color      : str,
                background_color: str,
                font_name       : str,
                font_size       : int,
                font_scale      : str,
                label_position  : str,
                label_padding   : int,
                min_label_width : int,
                min_label_height: int,
                **kwargs,
    ) -> io.NodeOutput:

        # if disabled, return image without modification
        if not enable_label:
            return io.NodeOutput(image)

        # extract image information
        batch, height, width, _  = image.shape[-4:]
        device, dtype            = image.device, image.dtype

        h_relpos = 0
        if   label_position == "bottom_left"  : h_relpos = 0.0
        elif label_position == "bottom_center": h_relpos = 0.5
        elif label_position == "bottom_right" : h_relpos = 1.0

        # create the font taking into account the auto scaling
        scale  = 1.0
        if "width" in font_scale:
            scale = width / 1024
        elif "height" in font_scale:
            scale = height / 1024
        font = load_font(font_name, int(font_size * scale))

        # iterate over each image in the batch and add them to the `numpy_images` buffer
        numpy_images_dtype = np.float16
        numpy_images       = np.empty((batch, height, width, 3), dtype=numpy_images_dtype)
        for i in range(batch):

            # convert from tensor to PIL image
            array     = (image[i].cpu().numpy() * 255).clip(0, 255).astype(np.uint8)
            pil_image = Image.fromarray(array)

            # draw the label with the parameters required by the user
            cls.draw_text_label(pil_image, text,
                                text_color = text_color,
                                back_color = background_color,
                                min_size   = (min_label_width, min_label_height),
                                font       = font,
                                padding    = (label_padding, label_padding) if label_padding>=0 else None,
                                h_relpos  = h_relpos,
                                )

            # add PIL image to the `numpy_images` buffer (i, H, W, C)
            numpy_images[i] = np.array(pil_image.convert("RGB"), dtype=numpy_images_dtype) / 255.0

        # return `numpy_images` as a pytorch tensor
        return io.NodeOutput( torch.from_numpy(numpy_images).to(device=device, dtype=dtype) )


    @staticmethod
    def draw_text_label(image : Image.Image,
                        text  : str,
                        text_color : str | tuple[int, int, int],
                        back_color : str | tuple[int, int, int],
                        *,
                        min_size     : tuple[int, int],
                        font         : ImageFont.FreeTypeFont | None,
                        corner_radius: int | None                     = None,
                        padding      : tuple[int, int] | None         = None,
                        h_relpos     : float                          = 0.0
                        ) -> Image.Image:
        """
        Overlay a rounded-rectangle label containing *text* onto *image*.
        The label is attached to one of the four corners (lower-right by default)
        and automatically expands when the requested size is too small to
        contain the text.

        Args:
            image        : Background image to draw onto (modified in-place).
            width        : Requested label width (px).  Will be enlarged if needed.
            height       : Requested label height (px).  Will be enlarged if needed.
            text         : String to display.  Multi-line allowed (`\\n`).
            color        : Text colour, any PIL-accepted specifier, e.g. 'red', '#ff0000'.
            font         : PIL FreeType font object.
            opacity      : 0-255 for the white background (0 = fully transparent).
            corner_radius: Radius of rounded corners.  None → 1/3 of height.
            anchor       : Corner anchor: 'lt', 'rt', 'lb', 'rb' (left/top/right/bottom).
            padding      : (horizontal, vertical) internal margin between text and box.

        Returns:
            The same image object, now with the label drawn on top.
        """
        if not font:
            return image
        draw                      = ImageDraw.Draw(image)
        image_width, image_height = image.size

        if padding is None:
            unit    = TextBox.container_for_text('m', font).width
            padding = ( int(unit), int(unit/2) )

        # 1. Measure text
        text_box    = TextBox.container_for_text(text, font)
        text_width  = int(text_box.width  + padding[0] )
        text_height = int(text_box.height + padding[1] )

        width  = max(min_size[0], text_width )
        height = max(min_size[1], text_height)
        radius = corner_radius if corner_radius is not None else height // 3

        x = (image_width - width) * h_relpos
        left_circle  = (h_relpos > 0.0)
        right_circle = (h_relpos < 1.0)


        # draw the white rectangle
        mainbox = TextBox(0,0,width,height).moved_to(x,image_height, anchor="bl")
        draw.rectangle(mainbox, fill=back_color)

        x_adjust = 0
        if left_circle:
            x_adjust -= radius/2
            circlebox = mainbox.moved_by(-radius,0).with_size( radius*2, radius*2 )
            juttedbox = mainbox.moved_by(-radius,radius).with_size( radius, mainbox.height-radius )
            draw.rectangle(juttedbox, fill=back_color)
            draw.ellipse(  circlebox, fill=back_color)
        if right_circle:
            x_adjust += radius/2
            circlebox = mainbox.moved_by(+radius,0).with_size( radius*2, radius*2, anchor="rt" )
            juttedbox = mainbox.moved_by(+radius,0).with_size( radius, mainbox.height-radius, anchor="rb" )
            draw.ellipse(  circlebox, fill=back_color)
            draw.rectangle(juttedbox, fill=back_color)

        # write the words and return the image
        text_box = text_box.centered_in( mainbox.moved_by(x_adjust,0) )
        draw.text(text_box, text, fill=text_color, font=font, anchor='la')
        return image

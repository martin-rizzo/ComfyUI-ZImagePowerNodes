"""
File    : illustration_style_prompt_encoder.py
Purpose : Node that converts a text prompt into an embedding, automatically
          adapting the prompt to match the selected illustrative style.
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jan 16, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

    The V3 schema documentation can be found here:
    - https://docs.comfy.org/custom-nodes/v3_migration

"""
from comfy_api.latest                import io
from .core.system                    import logger
from .styles.style_group             import StyleGroup
from .styles.predefined_styles_v080  import PREDEFINED_STYLE_GROUPS
ILLUSTRATION_STYLES = next((style_group for style_group in PREDEFINED_STYLE_GROUPS if style_group.category == "illustration"))


class IllustrationStylePromptEncoder(io.ComfyNode):
    xTITLE         = "Illustration-Style Prompt Encoder"
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
                "Transforms a text prompt into an embedding, adapted to the selected illustrative style. "
                "This node takes a prompt, adjusts its visual style according to the chosen option, and "
                "then encodes it using the provided text encoder to generate an embedding that will guide "
                "image generation."
            ),
            inputs=[
                io.Clip.Input  ("clip",
                                tooltip="The CLIP model used for encoding the text.",
                               ),
                io.String.Input("customization", optional=True, multiline=True, force_input=True,
                                tooltip=(
                                  'An optional multi-line string to customize existing styles. '
                                  'Each style definition must start with ">>>" followed by the style name, and then include '
                                  'its description on the next lines. The description should incorporate "{$@}" where the '
                                  'main text prompt will be inserted.'),
                               ),
                io.Combo.Input ("style_to_apply", options=cls.style_names(),
                                tooltip="The style you want for your image.",
                               ),
                io.String.Input("text", multiline=True, dynamic_prompts=True,
                                tooltip="The prompt to encode.",
                               ),
            ],
            outputs=[
                io.Conditioning.Output(tooltip="The encoded text used to guide the image generation."),
                io.String.Output(tooltip="The prompt after applying the selected illustration style."),
            ]
        )

    #__ FUNCTION __________________________________________
    @classmethod
    def execute(cls, clip, style_to_apply: str, text: str, customization: str = "") -> io.NodeOutput:
        prompt        = text
        style_name    = style_to_apply if isinstance(style_to_apply, str) else "none"
        custom_styles = StyleGroup.from_string(customization)

        # try to find the definition of the style selected by the user,
        # first search inside the custom styles that the user has defined (if any),
        # if not found, then try to find it in the predefined styles
        style = custom_styles.get_style_template(style_name) if style_name != "none" else None
        if not style:
            style = ILLUSTRATION_STYLES.get_style_template(style_name)

        # if the style was found, apply it to the prompt
        if style:
            prompt = StyleGroup.apply_style_template(prompt, style, spicy_impact_booster=False)

        # generate the embeddings and output them
        tokens = clip.tokenize(prompt)
        return io.NodeOutput( clip.encode_from_tokens_scheduled(tokens), prompt )


    @classmethod
    def style_names(cls) -> list[str]:
        return ["none"] + ILLUSTRATION_STYLES.get_names()


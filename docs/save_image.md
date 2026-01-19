# Save Image
![text](/docs/save_image.jpg)

This node functions similarly to the native ComfyUI "Save Image" node but includes an option to save images with modified metadata, making them compatible with CivitAI. It simulates nodes that CivitAI can easily recognize, allowing it to automatically extract prompt text and other generation parameters.

## Inputs

### images
The generated images you wish to save.

### filename_prefix
Prefix to add before the automatic image number. This field can even define directories or various variables like `%date:{FORMAT}%`, practically everything allowed by the native ComfyUI node. [More information about save file formatting.](https://blenderneko.github.io/ComfyUI-docs/Interface/SaveFileFormatting)

### civitai_compatible_metadata
Activating this option slightly modifies the image metadata so CivitAI can automatically extract the prompt text and other generation parameters. Deactivating it saves the image as stored by the native ComfyUI node without modifications.

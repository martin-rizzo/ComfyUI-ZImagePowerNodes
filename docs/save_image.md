# Save Image
![Node](/docs/save_image.jpg)

This node works similarly to the native ComfyUI "Save Image" but includes an option to save metadata compatible with CivitAI.  It streamlines the process of sharing your generation parameters on the CivitAI platform by structuring the image metadata in a format that CivitAI readily recognizes.

### CivitAI Metadata Export Process
The process automatically identifies key generation parameters such as prompt, seed, CFG scale, sampler name, and other relevant details. These parameters are then embedded within the image's metadata, making them accessible to CivitAI. The automatic detection mechanism works best with standard ComfyUI workflows or nodes associated with this project. For more complex workflows or third-party nodes that may not be automatically recognized, you can manually tag nodes with ">>C".

### Manual Parameter Extraction with ">>C"
You can append ">>C" to the title of any node you wish to explicitly include in the metadata export. By tagging a node with ">>C", you instruct the process to specifically examine that particular node for common generation parameters (e.g., prompt, seed, sampler name, etc.). Any identifiable parameters found within these tagged nodes will be extracted and included in the CivitAI-compatible metadata, ensuring comprehensive parameter capture even from unrecognized sources.

## Inputs

### images
The generated images you wish to save.

### filename_prefix
Prefix to add before the automatic image number. This field can even define directories or various variables like `%date:{FORMAT}%`, practically everything allowed by the native ComfyUI node. [More information about save file formatting.](https://blenderneko.github.io/ComfyUI-docs/Interface/SaveFileFormatting)

### civitai_compatible_metadata
Activating this option slightly modifies the image metadata so CivitAI can automatically read the prompt text and other generation parameters. Deactivating it saves the image as stored by the native ComfyUI node without modifications.

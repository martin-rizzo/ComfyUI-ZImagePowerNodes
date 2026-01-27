# Save Image
![Node](/docs/save_image.jpg)

This node works similarly to the native ComfyUI "Save Image" but includes an option to save metadata compatible with CivitAI. Internally, it injects nodes that CivitAI can easily recognize, facilitating seamless sharing of generation parameters through this platform.

The process automatically detects relevant parameters such as prompt, seed, CFG scale, sampler name, and others to include them in the image's metadata for CivitAI. This automatic detection works best with simple ComfyUI workflows or custom nodes specific to this project. For more complex workflows or third-party nodes, you can manually specify which parameters to export by appending ">>C" to the node titles.

By adding ">>C" to a node's title, you tag it as a CivitAI parameter exporter. Common parameters will be automatically searched within each tagged node and exported in the image's metadata.

## Inputs

### images
The generated images you wish to save.

### filename_prefix
Prefix to add before the automatic image number. This field can even define directories or various variables like `%date:{FORMAT}%`, practically everything allowed by the native ComfyUI node. [More information about save file formatting.](https://blenderneko.github.io/ComfyUI-docs/Interface/SaveFileFormatting)

### civitai_compatible_metadata
Activating this option slightly modifies the image metadata so CivitAI can automatically read the prompt text and other generation parameters. Deactivating it saves the image as stored by the native ComfyUI node without modifications.

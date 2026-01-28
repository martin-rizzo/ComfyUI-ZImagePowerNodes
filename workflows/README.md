# Z-Image Power Nodes Example Workflows

 * `/_dev_`               : Folder containing draft or experimental workflows used during development.
 * `/deprecated`          : Folder containing workflows using deprecated nodes that are no longer supported.
 * `/safetensors_versions`: Folder containing versions of workflows that use .safetensors checkpoint files.
 * `z-image_turbo_main_workflow.json`: Main example workflow for using Z-Image Power Nodes in text-to-image generation.

## Requirements

To use these workflows, you need to have "Z-Image Power Nodes" installed in ComfyUI.  
It can be installed via the ComfyUI Manager or downloaded from its respective repository.

### Installation via ComfyUI Manager (Recommended)

 - Open ComfyUI and click on the "Manager" button to launch the "ComfyUI Manager Menu".
 - Within the ComfyUI Manager, locate and click on the "Custom Nodes Manager" button.
 - In the search bar, type "Z-Image Power Nodes".
 - Select the option from the search results and click the "Install" button.
 - Restart ComfyUI to ensure the changes take effect.

### Manual Installation

 For manual installation, follow the instructions provided in the GitHub repository of the project:
 - https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes


## Recommended Checkpoints

### GGUF Format

GGUF checkpoints tend to run slightly slower in ComfyUI. However, if you are building
a complex workflow that involves other models or using heavy LLMs with ollama, GGUF
files can help prevent system freezes and OOM errors during generation, especially
when VRAM is limited. For simple image generation workflows, a safetensors file
(though heavier) might be preferable. When working with GGUF in Z-Image, from my
experience, using the Q5_K_S quantization typically offers the best balance between
file size and prompt response.

> [!IMPORTANT]
> ComfyUI does not natively support GGUF format, so you need to have installed https://github.com/city96/ComfyUI-GGUF

- "z_image_turbo-Q5_K_S.gguf" [5.19 GB]
  [ Download ]( https://huggingface.co/jayn7/Z-Image-Turbo-GGUF/blob/main/z_image_turbo-Q5_K_S.gguf )  
  Local Directory: `ComfyUI/models/diffusion_models/`

- "Qwen3-4B.i1-Q5_K_S.gguf" [2.82 GB]
  [ Download ]( https://huggingface.co/mradermacher/Qwen3-4B-i1-GGUF/blob/main/Qwen3-4B.i1-Q5_K_S.gguf )  
  Local Directory: `ComfyUI/models/text_encoders/`

- "ae.safetensors" [335 MB]
  [ Download ]( https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/vae/ae.safetensors )  
  Local Directory: `ComfyUI/models/vae/`

### Safetensors Format

Safetensors files are generally larger, but ComfyUI includes several built-in optimizations
to speed up generation even with limited VRAM. It's always a good idea to test the original
safetensors checkpoints on your system to see how they perform. However, using safetensors
in fp8 format is strongly discouraged as it can significantly reduce quality. If you have
an RTX 50 series GPU based on Blackwell architecture, NVFP4 quantized safetensors could be
a better choice.

- "z_image_turbo_bf16.safetensors" [12.3 GB]
  [ Download ]( https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors )  
  Local Directory: `ComfyUI/models/diffusion_models/`

- "qwen_3_4b.safetensors" [8.04 GB]
  [ Download ]( https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/text_encoders/qwen_3_4b.safetensors )  
  Local Directory: `ComfyUI/models/text_encoders/`

- "ae.safetensors" [335 MB]
  [ Download ]( https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/vae/ae.safetensors )  
  Local Directory: `ComfyUI/models/vae/`


## License

Copyright (c) 2026 Martin Rizzo  
This project is licensed under the MIT license.  
See the "LICENSE" file for details.


## More Info

- https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes


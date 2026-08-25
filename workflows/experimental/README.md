
# Z-Image Power Nodes - Experimental Workflows

__Workflows__
 * `z-image-turbo__t2i_double_trouble.json`: Text-to-image workflow combining two different styles.
 * `z-image-turbo__text2image.json` : Text-to-image generation workflow.


## Experimental

These workflows are experimental or utilize nodes in an experimental state, and
they are likely to be integrated into the upcoming version. They are designed to
leverage the latest ComfyUI features such as Nodes 2.0, Subgraphs, ConvRot,
ComfyKitchen-Attention, etc.


## Requirements

- ComfyUI v0.14 or higher (or v0.27+ if using INT8-ConvRot)
- Z-Image Power Nodes v2.1 or higher

Additionally, ensure that the Z-Image Turbo related checkpoints (in GGUF or
Safetensors format) are placed in the appropriate directories within your
ComfyUI setup.

If you choose to use GGUF-format checkpoints, you must also have the
"ComfyUI-GGUF" extension installed, as ComfyUI does not natively support GGUF
files. Once installed, the Power Nodes will automatically detect GGUF checkpoints.  
More information about the GGUF extension can be found at:
    https://github.com/city96/ComfyUI-GGUF


## Checkpoint Files

The loading nodes included in Power Nodes support both .safetensors and GGUF
files (provided that ComfyUI-GGUF is installed).

The following list contains recommended checkpoints, selected because they
performed best during testing. Given the diversity of GPUs, VRAM capacities,
and ComfyUI setups, results may vary. I recommend testing different options
to find the best configuration for your system.

While the Power Nodes were tested using the recommended checkpoints below, they
should also be compatible with other "Z-Image Turbo" checkpoints and LoRAs.
However, full functionality cannot be guaranteed for all custom combinations,
and you may need to tweak workflows for your specific setup.

### Safetensors (INT8-ConvRot)

 - "z_image_turbo_int8_convrot_bf16emixed.safetensors" | 6.17 GB |
   [ Download ]( https://huggingface.co/martin-rizzo/Z-Image-Turbo-INT8-ConvRot-ComfyUI/blob/main/z_image_turbo_int8_convrot_bf16emixed.safetensors )  
   Local Directory: `ComfyUI/models/diffusion_models/`

 - "qwen3-4b_int8_convrot_fp16emixed.safetensors" | 4.42 GB |
   [ Download ]( https://huggingface.co/martin-rizzo/Qwen3-4B-INT8-ConvRot-ComfyUI/blob/main/qwen3-4b_int8_convrot_fp16emixed.safetensors )  
   Local Directory: `ComfyUI/models/text_encoders/`

 - "Z-Image_half_natural_vae.safetensors" | 335 MB |
   [ Download ]( https://huggingface.co/easygoing0114/Z-Image_clear_vae/blob/main/Z-Image_half_natural_vae.safetensors )  
   Local Directory: `ComfyUI/models/vae/`

### GGUF (Q5/Q8)

- "z_image_turbo-Q5_K_S.gguf" | 5.19 GB |
  [ Download ]( https://huggingface.co/jayn7/Z-Image-Turbo-GGUF/blob/main/z_image_turbo-Q5_K_S.gguf )  
  Local Directory: `ComfyUI/models/diffusion_models/`

- "Qwen3-4B-Q8_0.gguf" | 4.28 GB |
  [ Download ]( https://huggingface.co/Qwen/Qwen3-4B-GGUF/blob/main/Qwen3-4B-Q8_0.gguf )  
  Local Directory: `ComfyUI/models/text_encoders/`

 - "Z-Image_half_natural_vae.safetensors" | 335 MB |
   [ Download ]( https://huggingface.co/easygoing0114/Z-Image_clear_vae/blob/main/Z-Image_half_natural_vae.safetensors )  
   Local Directory: `ComfyUI/models/vae/`

### Comfy-Org Original Safetensors (BF16)

- "z_image_turbo_bf16.safetensors" | 12.3 GB |
  [ Download ]( https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors )  
  Local Directory: `ComfyUI/models/diffusion_models/`

- "qwen_3_4b.safetensors" | 8.04 GB |
  [ Download ]( https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/text_encoders/qwen_3_4b.safetensors )  
  Local Directory: `ComfyUI/models/text_encoders/`

- "ae.safetensors" | 335 MB |
  [ Download ]( https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/vae/ae.safetensors )  
  Local Directory: `ComfyUI/models/vae/`

### Comfy-Org Original Safetensors (INT8-ConvRot / FP8)

- "z_image_turbo_int8_convrot.safetensors" | 6.20 GB |
  [ Download ]( https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/diffusion_models/z_image_turbo_int8_convrot.safetensors )  
  Local Directory: `ComfyUI/models/diffusion_models/`

- "qwen_3_4b_fp8_mixed.safetensors" | 5.63 GB |
  [ Download ]( https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/text_encoders/qwen_3_4b_fp8_mixed.safetensors )  
  Local Directory: `ComfyUI/models/text_encoders/`

- "ae.safetensors" | 335 MB |
  [ Download ]( https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/vae/ae.safetensors )  
  Local Directory: `ComfyUI/models/vae/`

### Not Recommended (may be useful on certain systems)

#### Safetensors (FP8)

- "z-image-turbo_fp8_scaled_e4m3fn_KJ.safetensors" | 6.16 GB |
  [ Download ]( https://huggingface.co/Kijai/Z-Image_comfy_fp8_scaled/blob/main/z-image-turbo_fp8_scaled_e4m3fn_KJ.safetensors )  
  Local Directory: `ComfyUI/models/diffusion_models/`

- "qwen3_4b_fp8_scaled.safetensors" | 4.41 GB |
  [ Download ]( https://huggingface.co/hhsebsb/qwen3-4b-fp8-scaled/blob/main/qwen3_4b_fp8_scaled.safetensors )  
  Local Directory: `ComfyUI/models/text_encoders/`

- "ae.safetensors" | 335 MB |
  [ Download ]( https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/vae/ae.safetensors )  
  Local Directory: `ComfyUI/models/vae/`


## Z-Image Power Nodes Installation

Z-Image Power Nodes can be installed via ComfyUI Manager or cloned directly
from the repository. Always ensure you are running the latest version.

__Installation via ComfyUI Manager (Recommended):__

 - Open ComfyUI and click **Manager** to open the menu.
 - Click **Custom Nodes Manager**.
 - Search for "Z-Image Power Nodes".
 - Click **Install** on the matching result.
 - Restart ComfyUI to apply changes.

__Manual Installation:__

Please follow the instructions provided in the GitHub repository:
 - https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes


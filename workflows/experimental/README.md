
# Z-Image Power Nodes: Example Workflows

__Workflows__
 * `z-image-turbo__t2i_double_trouble.json`: Text-to-image workflow combining two different styles.
 * `z-image-turbo__text2image.json` : Text-to-image generation workflow.

## Experimental

These workflows are experimental or utilize nodes in an experimental state, and
they are likely to be integrated into the upcoming version. They are designed to
leverage cutting-edge ComfyUI features such as Subgraphs, ConvRot, ComfyKitchen, etc.

## Requirements

- ComfyUI v0.14 or higher
- Z-Image Power Nodes v2.1 or higher

Additionally, ensure that the Z-Image Turbo related checkpoints (in GGUF or
Safetensors format) are placed in the appropriate directories within your
ComfyUI setup.

If you choose to use GGUF-format checkpoints, it is necessary to have the
"ComfyUI-GGUF" extension installed as well, since ComfyUI does not natively
support GGUF files. Once the extension is installed, the Power Nodes will
automatically detect checkpoints in GGUF format.  
You can find more information about the GGUF extension at:
    https://github.com/city96/ComfyUI-GGUF

## Checkpoint Files

The loading nodes included in the Power Nodes support both `.safetensors` and
GGUF files (provided that ComfyUI-GGUF is installed).

The following list contains recommended checkpoints. I chose these specifically
because they performed best during my testing phase. However, given the diversity
of GPUs, VRAM capacities, and ComfyUI versions, it is very difficult to determine
which one will work best on every system. Therefore, I recommend testing them all
to find the combination that works best for you.

Please be aware that although I tested "Z-Image Power Nodes" using the recommended
checkpoints below, it should also be compatible with other "Z-Image Turbo"
checkpoints and LoRAs. However, I cannot guarantee full functionality for all
custom combinations; you may need to tweak the workflows to optimize them for
your specific setup.

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

## Checkpoints Not Recommended (might be useful on certain systems)

### Safetensors (FP8)

- "z-image-turbo_fp8_scaled_e4m3fn_KJ.safetensors" | 6.16 GB |  
  [ Download ]( https://huggingface.co/Kijai/Z-Image_comfy_fp8_scaled/blob/main/z-image-turbo_fp8_scaled_e4m3fn_KJ.safetensors )  
  Local Directory: `ComfyUI/models/diffusion_models/`

- "qwen3_4b_fp8_scaled.safetensors" | 4.41 GB |  
  [ Download ]( https://huggingface.co/hhsebsb/qwen3-4b-fp8-scaled/blob/main/qwen3_4b_fp8_scaled.safetensors )  
  Local Directory: `ComfyUI/models/text_encoders/`

- "ae.safetensors" | 335 MB |  
  [ Download ]( https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/vae/ae.safetensors )  
  Local Directory: `ComfyUI/models/vae/`

## Z-Image Power Nodes

Z-Image Power Nodes can be installed via ComfyUI Manager or downloaded directly
from its respective repository. Please always ensure you have the latest version
of these nodes installed.

__Installation via ComfyUI Manager (Recommended):__

 - Open ComfyUI and click on the "Manager" button to launch the "ComfyUI Manager Menu".
 - Within the ComfyUI Manager, locate and click on the "Custom Nodes Manager" button.
 - In the search bar, type "Z-Image Power Nodes".
 - Select the option from the search results and click the "Install" button.
 - Restart ComfyUI to ensure the changes take effect.

__Manual Installation:__

For manual installation, please follow the instructions provided in the GitHub repository:
 - https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes


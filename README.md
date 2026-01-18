<div align="center">

# Z-Image Power Nodes <br><sub><sup><i>Pushing the best image generation model to its limits!</i></sup></sub>
[![Platform](https://img.shields.io/badge/platform%3A-ComfyUI-007BFF)](#)
[![License](https://img.shields.io/github/license/martin-rizzo/ComfyUI-ZImagePowerNodes?label=license%3A&color=28A745)](#)
[![Version](https://img.shields.io/github/v/tag/martin-rizzo/ComfyUI-ZImagePowerNodes?label=version%3A&color=D07250)](#)
[![Last](https://img.shields.io/github/last-commit/martin-rizzo/ComfyUI-ZImagePowerNodes?label=last%20commit%3A)](#)

<img src="banner.jpg" width="66%"></img>

</div>

**ComfyUI-ZImagePowerNodes** is a collection of custom nodes designed and refined specifically for the [Z-Image model](https://github.com/Tongyi-MAI/Z-Image). They are based on some ideas and discoveries I made while developing the [Amazing Z-Image Workflow](https://github.com/martin-rizzo/AmazingZImageWorkflow).


## Table of Contents
1. [Installation](#installation)
   - [Installation via ComfyUI Manager (Recommended)](#installation-via-comfyui-manager-recommended)
   - [Manual Installation](#manual-installation)
   - [Windows Portable Installation](#windows-portable-installation)
2. [License](#license)


## Nodes

### ZSampler Turbo

ZSampler Turbo is a specialized sampler designed to divide the denoising process into three stages: composition, details, and refinement. It maintains image stability between 4 to 9 steps and achieves sufficient quality for most cases between 7 to 9 steps, often eliminating the need for further refining or post-processing. This sampler shows improved prompt adherence, especially with the GGUF Q5_K_S checkpoint.
**[ZSampler Turbo documentation](docs/zsampler_turbo.md)**.

### Photo-Style Prompt Encoder

### Illustration-Style Prompt Encoder

### Empty Z-Image Latent Image


## Installation
_Ensure you have the latest version of [ComfyUi](https://github.com/comfyanonymous/ComfyUI)._

### Installation via ComfyUI Manager (Recommended)

The easiest way to install the nodes is through [ComfyUI-Manager](https://github.com/Comfy-Org/ComfyUI-Manager):

  1. Open ComfyUI and click on the "Manager" button to launch the "ComfyUI Manager Menu".
  2. Within the ComfyUI Manager, locate and click on the "Custom Nodes Manager" button.
  3. In the search bar, type "Z-Image Power Nodes".
  4. Select the option from the search results and click the "Install" button.
  5. Restart ComfyUI to ensure the changes take effect.

### Manual Installation

<details>
<summary>🛠️ Manual installation instructions. (expand for details)</summary>
.

1. Open your preferred terminal application.
2. Navigate to your ComfyUI directory:
   ```bash
   cd <your_comfyui_directory>
   ```
3. Move into the **custom_nodes** folder and clone the repository:
   ```bash
   cd custom_nodes
   git clone https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes.git
   ```
</details>

### Windows Portable Installation

<details>
<summary>🛠️ Windows portable installation instructions. (expand for details)</summary>
.

1. Go to where you unpacked **ComfyUI_windows_portable**,  
   you'll find your `run_nvidia_gpu.bat` file here, confirming the correct location.
3. Press **CTRL + SHIFT + RightClick** in an empty space and select "Open PowerShell window here".
4. Clone the repository into your custom nodes folder using:
   ```
   git clone https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes .\ComfyUI\custom_nodes\ComfyUI-ZImagePowerNodes
   ```
</details>

## Recommended Checkpoints

### GGUF Format

<sub>GGUF checkpoints tend to run slightly slower in ComfyUI. However, if you are building a complex workflow that involves other models or using heavy LLMs with ollama, GGUF files can help prevent system freezes and OOM errors during generation, especially when VRAM is limited. For simple image generation workflows, a safetensors file (though heavier) might be preferable. When working with GGUF in Z-Image, from my experience, using the Q5_K_S quantization typically offers the best balance between file size and prompt response. </sub>

 - __[z_image_turbo-Q5_K_S.gguf](https://huggingface.co/jayn7/Z-Image-Turbo-GGUF/blob/main/z_image_turbo-Q5_K_S.gguf)__ <sub>[5.19 GB]</sub>\
   Local Directory: __`ComfyUI/models/diffusion_models/`__
 - __[Qwen3-4B.i1-Q5_K_S.gguf](https://huggingface.co/mradermacher/Qwen3-4B-i1-GGUF/blob/main/Qwen3-4B.i1-Q5_K_S.gguf)__ <sub>[2.82 GB]</sub>\
   Local Directory: __`ComfyUI/models/text_encoders/`__
 - __[ae.safetensors](https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/vae/ae.safetensors)__ <sub>[335 MB]</sub>\
   Local Directory: __`ComfyUI/models/vae/`__

### Safetensors Format

<sub>Safetensors files are generally larger, but ComfyUI includes several built-in optimizations to speed up generation even with limited VRAM. It's always a good idea to test the original safetensors checkpoints on your system to see how they perform. However, using safetensors in fp8 format is strongly discouraged as it can significantly reduce quality. If you have an RTX 50 series GPU based on Blackwell architecture, NVFP4 quantized safetensors could be a better choice.</sub>

 - __[z_image_turbo_bf16.safetensors](https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors)__ <sub>(12.3 GB)</sub>\
   Local Directory: __`ComfyUI/models/diffusion_models/`__
 - __[qwen_3_4b.safetensors](https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/text_encoders/qwen_3_4b.safetensors)__ <sub>(8.04 GB)</sub>\
   Local Directory: __`ComfyUI/models/text_encoders/`__
 - __[ae.safetensors](https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/vae/ae.safetensors)__ <sub>(335 MB)</sub>\
   Local Directory: __`ComfyUI/models/vae/`__



## Example Workflow

<!--
<table>
  <tr>
    <td width="190px">
      <img src="workflows/ximg/zimage-nodes-workflow.png" alt="Z-Image Nodes Workflow" width="171" height="256">
    </td>
    <td>
      The image contains a reference workflow for using and testing the Z-Image model with these nodes.<br/>
      <i>- to load this workflow, simply drag and drop the image into ComfyUI.</i><br/>
      <i>- other workflows are available in the <b><a href="workflows">workflows directory</a></b>.</i> 
    </td>
  </tr>
</table>
-->

## License

Copyright (c) 2026 Martin Rizzo  
This project is licensed under the MIT license.  
See the ["LICENSE"](LICENSE) file for details.
  

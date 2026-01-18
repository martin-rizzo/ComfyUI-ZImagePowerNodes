# ZSampler Turbo

![text](/docs/zsampler_turbo.jpg)

The distinctive feature of this sampler is that it divides the number of steps into three stages: composition, details, and refinement. The sigmas are calculated to keep the image stable from 4 to 9 steps. Naturally, with fewer steps, the final quality decreases, but the resulting images remain quite similar.

Between 7 and 9 steps, the image achieves sufficient quality and detail, making further refining or post-processing unnecessary.

This sampler also enhances prompt adherence, particularly when using the GGUF Q5_K_S checkpoint. (More tests are needed to verify if there's an improvement with safetensors bf16 as well.)

## Inputs

### Model

Any checkpoint from the "Z-Image Turbo" model. This sampler hasn't been extensively tested with LoRAs applied, nor has it been determined which types of LoRA training might benefit from this three-stage sampling process.

### Positive

The positive conditioning input, typically the prompt embedding. There is no negative conditioning because this sampler always operates at CFG 1.0. In the future, it may be worth testing a similar sampling approach with a slightly higher CFG value, but I wanted to avoid adding another variable during testing.

### Latent Input

The latent image to be denoised.

### Steps

Number of denoising steps, which can range from 4 to 9.

### Denoise

This parameter is not currently implemented. The node treats it as if it were always set to 1.0. In the future, implementing this could potentially enable some form of inpainting functionality.

# Empty Z-Image Latent Image
![Node](/docs/empty_zimage_latent_image.jpg)

This node generates an empty latent image specifically formatted for use in Z-Image workflows. It allows users to define key parameters such as orientation, aspect ratio, scale, and batch size, providing a customizable starting point for image generation.

## Inputs

### landscape
 * __true__: Sets the orientation to landscape (horizontal).
 * __false__: Sets the orientation to portrait (vertical).

### ratio
Determines the desired aspect ratio of the image:
 * __1:1  (square)__: Social media posts and profile pictures
 * __4:3  (retro tv)__: Legacy television and older computer monitors
 * __3:2  (photo)__: DSLR cameras and standard 35mm film
 * __16:10  (monitor)__: Common in MacBooks and productivity laptops
 * __16:9  (widescreen)__: Current universal standard for video and TV
 * __2:1  (univisium)__: Modern streaming series and smartphone screens
 * __21:9  (ultrawide)__: Wide cinema format and ultrawide monitors
 * __12:5  (anamorphic)__: Standard theatrical widescreen cinema release
 * __70:27  (cinerama)__: Extreme panoramic cinema format
 * __32:9  (super wide)__: Dual-monitor width for ultra-wide displays

<sub>**Note:** As the aspect ratio becomes more extreme, there is a higher likelihood of visual inconsistencies in the generated image.</sub>

### size
Controls the scale of the latent image:
 * __small__: Lower resolution, ideal for quick previews or low-resource operations.
 * __medium (recommended)__: Higher visual consistency compared to other sizes.
 * __large__: Highest detail level, though may occasionally exhibit slightly reduced coherence.

### batch_size
The number of identical empty latent images to generate simultaneously. This option is useful for parallel processing tasks or creating multiple image variations at once.

## Outputs

### latent
The generated empty latent image ready to be used as the initial canvas in your Z-Image diffusion processes.


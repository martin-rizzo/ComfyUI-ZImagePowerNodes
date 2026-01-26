"""
File    : styles/styles_by_category_v090.py
Purpose : Contain all style definitions grouped by category (v0.9.0)
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jan 25, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
"""
from .style_group import StyleGroup


_PhotoStyles = """
>>>Phone Photo
YOUR CONTEXT:
Your photographs has android phone cam-quality.
Your photographs exhibit {$spicy-content-with} surprising compositions, sharp complex backgrounds, natural lighting, and candid moments that feel immediate and authentic.
Your photographs are actual gritty candid photographic background.
YOUR PHOTO:
{$@}


>>>Casual Photo
YOUR CONTEXT:
You are an amateur documentary photographer taking low quality photos.
Your photographs exhibit {$spicy-content-with} sharp backgrounds, unpolished realism with natural lighting, and candid friendship-level moments that feel immediate and authentic.
YOUR PHOTO:
{$@}


>>>Vintage Photo
YOUR CONTEXT:
You are an 80s photographer who enjoys informal shots.
Your worn vintage photographs exhibit {$spicy-content-with} a minimalist, amateurish composition, warm desaturated tones and a soft focus that creates a cozy atmosphere.
YOUR PHOTO:
{$@}


>>>Portra Film Photo
YOUR CONTEXT:
You are a photographer who appreciates the classic aesthetic of Kodak Portra film.
Your photograph emulates that look, known for its soft colors, fine grain, and natural skin tones. The image features {$spicy-content-with} a subtle warmth, with a focus on accurate color rendition and a gentle, diffused glow. Highlights are smooth and creamy, while shadows retain detail. Minimal post-processing is applied to preserve the organic, film-like quality.
YOUR PHOTOGRAPH:
{$@}


>>>70s Memories Photo
YOUR CONTEXT:
You are a seasoned photographer creating images with a soft, vintage aesthetic reminiscent of 1970-80 film photography. 
The photos display warm, slightly amber tones, gentle buttery highlights, and muted shadows, giving the scene a nostalgic, timeless feel. 
Lighting is natural and diffused—golden-hour sunlight, overcast daylight, or window light filtered through sheer curtains—producing smooth, even illumination without harsh edges. 
Exposure is balanced to preserve detail in both highlights and shadows, resulting in a moderate contrast curve that feels “film-like.” 
A subtle haze or soft-focus effect adds a dreamy, painterly quality, while fine grain (similar to 400 ISO film) provides texture without distracting from the subject. 
Overall, the image looks intimate, elegant, and evocative, as if lifted from a cherished family album or a vintage lifestyle magazine.
YOUR PHOTO:
{$@}


>>>Flash 90s Photo
YOUR CONTEXT:
You are an amateur photographer, taking photos with point-and-shoot cam-quality, in the early 1990s.
Your photographs exhibit {$spicy-content-with} a rough, low-resolution quality, washed-out colors, including a harsh built-in flash, grainy texture, and overexposed highlights, capturing a casual atmosphere that evokes nostalgia.
YOUR PHOTO:
{$@}


>>>Production Photo
YOUR CONTEXT:
You are a Hollywood filmmaker making a high-budget film.
Your photographs exhibit {$spicy-content-with} atmospheric composition that emphasize intense emotions using selective focus, and warm and cold colors with high quality studio lighting.
YOUR PHOTO:
{$@}


>>>Classic Film Photo
YOUR CONTEXT:
You are a professional cinematographer of iconic classic mid-century cinema (1950s-1960s Hollywood golden age).
Your photographs are on 35mm film with grain, displaying {$spicy-content-with} a warm color temperature, and an anamorphic lens that creates imperfections and blurry edges.
YOUR PHOTO:
{$@}


>>>Noir Photo
YOUR CONTEXT:
You are a cinematographer who works in dark movies.
Your photographs exhibit {$spicy-content-with} intense side lighting and gobo-crafted patterns to sculpt deep, sharply defined shadows, along with a muted Ektachrome palette that evokes film noir.
YOUR PHOTO:
{$@}


>>>80s Dark Fantasy Photo
YOUR CONTEXT:
You are a still photographer on the set of a 1980s dark fantasy epic (think *Excalibur*, *Legend*, *Conan the Barbarian*, or *Hawk the Slayer*). The aesthetic is deliberately *not* pristine; it’s a world built with practical effects, visible matte paintings, and a sense of tangible grit.
Your photograph showcases a heavily stylized composition, prioritizing atmosphere over hyper-realism. Lighting is dramatically theatrical, employing saturated colors: deep cobalt blues, fiery oranges and reds, sickly emerald greens, and bruised purples. Strong backlighting and rim lighting are key. Soft focus is used extensively to create a dreamlike quality, but with a slight edge to maintain a sense of danger. Emphasis is placed on creating a sense of scale and grandeur through forced perspective, miniature work, and atmospheric haze.  
Post-processing involves adding noticeable (but not overwhelming) film grain, bloom and glow effects around light sources (especially magical ones), a subtle color shift towards cooler tones, and a slight diffusion to soften details. There's a hint of optical distortion, reminiscent of early anamorphic lenses. The overall mood is one of brooding mystery and impending doom.
YOUR PHOTOGRAPHY:
{$@}


>>>Lomography
YOUR CONTEXT:
You are an adventurous experimental photographer exploring the world through a lomographic lens.
Your photographs exhibit {$spicy-content-with} film grain, colorful lens flares, soft focus with motion blur, and analog filter effects, trying to capture emotions.
YOUR PHOTO:
{$@}


>>>Spotlight Stage Photo
YOUR CONTEXT:
You are a professional stage and theater photographer capturing dramatic performances.
Your photographs exhibit {$spicy-content-with} a single, high-intensity overhead spotlight that creates a sharp circular pool of light, dramatic chiaroscuro contrast that isolates the subject against a pitch-black background, and visible volumetric light beams with subtle dust motes for an authentic theatrical atmosphere.
YOUR PHOTO:
{$@}


>>>Wide Angle / Peephole
YOUR CONTEXT:
Your peephole shows {$spicy-content-with} a shot from a high angle, inside a fisheye lens distortion glass circle, highly distorted with a wide angle.
YOUR PEEPHOLE:
{$@}


>>>Drone Photo
YOUR CONTEXT:
You are an aerial photographer who enjoys using wide-angle drone cams.
Your photographs exhibit {$spicy-content-with} panoramic scenes captured from afar, high up with elevated perspectives and intense colors.
YOUR PHOTO:
{$@}


>>>Minimalist Photo
YOUR CONTEXT:
You are a photographer who prefers serene and tranquil images.
Your photographs exhibit {$spicy-content-with} high contrast and clean, minimalist compositions that emphasize empty space to highlight negative space.
YOUR PHOTO:
{$@}


>>>High-Key Fashion Photo
YOUR CONTEXT:
You are a fashion photographer who creates ultra-bright photos for luxury productions.
Your photograph showcases {$spicy-content-with} a high-key composition shot flooded with soft studio lighting. The exposure is over-lit with white background, eliminating shadows and delivering a crisp, polished look. Colors are saturated yet controlled (vivid reds, cobalt blues, and crisp whites) while the photo has immaculate details thanks to high-resolution capture and minimal post-processing to maintain the airy, glamorous aesthetic.
YOUR PHOTOGRAPH:
{$@} 


>>>Light and Airy Photo
YOUR CONTEXT:
You are a photographer who loves bright, ethereal, and romantic images.
Your photograph is bathed in soft, diffused light, creating a bright and airy aesthetic. Colors are pastel and delicate, with a focus on whites, creams, and light blues. The image features {$spicy-content-with} a shallow depth of field, blurring the background and drawing attention to the subject. Post-processing emphasizes highlights and reduces shadows, resulting in a clean, luminous look.
YOUR PHOTOGRAPH:
{$@}


>>>Teal and Orange Photo
YOUR CONTEXT:
You are a color specialist photographer.
Your photograph showcases {$spicy-content-with} a satured teal and orange colors. The image features cool teal tones in the shadows and highlights, balanced by warm orange tones in the midtones and skin tones, creating a vibrant photography with high contrast and vivid colors.
YOUR PHOTOGRAPH:
{$@}


>>>Orthochromatic Spirit Photo
YOUR CONTEXT:
You are a photographer inspired by the look of early photographic processes, specifically orthochromatic and colorized films.
Your photograph showcases {$spicy-content-with} a scene with a high-contrast, blue-sensitive aesthetic. Reds appear very dark, while blues and greens are bright. The image is characterized by a stark, graphic quality. Post-processing focuses on enhancing the contrast and emphasizing the tonal separation.
YOUR PHOTOGRAPH:
{$@}


>>>Synthwave Photo
YOUR CONTEXT:
You are a photographer inspired by the retro-futuristic visuals of the 1980s.
Your photograph showcases {$spicy-content-with} Synthwave aesthetic, characterized by neon colors and geometric shapes, it includes vibrant pinks, purples, and blues, with a glowing effect. Grids, scanlines, and a retro-futuristic atmosphere. The photograph feels like a scene from a classic 80s sci-fi film.
Real people against a computer-generated background.
YOUR PHOTOGRAPH:
{$@}


>>>Quiet Luxury Photo
YOUR CONTEXT:
You are an editorial fashion photographer specializing in the Old Money aesthetic. 
Your photograph showcases {$spicy-content-with} a sophisticated, clean composition using natural, soft morning light. The color palette is muted and neutral, focusing on beige, cream, navy blue, and forest green. The scene feels expensive and timeless, set in a luxury location. 
YOUR PHOTOGRAPH:
{$@}


>>>Dramatic Light & Shadow
YOUR CONTEXT:
You are a professional photographer specializing in high-impact visual storytelling, with a focus on dramatic lighting and strong contrast.
Your images feature ultra-sharp detail and a color palette that emphasizes deep blacks, punchy primary colors, and selective color isolation.
The lighting is meticulously sculpted: a dominant hard rim-light or a strong directional key-light creates pronounced shadows, while a subtle fill-light preserves texture. 
You deliberately push the exposure to achieve a slight over-exposure in the highlights, producing a glowing effect that draws the eye.
YOUR PHOTO:
{$@}


>>>Street Documentary Photo
YOUR CONTEXT:
You are a documentary photographer chronicling urban life.
Your photograph showcases {$spicy-content-with} candid moments in natural street environments. The image employs a natural color balance, modest contrast, and a shallow depth of field to isolate subjects within bustling scenes. Emphasis is placed on authentic emotion, body language, and the interplay of ambient city light (neon signs, street lamps). Minimal post-processing preserves the raw, honest feel—only slight exposure adjustments and noise reduction are applied to maintain the immediacy of the moment.
YOUR PHOTOGRAPH:
{$@}


>>>Tilt Shift / Toy Photo
YOUR CONTEXT:
You are a photographer who enjoys using tilt-shift lenses to turn real-world scenes into miniature toy models.
Your photographs exhibit {$spicy-content-with} crisp, high-resolution details captured in an exaggerated perspective, with a very narrow focus plane, and a dreamy, toy-like atmosphere that creates the classic “miniature” illusion.
YOUR PHOTO:
{$@}


>>>Pop Photo
YOUR CONTEXT:
You are a contemporary pop artist known for your vibrant, oversaturated palettes and energetic, graphic compositions.
Your photographs exhibit {$spicy-content-with} exaggerated colors and solid backgrounds using Ben-Day dots, achieving an unconventional and clearly pop art effect.
YOUR PHOTO:
{$@}

"""


_IllustrationStyles = """
>>>Comic 1
YOUR CONTEXT:
You are an American artist.
Your illustration has a comic book cover style, with vibrant colors and outlined shapes, featuring {$spicy-content-with} realistic and epic details in the style of modern comics.
YOUR ILLUSTRATION:
{$@}


>>>Comic 2
YOUR CONTEXT:
You are an Italian artist.
Your illustration has a European comic book style, featuring {$spicy-content-with} black hand-drawn outlines, solid colors, realistic anatomical proportions, and cross-hatching for shading.
YOUR ILLUSTRATION:
{$@}


>>>Comic 3
YOUR CONTEXT:
You are a European artist creating fiction worlds.
Your image is a classic ligne claire futurist illustration, featuring {$spicy-content-with} exceptionally clean lines that define each element with the utmost precision. The composition highlights an intense atmosphere with complex technology. The color palette is vibrant, with flat colors and intricate lines and design.
YOUR IMAGE:
{$@}


>>>Action Cover Art
YOUR CONTEXT:
You are a cutting-edge comic artist specializing in high-octane, mature industrial sci-fi where movement is everything.
Your illustration captures a moment of extreme tension featuring {$spicy-content-with} "ink splatters" that suggest violent, rapid motion. The style is technical and sharp, with a focus on high-tech gear, tactical clothing, and urban decay, all rendered with a jittery, energetic hand-drawn line. The composition uses extreme low-angle shots to make the subjects feel powerful and intimidating, while the lighting mimics the cold, flickering strobes of an industrial complex, adding a sense of claustrophobic urgency.
YOUR ILLUSTRATION:
{$@}


>>>Explosive Cover Art
YOUR CONTEXT:
You are a celebrated comic book cover artist, renowned for hyper-realistic action and monumental heroics.
Your cover art is a Dynamic Heroic Realism illustration, characterized by {$spicy-content-with} intricate anatomical accuracy, meticulously rendered textures (fabric, metal, skin), and an explosive sense of motion. The composition often features dramatic foreshortening and a heroic, powerful pose for the central figure, surrounded by dynamic environmental destruction or energy effects. Lighting is grand and directional, sculpting forms with sharp highlights and deep shadows, ensuring every detail contributes to an overwhelming sense of epic scale and immediate impact.
YOUR ILLUSTRATION:
{$@}


>>>Pop-Art
YOUR CONTEXT:
You are a bold artist.
Your illustration features {$spicy-content-with} Pop Art style, characterized by bold vibrant colors. The colors are executed using the pointillist technique, where dots of color come together to create the overall picture. Dazzling patterns and comic style characters. The scene has a flat, two-dimensional appearance typical of pop art aesthetics.
YOUR ILLUSTRATION:
{$@}


>>>Vintage Comic
YOUR CONTEXT:
You are a 1950s artist.
Your illustration in a worn sheet of paper features {$spicy-content-with} a vintage 1950s comic book style made with hand-drawn lines and painted in solid white, red, blue, and black.
YOUR ILLUSTRATION:
{$@}


>>>Vintage Illustration
YOUR CONTEXT:
You are a sci-fi pulp magazine illustrator from the 1940s.
Your drawing is a lush, painted-style comic cover including {$spicy-content-with} dramatic, heroic lighting and a vivid "Technicolor" palette of saturated oranges, deep teals, and bright yellows. It features soft airbrushed textures, muscular anatomy, and a grainy film-stock finish that evokes a sense of retro-futuristic adventure.
YOUR DRAWING:
{$@}


>>>Modern Pin-Up Illustration
YOUR CONTEXT:
You are a specialist in retro-inspired erotic illustration.
Your artwork follows a Vintage Pin-up style, featuring {$spicy-content-with} a charismatic figure posed provocatively within fields of stylized geometry and chromatic gradients. The composition is balanced and symmetrical, employing the “rule of thirds” to place the figure’s gaze and gesture in a way that invites the viewer’s eye across the frame. Lines are sleek and fluid, emphasizing the form and musculature of the figure. Lighting is soft yet directional, reminiscent of studio photography: a luminous aura envelops the skin, while subtle atmospheric shading softens contours, yielding a glossy, almost photographic finish. Color choices are vibrant yet tasteful—teal, cherry red, pastel pink, and ivory—mirroring the palette of classic pin-up posters. Background elements (checkerboard patterns, tonal washes, abstracted forms) are rendered with minimal detail, using gentle gradients and subtle texture to maintain focus on the figure’s dynamic pose.  
YOUR ILLUSTRATION:
{$@}


>>>Manga
YOUR CONTEXT:
You are a Japanese manga artist.
Your illustration features {$spicy-content-with} black and white manga-style that includes manga screentone patterns with high-contrast black and white drawing, in a violent atmosphere. Always imagine colors as shades of gray.
YOUR ILLUSTRATION:
{$@}


>>>Anime
YOUR CONTEXT:
You are a Japanese anime artist.
Your Japanese animation includes {$spicy-content-with} an ominous atmosphere, clean lines, and dramatic facial expressions. The artwork uses cool and dark tones along with dramatic lighting and shadows that emphasize the central figure and create a somber, intense mood.
YOUR DRAWING:
{$@}


>>>Ultimate Anime
YOUR CONTEXT:
You are a top-tier anime key visual artist specializing in high-fidelity CGI rendering. Your goal is to create promotional artwork that blends the expressive character designs of anime with the polished look of modern 3D animation.
The artwork is rendered at 8K (or higher) resolution with perfectly clean linework and seamless anti-aliasing. Color palettes are vibrant and harmonious, adhering to established character designs and world aesthetics.
Lighting is *critical*: a strong key light defines form, rim lighting separates the subject, and soft fill lights preserve detail. Highlights should have a pronounced bloom and subtle lens flares. Shadows are smoothly graded with a focus on realistic light diffusion.
Shading utilizes advanced rendering techniques like physically-based rendering (PBR) to create realistic material properties. Surfaces (skin, hair, fabric, metal) have a polished, three-dimensional feel with subtle subsurface scattering and detailed specular highlights. Avoid overly-stylized cell-shading; aim for a smooth gradient.
Backgrounds are richly composed, utilizing depth-of-field, atmospheric perspective, and subtle particle effects (digital glitches, energy particles, volumetric lighting) to enhance immersion. Backgrounds should *support* the characters, not distract from them.
Linework is clean and confident, with varying line weights to emphasize form. Consider a subtle digital "smoothing" effect to the lines.
Composition is dynamic and emotionally resonant: strong poses, expressive facial features like bright expressive anime eyes, and soft gradients and dynamic strands.  Think about the "rule of thirds" and leading lines.
The overall impression should be that of a high-budget anime promotional image rendered with cutting-edge CGI technology - visually striking, technically flawless, and deeply respectful of the source material. Consider elements like bloom, lens flares, and subtle chromatic aberration.
YOUR ILLUSTRATION:
{$@}


>>>Studio Anime
YOUR CONTEXT:
You are a Japanese anime artist.
Your Japanese animation includes {$spicy-content-with} warm artwork inspired by Studio Ghibli, with detailed characters and a whimsical aesthetic, full of emotion.
YOUR DRAWING:
{$@}


>>>Retro Anime 80s
YOUR CONTEXT:
You are a nostalgic animator who revives the iconic visual language of 1980s Japanese anime. Your artwork captures the era signature aesthetic: bold, angular designs with exaggerated proportions, vibrant primary colors (crimson red, cobalt blue, sunshine yellow), and dramatic, hand-drawn line hatching. The backgrounds feature expansive vistas of geometric objects, and stylized atmospheric formations rendered in a grainy, slightly desaturated texture reminiscent of cel-animation cels. Lighting is dramatic, with strong edge highlights that define form and spark-filled energy emissions, while chromatic aberrations punctuate areas of intense power.
YOUR ILLUSTRATION:
{$@}


>>>Dark Comic Illustration
YOUR CONTEXT:
You are a master of hard-boiled noir graphic novels, specializing in themes of vengeance and the urban underworld. 
Your illustration is a masterclass in high-contrast chiaroscuro, featuring {$spicy-content-with} heavy, ink-drenched shadows and sharp, brutal highlights. The style is raw and visceral, with a focus on shiny surfaces, textured grime, and intense facial expressions that convey deep psychological weight. The composition is cinematic and claustrophobic, using low-angle shots to empower characters and stark lighting to create a sense of impending danger and adult narrative depth.
YOUR ILLUSTRATION:
{$@}


>>> Digital Cyberpunk
YOUR CONTEXT:
You are a digital artist working in a dystopian, technologically advanced future.
Your illustration is a Cyberpunk Noir scene, characterized by {$spicy-content-with} harsh, dramatic lighting that casts long, sharp shadows, reflecting the grimy underbelly of a futuristic scene. It employs a limited color palette dominated by deep blues, neon greens, and stark oranges, giving a mysterious aesthetic.
YOUR ILLUSTRATION:
{$@}


>>>Electric Blue Outline
YOUR CONTEXT:
Your image showcases {$spicy-content-with} a digital cyberpunk draw, characterized by vibrant and saturated colors with solid backgrounds and blue outlines.
YOUR IMAGE:
{$@}


>>>Ink Frenzy
YOUR CONTEXT:
You are an underground street-art comic illustrator.
Your image is a high-energy, chaotic ink drawing featuring {$spicy-content-with} aggressive brush strokes, intentional ink splatters, and "controlled mess" textures. It combines thick, variable-width outlines with vibrant, clashing spray-paint colors. The style is rebellious, modern, and feels like it’s vibrating with motion and urban grit.
YOUR IMAGE:
{$@}


>>>Ink & Shadow
YOUR CONTEXT:
You are a master of hard-boiled noir illustration, prioritizing raw emotional impact through minimalist techniques.
Your illustration is a brutalist, hand-inked work featuring stark black-and-white contrasts with a single, aggressive accent color (like blood red or electric gold). Lines are thick, confident, and jagged, stripping away detail to focus on character and environment. The composition is cinematic and voyeuristic, emphasizing shadows and reflective surfaces.
YOUR ILLUSTRATION:
{$@}


>>>Unsettling
YOUR CONTEXT:
You are an illustrator of dark and disturbing themes.
Your illustration includes {$spicy-content-with} stippling textures, dramatic raking side lighting, and a dread-filled atmosphere that is oppressive and claustrophobic. High contrast emphasizes form and shadow, employing cinematic chiaroscuro for depth.
YOUR DRAWING:
{$@}


>>>Epic Greg
YOUR CONTEXT:
You are a master digital painter specializing in grand-scale heroic fantasy illustrations. Your work evokes the spirit of classic fantasy artists like Frank Frazetta, Boris Vallejo, and Brom.
Your illustration is a meticulously crafted digital oil painting, characterized by masterful, sweeping brushwork and thick impasto textures that give a sense of tangible depth. It features dramatic, cinematic lighting with intense chiaroscuro – light sources like roaring fires, magical energy, or celestial bodies pierce through atmospheric haze, billowing smoke, and swirling clouds. 
The composition is classically inspired, often employing dynamic poses, heroic proportions, and a sense of epic scale.  Details are richly rendered, focusing on textures like weathered armor, flowing fabrics, and rugged landscapes. The palette is a moody blend of deep earth tones (ochres, umbers, siennas) accented by vibrant, glowing highlights (gold, crimson, azure) to create a legendary and immersive feel.  
Consider incorporating elements of high fantasy tropes: mythical creatures, ancient ruins, powerful artifacts, and characters embodying courage, strength, and destiny.
YOUR PAINTING:
{$@}


>>>Cyber Idol
YOUR CONTEXT:
You are an avant-garde Japanese concept artist specializing in futuristic idol culture. Your illustrations fuse the dazzling charisma of J-pop idols with a tech-saturated aesthetic, rendered in a dynamic digital painting style with visible brushstrokes. The visual scheme features a kaleidoscope of neon pinks, electric cyan, ultraviolet, and hot magenta, contrasted against deep, metallic blacks and chrome surfaces, all with a painterly quality. Characters sport elaborate cybernetic accessories—holographic projections, light-emitting garments, and augmented-reality interfaces—rendered with *stylized* reflective materials and *exaggerated* glowing emissive effects. The lighting is multi-layered: radiant atmospheric glows, dynamic energy flares, and shifting chromatic beams that dissect the haze, *interpreted with bold color and dramatic contrast*. Compositionally, you combine tight, charismatic portrait shots with wider views, using *suggested* motion blur and particle effects to convey a pulsating, hyper-connected performance. The overall aesthetic leans towards a vibrant, energetic illustration reminiscent of contemporary anime keyframes.  The background is abstract and dynamic, focusing on light and color rather than a specific location.
YOUR ILLUSTRATION:
{$@}


>>>Minimalist Digital Illustration
YOUR CONTEXT:
You are a cover artist known for powerful, minimalist designs.
Your cover art is a bold graphic iconography piece, featuring {$spicy-content-with} stark, impactful silhouettes and clean, sharp lines that define forms with absolute clarity. The color palette is vibrant, employing large fields of solid color with subtle gradients. Most importantly, the proportions are exaggerated, and the perspective is extremely distorted, creating a sense of vertigo and action.
YOUR ILLUSTRATION:
{$@}


>>>Synthwave Digital Illustration
YOUR CONTEXT:
You are an eclectic digital artist inspired by 80s nostalgia and pastel futurism.
Your illustration follows a Retro Vaporwave aesthetic, featuring {$spicy-content-with} pastel gradients, glitchy raster effects, and abstracted retro signifiers such as fragmented landscapes, digital artifacts, and chromatic distortions. The composition is flat yet layered, with glowing grid lines and reflective surfaces that evoke a dreamy, nostalgic ambience.
YOUR ILLUSTRATION:
{$@}


>>>Whimsical Watercolor
YOUR CONTEXT:
You are an illustrator specializing in gentle, enchanting narratives for children's books.
Your drawing is a whimsical watercolor image, featuring {$spicy-content-with} loose, fluid watercolor washes, delicate linework, and playful, anthropomorphic elements within a lush natural setting. The style is soft and inviting, with a vibrant yet gentle color palette that captures the magic of innocence.
YOUR DRAWING:
{$@}


>>>Modern Ukiyo-e Print
YOUR CONTEXT:
You are a master of traditional Japanese woodblock printing adapted to a modern narrative.
Your illustration features {$spicy-content-with} bold, flowing outlines and flat areas of color with subtle wood-grain textures. The composition uses dramatic perspective typical of "Ukiyo-e" art, with stylized waves, clouds, or smoke, and a color palette of deep indigo, vermillion, and ochre on an aged washi paper background.
YOUR DRAWING:
{$@}


>>>LowRes Pixel Art
YOUR CONTEXT:
You are a pixel artist.
Your illustration is a low-resolution pixel art featuring {$spicy-content-with} chunky pixels and vibrant intense colors, arcade game style.
YOUR ILLUSTRATION:
{$@}

"""



_OtherStyles = """

>>>City Light Poster
YOUR PHOTO:
An eye-level, realistic photo of a glass-encased advertising poster (mupi) located on a clean city sidewalk. There are reflections of nearby buildings and trees on the glass surface. The lighting is natural overcast daylight. The advertising poster is faded and sun-faded, low quality printed advertisement.
POSTER DETAILS:
While the street and buildings are visible in the background, the inside of the poster contains the following:
{$@}


>>>Vintage VGA Monitor
YOUR CONTEXT
An old VGA CRT rectangular monitor sitting on a wooden desk, and a window is reflected on its screen. The monitor's casing has a raised black inscription in the upper left corner that reads "VGA". The screen has a slight curve and sweep lines typical of CRT displays.
INSIDE YOUR MONITOR'S SCREEN:
A low-resolution, 2D pixel art platform videogame form early 1990s.
INSIDE THE VIDEOGAME FROM EARLY 1990s:
{$@}
OUTSIDE YOUR MONITOR'S SCREEN:
A wooden desk and a wall.


>>>Vintage Polaroid Photo
YOUR CONTEXT:
You are a nostalgic photographer who embraces instant film’s tactile charm.
Your Polaroid photograph is using vintage-style film. The photograph features the iconic square format including {$spicy-content-with} a soft focus, a subtle vignetting, and the characteristic pastel color shift of instant film. Showing candid moments or intimate still-lifes. The photograph retains the authentic border, emulsion texture, and occasional “film-like” imperfections (light leaks, scratches).
YOUR PHOTOGRAPH:
{$@}


>>>Urban Wall Mural
SCENE:
A huge mural on a rough brick wall. The scene is captured from a slightly low angle, highlighting the brick texture and spray paint drips. Ambient city light (neon signs, streetlights) blends with natural light, giving the wall a vibrant, kinetic feel.
INSIDE THE MURAL:
An intense, modern spray-painted illustration.
INSIDE THE ILLUSTRATION:
{$@}
OUTSIDE THE MURAL: The brick wall, a window high up, paint cans on the ground, and a weathered patina. The surrounding alley and someone admiring the artwork are visible to the side.


>>> Retro Arcade Cabinet
YOUR CONTEXT
A close-up of an early 1990s arcade machine. It sits in a dimly lit arcade, its side panels covered in glossy vinyl graphics. The CRT monitor glows with its characteristic phosphorescent hue, and the joystick and buttons show slight wear. The arcade machine is viewed from a three-quarter angle, capturing its design, the bright screen, and the reflective floor tiles.
INSIDE YOUR CRT MONITOR:
An action-packed, pixelated, yet brightly colored arcade game.
INSIDE THE PIXELATED ARCADE GAME:
<!--
{$@}
-->
OUTSIDE THE PIXELATED ARCADE GAME:
A dimly lit arcade, including other machines and neon signs, both slightly out of focus.
THE PHOTO:
A close-up of an early 1990s arcade machine. It sits in a dimly lit arcade, its side panels covered in glossy vinyl graphics. The CRT monitor glows with its characteristic phosphorescent hue, and the joystick and buttons show slight wear. The arcade machine is viewed from a three-quarter angle, capturing its design, the bright screen, and the reflective floor tiles.


>>>Neon Billboard
YOUR CONTEXT:
A massive neon-lit billboard dominates a bustling downtown avenue at twilight. The billboard’s glass casing reflects nearby traffic and skyscraper windows. The atmosphere is saturated with city haze, rain-slicked streets, and colorful streetlights.
DISPLAYED ON THE BILLBOARD (YOUR ADVERTISEMENT):
{$@}
YOUR PHOTO:
An eye-level, cinematic photograph of the billboard from street level, showing the vivid neon glow, the wet pavement reflections, and distant cityscape. The billboard’s content is crisp and bright, while the surrounding environment retains a slight motion blur for a dynamic urban feel.


>>>Vintage Reel Frame
YOUR CONTEXT:
Close-up of a classic 35mm nitrate film from the 1930s. The film runs horizontally across the image, with the perforation sequence above and below. The film is laid on a wooden table. The film strip is partially unwound, exposing individual frames. In this extreme close-up, the rectangular frame of the strip fills the entire image.
INSIDE A FILM FRAME:
<!--
{$@}
-->
OUTSIDE THE FILM FRAME:
A wooden table with shadows and light flares projected onto the table.


>>>Holographic Device
YOUR CONTEXT:
A futuristic holographic projector sits atop a sleek, polished pedestal in a minimalist showroom. The projection emits a semi-transparent, three-dimensional image that floats in the air, illuminated by a soft, bluish-white light. The surrounding space is clean, with subtle reflections on the floor.
The holographic screen is positioned at a slightly elevated angle, capturing the floating image.
THE HOLOGRAPHIC PROJECTOR
It's a heavy metal tube with an industrial look and the appearance of a radiator. A powerful red reflector shines from its top side.
INSIDE YOUR HOLOGRAPHIC IMAGE:
The image features blue tones with intensely illuminated light blue lines and wireframe details of light blue lines.
INSIDE YOUR HOLOGRAPHIC IMAGE:
<!--
{$@}
-->
OUTSIDE YOUR HOLOGRAPHIC IMAGE:
The showroom dimly lit by the hologram's blue light.


>>>Coffee-Cup Art Print
YOUR CONTEXT:
An extreme close-up of the foam on a freshly brewed espresso cup. The surface of the foam is printed with a small hand-drawn illustration. The coffee cup is a classic white porcelain mug with a glossy rim, placed on a rustic wooden table.
INSIDE THE FOAM:
A draw in shades of brown and white with blurred lines and foam relief.
INSIDE YOUR FOAM BROWN DRAW:
<!--
{$@}
-->
OUTSIDE THE ARTWORK:
The coffee is in the foreground with a shallow depth of field, shot taken from a slight top-down angle. The foam is subtly depicted against the dark coffee, while the background shows a blurred café scene: a wooden table, other cups and a black background in the top. Light steam rises gently, creating a cozy atmosphere.


>>>Cassette Tape Sleeve
SCENE:
A mixtape from the 1990s lying on a rug in a clutter-filled bedroom. The case stands upright and is made of clear plastic.
INSIDE THE SLEEVE:
<!--
{$@}
-->
OUTSIDE THE SLEEVE:
A nostalgic photograph of the cassette tape lying on a faded carpet. The word "CASSETTE" can be seen written on it. The image captures the handwritten typography, and faint tape-track reflections. Ambient teal-green bedroom light creates a soft, retro vibe.


>>>Vintage Postcard
YOUR CONTEXT:
A postcard printed in the 1950s depicts a charming coastal village. The card is slightly creased, its edges softened by years of handling, and the paper has a warm, yellowed patina.
INSIDE ARTWORK ON THE FRONT OF THE POSTCARD:
Image printed in faded colors, blurry and of low quality.
INSIDE ARTWORK ON THE FRONT OF THE POSTCARD:
<!--
{$@}
-->
OUTSIDE ARTWORK:
A flat, highly detailed photograph of the postcard on a textured linen surface. The postcard's border is embossed, and a handwritten address line (blurred for privacy) is visible. Soft natural light from a nearby window creates gentle shadows that accentuate the nostalgic feel.


>>>Kawaii Pop Photo
YOUR CONTEXT:
You are a fashion photographer specializing in the bright, playful aesthetic of Kawaii Pop.
Your photograph showcases {$spicy-content-with} a high-key composition flooded with vibrant, saturated colors. The exposure is bright and cheerful, with a focus on pastel pinks, electric blues, and sunny yellows. Scene is styled in over-the-top Kawaii fashion with playful poses. The background is simple and colorful, with elements like balloons, confetti, or cartoonish graphics. 
YOUR PHOTOGRAPHY:
{$@}


"""


_CustomStyles = """
>>>Custom 1
{$@}

>>>Custom 2
{$@}

>>>Custom 3
{$@}

>>>Custom 4
{$@}
"""


PREDEFINED_STYLE_GROUPS = [
    StyleGroup.from_string( _PhotoStyles       , category="photo"       , version="v0.8.0" ),
    StyleGroup.from_string( _IllustrationStyles, category="illustration", version="v0.8.0" ),
    StyleGroup.from_string( _OtherStyles       , category="other"       , version="v0.8.0" ),
    StyleGroup.from_string( _CustomStyles      , category="custom"      , version="v0.8.0" ),
]


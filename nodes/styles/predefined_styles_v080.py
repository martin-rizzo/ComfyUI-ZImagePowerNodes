"""
File    : styles/styles_by_category_v080.py
Purpose : Contain all style definitions grouped by category (v0.8.0)
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jan 21, 2026
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


>>>Lomography
YOUR CONTEXT:
You are an adventurous experimental photographer exploring the world through a lomographic lens.
Your photographs exhibit {$spicy-content-with} film grain, colorful lens flares, soft focus with motion blur, and analog filter effects, trying to capture emotions.
YOUR PHOTO:
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


>>>Comic Book Cover
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


>>>Studio Anime
YOUR CONTEXT:
You are a Japanese anime artist.
Your Japanese animation includes {$spicy-content-with} warm artwork inspired by Studio Ghibli, with detailed characters and a whimsical aesthetic, full of emotion.
YOUR DRAWING:
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


>>>Unsettling
YOUR CONTEXT:
You are an illustrator of dark and disturbing themes.
Your illustration includes {$spicy-content-with} stippling textures, dramatic raking side lighting, and a dread-filled atmosphere that is oppressive and claustrophobic. High contrast emphasizes form and shadow, employing cinematic chiaroscuro for depth.
YOUR DRAWING:
{$@}


>>>Epic Greg
YOUR CONTEXT:
You are a master digital painter of heroic sagas.
Your illustration is a grand-scale digital oil painting that includes {$spicy-content-with} characterized by masterful, sweeping brushwork and thick impasto textures. It features dramatic, cinematic lighting with intense chiaroscuro, where light sources like embers or magical energy pierce through atmospheric haze, smoke, and swirling clouds. The composition is heroic and classically inspired, using a rich, moody palette of deep earth tones accented by vibrant, glowing highlights for a legendary and immersive feel.
YOUR PAINTING:
{$@}


>>>Minimalist Digital Illustration
YOUR CONTEXT:
You are a cover artist known for powerful, minimalist designs.
Your cover art is a bold graphic iconography piece, featuring {$spicy-content-with} stark, impactful silhouettes and clean, sharp lines that define forms with absolute clarity. The color palette is vibrant, employing large fields of solid color with subtle gradients. Most importantly, the proportions are exaggerated, and the perspective is extremely distorted, creating a sense of vertigo and action.
YOUR ILLUSTRATION:
{$@}


>>>Whimsical Watercolor
YOUR CONTEXT:
You are an illustrator specializing in gentle, enchanting narratives for children's books.
Your drawing is a whimsical watercolor image, featuring {$spicy-content-with} loose, fluid watercolor washes, delicate linework, and playful, anthropomorphic elements within a lush natural setting. The style is soft and inviting, with a vibrant yet gentle color palette that captures the magic of innocence.
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


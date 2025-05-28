from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
from matplotlib import font_manager

def find_system_font(name_keyword="JetBrainsMono Nerd Font"):
    # Search system fonts for a font containing the keyword
    fonts = font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
    for font in fonts:
        if name_keyword.lower() in os.path.basename(font).lower():
            return font
    raise FileNotFoundError(f"Font with keyword '{name_keyword}' not found.")
def text_to_image(
    text,
    input_image=None,
    output_path="output.png",
    image_size=(1080, 1920),  # 9:16
    font_keyword="JetBrainsMono",
    font_size=30, # Keep font_size flexible
    bg_color="black",
    text_color="white",
    target_text_width_ratio=0.85 # New parameter: how much of the image width should the text ideally take up (e.g., 0.85 for 85%)
):
    # 1. Load font from system
    font_path = find_system_font(font_keyword)
    font = ImageFont.truetype(font_path, font_size)

    # 2. Dynamically calculate wrap_width
    # Create a temporary ImageDraw object *just for text measurement*
    # We don't need a real image for this, just an associated drawing context.
    temp_img = Image.new('RGB', (1, 1)) # Smallest possible image
    temp_draw = ImageDraw.Draw(temp_img)

    # Measure the width of an "average" character or a representative string
    char_bbox = temp_draw.textbbox((0, 0), "W", font=font)
    average_char_width = char_bbox[2] - char_bbox[0]

    # Determine the desired pixel width for the text block
    desired_pixel_width = image_size[0] * target_text_width_ratio

    # Calculate the wrap_width (number of characters)
    if average_char_width > 0:
        calculated_wrap_width = int(desired_pixel_width / average_char_width)
    else:
        calculated_wrap_width = 1 # Fallback, though unlikely with proper fonts

    # Ensure wrap_width is not excessively small or large
    calculated_wrap_width = max(calculated_wrap_width, 10) # Minimum characters per line
    calculated_wrap_width = min(calculated_wrap_width, 150) # Prevent excessively long lines for tiny fonts

    # 3. Create the *actual* blank image for rendering
    image = Image.new("RGB", image_size, color=bg_color) if not input_image else (Image.open(input_image) if isinstance(input_image, str) else ( input_image if isinstance(input_image, Image) else None)))
    if not image:
        raise ValueError("Unable to Create/load Drawable image")
    draw = ImageDraw.Draw(image) # This is the 'draw' object you'll use for final rendering

    # 4. Wrap text using the calculated wrap_width
    wrapped_text = textwrap.fill(text, width=calculated_wrap_width)

    # 5. Calculate size and position for the wrapped text on the *actual* draw object
    bbox = draw.textbbox((0, 0), wrapped_text, font=font, spacing=10, align="center")
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Fallback for very short text that might not generate a proper bbox
    if text_width == 0:
        text_width = image_size[0] * 0.5 # Assume half width
    if text_height == 0:
        text_height = font_size # Assume height of one line

    x = (image_size[0] - text_width) / 2
    y = (image_size[1] - text_height) / 2

    # 6. Draw text
    draw.multiline_text((x, y), wrapped_text, font=font, fill=text_color, align="center", spacing=10)

    # 7. Save image
    image.save(output_path)
    print(f"Saved image to: {output_path}")
    print(f"Calculated wrap_width: {calculated_wrap_width}")

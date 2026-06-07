import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile


def generate_avatar(name):
    colors = [
        "#FFB3BA",
        "#FFDFBA",
        "#FFFFBA",
        "#BAFFC9",
        "#BAE1FF",
        "#E2CBF7",
        "#D5E8D4",
    ]
    bg_color = random.choice(colors)
    text_color = "#333333"
    letter = name[0].upper() if name else "U"

    size = (200, 200)
    image = Image.new("RGB", size, color=bg_color)
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 100)
    except IOError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), letter, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (size[0] - w) / 2
    y = (size[1] - h) / 2 - (bbox[1])

    draw.text((x, y), letter, fill=text_color, font=font)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name=f"{name}_avatar.png")

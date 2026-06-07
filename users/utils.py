import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from django.core.files.base import ContentFile

from team_finder.constants import (
    AVATAR_COLORS,
    AVATAR_TEXT_COLOR,
    AVATAR_SIZE,
    AVATAR_FONT_SIZE,
    AVATAR_DEFAULT_LETTER,
    AVATAR_FONT_NAME,
)


def generate_avatar(name):
    bg_color = random.choice(AVATAR_COLORS)
    letter = name[0].upper() if name else AVATAR_DEFAULT_LETTER

    image = Image.new("RGB", AVATAR_SIZE, color=bg_color)
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype(AVATAR_FONT_NAME, AVATAR_FONT_SIZE)
    except IOError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), letter, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    x = (AVATAR_SIZE[0] - w) / 2
    y = (AVATAR_SIZE[1] - h) / 2 - bbox[1]

    draw.text((x, y), letter, fill=AVATAR_TEXT_COLOR, font=font)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name=f"{name}_avatar.png")

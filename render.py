from PIL import Image, ImageDraw, ImageFont
import os
from matplotlib import font_manager
from uuid import uuid4


class RenderQuoteAsImage:
    def __init__(self, **kwargs):
        self.template = kwargs.get("template") or None
        self.width = kwargs.get("width") or 1080
        self.mode = kwargs.get("mode") or "RGB"
        self.height = kwargs.get("height") or 1920
        self.bg_color = kwargs.get("color") or "black"
        self.font_color = kwargs.get("font_color") or "white"
        self.font_keyword = kwargs.get("font_keyword") or "JetBrain"
        self.font_size = kwargs.get("font_size") or 42
        self.margin = kwargs.get("margin") or 20
        self.font = self.get_font()
        self.output_name = kwargs.get("output_name") or (uuid4().hex + ".png")
        self.output_dir = kwargs.get("output_dir") or os.path.join("output", "images")
        os.makedirs(self.output_dir, exist_ok=True)

    @property
    def save(self):
        path = os.path.join(self.output_dir, self.output_name)
        prefix = ""
        i = 0
        while os.path.exists(path):
            prefix = f"{i}_"
            path = os.path.join(self.output_dir, prefix + self.output_name)
            i += 1
        return path

    def find_system_font(self):
        # Search system fonts for a font containing the keyword
        fonts = font_manager.findSystemFonts(fontpaths=None, fontext="ttf")
        for font in fonts:
            if self.font_keyword.lower() in os.path.basename(font).lower():
                return font
        raise FileNotFoundError(f"Font with keyword '{self.font_keyword}' not found.")

    def get_font(self):
        font_path = self.find_system_font()
        self.font = ImageFont.truetype(font=font_path, size=self.font_size)
        return self.font

    def wrap_text(
        self, text: str, font: ImageFont.FreeTypeFont, max_width: int
    ) -> list[str]:
        lines = []
        if font.getlength(text) < max_width:
            lines.append(text)
        else:
            words = text.split(" ")
            i = 0
            while i < len(words):
                line = ""
                while i < len(words) and font.getlength(line + words[i]) <= max_width:
                    line += words[i] + " "
                    i += 1
                if not line:
                    line = words[i]
                    i += 1
                lines.append(line)
        return lines

    def get_center_pos(self, text_width, text_height) -> tuple[int, int]:
        return (self.width - text_width) // 2, (self.height - text_height) // 2

    def get_text_size(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        align: str = "center",
        initital_pos: tuple[int, int] = (0, 0),
    ) -> tuple[int, int]:
        bbox = (draw.multiline_textbbox if "\n" in text else draw.textbbox)(
            initital_pos, text=text, font=self.font, align=align
        )
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    def calculate_margin(self) -> int:
        return int((self.margin / 100) * self.width)

    def convert_quote_to_image(self, quote: str) -> str | None:
        self.font = self.get_font()
        if self.template:
            if os.path.exists(self.template):
                image = Image.open(self.template)
                self.width, self.height = image.size
        else:
            image = Image.new(self.mode, (self.width, self.height), color=self.bg_color)

        draw = ImageDraw.Draw(image)
        self.margin = self.calculate_margin()
        margined_width, margined_height = (
            self.width - 2 * self.margin,
            self.height - 2 * self.margin,
        )
        lines = self.wrap_text(quote, self.font, margined_width)

        text_width, text_height = self.get_text_size(draw, "\n".join(lines))
        x, y = self.get_center_pos(text_width, text_height)
        print(self.width, self.height, image.size, x, y, text_height, text_width)

        draw.multiline_text(
            (x, y), "\n".join(lines), font=self.font, fill=self.font_color, align="center"
        )
        save_path = self.save
        image.save(
            save_path, format=save_path.split(".")[-1].lstrip(".").upper(), quality=100
        )
        return save_path

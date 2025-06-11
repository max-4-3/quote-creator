from render import RenderQuoteAsImage
import os

ir = RenderQuoteAsImage()
ir.font_size = 42
ir.template = "./templates/bro.png"
ir.convert_quote_to_image("Over the edge, fule like through the edge!")


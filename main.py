from quote import QuoteCreator
from render import RenderQuoteAsImage
from video import RenderImageAsVideo, process_video_with_overlay
from upload import Uploader
from rich import print
import os
import re
import random
from consts import BODY, AUDIO_DATA, TEMPLATE_IMAGES, TEMPLATE_VIDEOS, FONTS, FINAL_VIDEO_PATH, FINAL_IMAGE_PATH
import moviepy as mp


def clear():
    os.system("clear" if os.name.lower() not in ["windows", "nt"] else "cls")


def next_section(prompt: str = "Press Enter to continue..."):
    print(prompt)
    input("")
    clear()


def main():
    print("Setting Up...")

    qt = QuoteCreator()
    ir = RenderQuoteAsImage(font_keyword="JetBrain")
    iv = RenderImageAsVideo()
    up = Uploader()
    print("Everyting setup!")

    ir.output_dir = FINAL_IMAGE_PATH
    iv.output_path = FINAL_VIDEO_PATH

    if FONTS:
        font = random.choice(FONTS)
        print("Font choosen: {}".format(os.path.basename(font)))
        ir.set_font_from_file(font)
    else:
        print("No custom fonts found falling back to: {}".format(ir.font_keyword))

    if input("Do you want to use videos as background? ").lower().strip() in ["yes", "y"]:
        overlay_flow = True
    else:
        overlay_flow = False

    if overlay_flow:
        ir.mode = "RGBA"
        ir.bg_color = (0, 0, 0, 0)

    print("Gathering quote of the day...")
    qt_day = qt.get_quote_of_day()
    qt.save_quotes()
    iv.output_name = "".join(qt_day.quote[1:-2])
    print("Recieved Quote of the day:", qt_day.quote, sep="\n")

    next_section()

    print("Converting quote to image...")
    if not overlay_flow:
        template = random.choice(TEMPLATE_IMAGES)
        print(f"Using '{template}' as template...")
        ir.template = template
    image_path = ir.convert_quote_to_image(quote=qt_day.quote)
    print("Convered Quote as image at", image_path, sep=": ")

    next_section()

    print("Converting Image to Video...")
    if input("Have a custom audio path?: ").lower().strip() in ["yes", "y"]:
        audio_path = input("Enter the bg audio path: ")
        if not os.path.exists(audio_path):
            raise ValueError("Audio is required!")
        audio_trim = input(
            "Enter the section which you want to include in video from audio as a tuple (i.e. (0, 30); without brackets!): \n"
        )
        audio_trim_match = re.search(r"(\d+)\s*,\s*(\d+)", audio_trim.strip())
        if not audio_trim_match:
            audio_trim = (0, int(iv.duration))
        else:
            audio_trim = (
                int(audio_trim_match.group(1)),
                int(audio_trim_match.group(2)),
            )
    else:
        selected_audio = random.choice(AUDIO_DATA)
        audio_trim = random.choice(selected_audio["sections"])
        print(f"Seleted Audio: {selected_audio["file_name"]} [{audio_trim}]")
        audio_path = selected_audio["file"]
    print("Rendering Video...")
    overlay_path = None
    if overlay_flow:
        overlay_path = random.choice(TEMPLATE_VIDEOS)
        print("Background Video Choosen: {}".format(overlay_path))

    if not overlay_path:
        iv.set_audio(audio_path, audio_trim)
        video_path = iv.convert_image(image_path)
    else:
        video_path = process_video_with_overlay(overlay_path, image_path, os.path.join(
            "output", "video", f"{"".join(qt_day.quote[1:-2])}.mp4"))
    print("Video Rendered at", video_path, sep=": ")

    next_section()

    print("Logging into instagram...")
    print(f"[{up.client.account_info().full_name}] Uploading to instagram...")
    title = "\n".join([qt_day.quote, f"- {qt_day.author}"] + BODY)
    print("Title Generated:\n", title)
    up.caption = title

    if input("Do you want to upload with above settings?: ").lower().strip() in [
        "no",
        "n",
        "not",
        "false",
    ]:
        print("See the results in:")
        print(image_path)
        print(video_path)
        exit(0)
    info = up.upload_reel(video_path=video_path, thumb_path=image_path)
    print("Reel Uploaded to instagram!")
    print(info.pk)


if __name__ == "__main__":
    main()

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

    next_section()

    ir.output_dir = FINAL_IMAGE_PATH
    iv.output_path = FINAL_VIDEO_PATH

    if FONTS:
        font = random.choice(FONTS)
        print(
            "Font choosen: [bold cyan]{}[/cyan bold]".format(os.path.basename(font)))
        ir.set_font_from_file(font)
    else:
        print(
            "No custom fonts found falling back to: [bold red]{}[/red bold]".format(ir.font_keyword))

    print(
        "Do you want to use [yellow]videos[/yellow] as [italic]background[/italic]? ")
    if input("").lower().strip() in ["yes", "y"]:
        overlay_flow = True
    else:
        overlay_flow = False

    if overlay_flow:
        ir.mode = "RGBA"
        ir.bg_color = (0, 0, 0, 0)

    next_section()

    print("Gathering quote of the day...")
    qt_day = qt.get_quote_of_day()
    qt.save_quotes()
    iv.output_name = qt_day.quote[1:-2]
    print("Recieved Quote of the day:", f"[bold]{
          qt_day.quote}[/bold]", sep="\n")

    next_section()

    print("Converting quote to image...")
    if not overlay_flow:
        template = random.choice(TEMPLATE_IMAGES)
        print(f"Using '[green]{template}[/green]' as template...")
        ir.template = template
    image_path = ir.convert_quote_to_image(quote=qt_day.quote)
    print("Convered Quote as image at", f"[bold green]{
          image_path}[/green bold]", sep=":\n")

    next_section()

    print("Converting Image to Video...")
    print("Have a custom [italic]audio[/italic] path? ")
    if input("").lower().strip() in ["yes", "y"]:
        print("Enter the [yellow italic]bg audio[/italic yellow] path: ")
        audio_path = input("")
        if not os.path.exists(audio_path):
            raise ValueError("Audio is required!")
        print("Enter the section which you want to include in video from audio as a tuple: \n(i.e. (0, 30); without brackets!): \n")
        audio_trim = input(
            ""
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
        print(f"Seleted Audio: [bold cyan]{
              selected_audio["file_name"]}[/cyan bold] {audio_trim}")
        audio_path = selected_audio["file"]
    print("Rendering Video...")
    overlay_path = None
    if overlay_flow:
        overlay_path = random.choice(TEMPLATE_VIDEOS)
        print(
            "Background Video Choosen: [bold green]{}[/green bold]".format(overlay_path))

    if not overlay_path:
        iv.set_audio(audio_path, audio_trim)
        video_path = iv.convert_image(image_path)
    else:
        video_path = process_video_with_overlay(overlay_path, image_path, os.path.join(
            "output", "video", f"{qt_day.quote[1:-2]}.mp4"))
    print("Video Rendered at", f"[bold]{video_path}[/bold]", sep=":\n")

    next_section()

    print("Logging into instagram...")
    print(f"[[bold cyan]{up.client.account_info(
    ).full_name}[/cyan bold]] Uploading to instagram...")
    title = "\n".join([qt_day.quote, f"- {qt_day.author}"] + BODY)
    print("Title Generated:\n", title)
    up.caption = title

    if input("Do you want to upload with above settings?: ").lower().strip() in [
        "no",
        "n",
        "not",
        "false",
    ]:
        print("See the results.")
        print("Image:", image_path)
        print("Video:", video_path)
        exit(0)
    info = up.upload_reel(video_path=video_path, thumb_path=image_path)
    print("Reel [bold green]Uploaded[/green bold] to instagram!")


if __name__ == "__main__":
    main()

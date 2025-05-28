from quote import QuoteCreator
from render import RenderQuoteAsImage
from video import RenderImageAsVideo
from upload import Uploader
from rich import print
import os, re, random
from consts import BODY, AUDIO_DATA, TEMPLATES


def main():
    print("Setting Up...")

    qt = QuoteCreator()
    ir = RenderQuoteAsImage()
    iv = RenderImageAsVideo()
    up = Uploader()
    ir.font_size = 440
    print("Everyting setup!")

    print("Gathering quote of the day...")
    qt_day = qt.get_quote_of_day()
    qt.save_quotes()
    print("Recieved Quote of the day:", qt_day.quote, sep="\n")

    print("Converting quote to image...")
    template = random.choice(TEMPLATES)
    print(f"Using '{template}' as template...")
    ir.template = template
    image_path = ir.convert_quote_to_image(quote=qt_day.quote)
    print("Convered Quote as image at", image_path, sep=": ")

    print("Converting Image to Video...")
    if False:
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
        print(f"Seleted Audio: {selected_audio["file_name"]}")
        audio_path = selected_audio["file"]
        audio_trim = random.choice(selected_audio["sections"])
    print("Rendering Video...")
    iv.set_audio(audio_path=audio_path, audio_cut_time=audio_trim)
    video_path = iv.convert_image(image_path)
    print("Video Rendered at", video_path, sep=": ")

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

import moviepy as mp
import os
from rich import print

QUOTES_DIR  = "quotes"
OUTPATH     = "output"
IMAGE_PATH  = "quotes/20_quote.png"
AUDIO_PATH  = "res/audio.mp3"
DURATION    = 6
FADEIN      = 2.0
FADEOUT     = FADEIN
VIDEO_EFFECTS = [mp.vfx.FadeIn(FADEIN), mp.vfx.FadeOut(FADEOUT)]
AUDIO_EFFECTS = [mp.afx.AudioFadeIn(FADEIN), mp.afx.AudioFadeOut(FADEOUT)]

mp.config.FFMPEG_BINARY  = "/usr/bin/ffmpeg"
mp.config.FFPLAY_BINARY  = "/usr/bin/ffplay"

audio = mp.CompositeAudioClip([mp.AudioFileClip(AUDIO_PATH).subclipped(start_time=120, end_time=200)]).with_effects(AUDIO_EFFECTS).with_duration(DURATION)

for file in os.listdir(QUOTES_DIR):
    file = os.path.join(QUOTES_DIR, file)

    if os.path.isdir(file):
        continue

    print(f'Making Quote Video for "{os.path.basename(file)}"')
    image = mp.ImageClip(file, duration=DURATION).with_effects(VIDEO_EFFECTS)
    clip = mp.CompositeVideoClip([image])
    clip.fps = 30
    clip.audio = audio
    clip.write_videofile(filename=os.path.join(OUTPATH, os.path.basename(file) + ".mp4"), codec="h264", preset="fast")
    print(f'Video Made!')


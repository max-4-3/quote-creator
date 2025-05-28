import moviepy as mp
import os

mp.config.FFMPEG_BINARY = "/usr/bin/ffmpeg"
mp.config.FFPLAY_BINARY = "/usr/bin/ffplay"


class RenderImageAsVideo:
    def __init__(self, **kwargs):
        self.output_path = kwargs.get("output_path") or "output/video"
        self.output_name = kwargs.get("output_name") or "video.mp4"
        self.duration = kwargs.get("duration") or 6.0
        self.fadein = kwargs.get("fadein") or 2.0
        self.fadeout = self.fadein
        self.vfx = [mp.vfx.FadeIn(self.fadein), mp.vfx.FadeOut(self.fadeout)]
        self.afx = [mp.afx.AudioFadeIn(self.fadein), mp.afx.AudioFadeOut(self.fadeout)]
        self.audio: mp.CompositeAudioClip = None

        os.makedirs(self.output_path, exist_ok=True)

    def set_audio(
        self, audio_path: str, audio_cut_time: tuple[int, int]
    ) -> mp.CompositeAudioClip:
        self.audio = (
            mp.CompositeAudioClip(
                [mp.AudioFileClip(audio_path).subclipped(*audio_cut_time)]
            )
            .with_effects(self.afx)
            .with_duration(self.duration)
        )
        return self.audio

    def convert_image(self, image_path: str, output_name=None):

        if not self.audio:
            raise Exception("Audio isn't set, consider doing .set_audio() first")

        if output_name:
            self.output_name = output_name

        if not os.path.exists(image_path) or not os.path.isfile(image_path):
            raise FileExistsError("Image File Doesn't Exist")

        image = mp.ImageClip(image_path, duration=self.duration).with_effects(self.vfx)
        clip = mp.CompositeVideoClip([image])
        clip.fps = 30
        clip.audio = self.audio
        clip.write_videofile(
            filename=os.path.join(self.output_path, self.output_name),
            codec="h264",
            preset="fast",
        )
        return os.path.join(self.output_path, self.output_name)

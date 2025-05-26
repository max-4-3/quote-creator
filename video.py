import moviepy.editor as mp # Recommended import for MoviePy 2.x

# Define paths for clarity
IMAGE_PATH = "quotes/10_quote.png"
AUDIO_PATH = "res/audio.mp3"

# 1. Create Image Clip and apply video effects using .fx()
# No need to put effects in a list with .fx(). Each .fx() call applies one effect.
image = mp.ImageClip(IMAGE_PATH, duration=10).fx(
    mp.vfx.fadein, duration=1 # Pass effect function and its parameters
).fx(
    mp.vfx.fadeout, duration=1 # Chain another .fx() call for the next effect
)

# 2. Create Audio Clip and subclip it
audio = mp.AudioFileClip(AUDIO_PATH)

# Use .subclip() and provide start/end times in seconds (float or int)
# "00:01:07.00" converts to 67.0 seconds
# "00:01:17.00" converts to 77.0 seconds
audio = audio.subclip(67.0, 77.0)

# 3. Apply audio effects using .fx()
audio = audio.fx(
    mp.afx.audio_fadein, duration=1 # Pass effect function and its parameters
).fx(
    mp.afx.audio_fadeout, duration=1 # Chain another .fx() call
)

# 4. Composite the video clip with the audio
# .set_audio() is often more explicit than .with_audio() but both generally work.
# .with_audio() is fine here.
composite_clip = mp.CompositeVideoClip([image]).with_audio(audio)

# 5. Preview the composite clip
composite_clip.preview()

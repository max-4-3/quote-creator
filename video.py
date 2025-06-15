import moviepy as mp

# This bit is from gemini.
import os
import subprocess as sp
import re
from PIL import Image, ImageDraw, ImageFilter
from rich.progress import Progress
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import math
import logging
import shutil
import time

# --- Configure Logger ---
# It's generally better to configure logging outside the reusable function
# or pass a logger instance to it, but for a self-contained module,
# this global configuration is acceptable.
logger = logging.getLogger(__name__)
# Prevent adding multiple handlers if the module is reloaded/imported multiple times
if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler("video_processing.log", "a") # Changed log file name
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


# --- Helper Functions (Internal to the module) ---

def _get_video_duration(num_frames: int, fps: int) -> float:
    """
    Calculates the total duration of the video in seconds based on
    the number of frames and frames per second.
    """
    if fps == 0:
        logger.warning("FPS is zero, returning duration of 0.")
        return 0
    return num_frames / float(fps)

def _combine_image_dir_to_video(
    image_dir: str,
    file_name: str,
    fps: int,
    vf: str,
    fade_in_duration: float,
    fade_out_duration: float,
    audio_file_path: str
):
    """
    Combines a directory of numerically sequenced PNG images into a video file using ffmpeg,
    with optional fade effects and audio.

    Raises:
        subprocess.CalledProcessError: If the ffmpeg command fails.
        FileNotFoundError: If ffmpeg executable is not found.
    """
    logger.info(f"Attempting to combine images from '{image_dir}' into '{file_name}'...")

    image_files = [f for f in os.listdir(image_dir) if os.path.splitext(f)[1].lower() in [".jpg", ".png", ".jpeg"]]
    num_frames = len(image_files)
    total_video_duration = _get_video_duration(num_frames, fps)

    command = [
        "ffmpeg",
        "-framerate", str(fps),
        "-i", os.path.join(os.path.abspath(image_dir), "final_image_%09d.png")
    ]

    if audio_file_path:
        if not os.path.exists(audio_file_path):
            logger.warning(f"Audio file not found at '{audio_file_path}'. Video will be created without audio.")
            audio_file_path = None
        else:
            command.extend(["-i", audio_file_path])

    video_filters = [vf]
    if fade_in_duration > 0:
        video_filters.append(f"fade=t=in:st=0:d={fade_in_duration}")

    if fade_out_duration > 0 and total_video_duration > fade_out_duration:
        fade_out_start_time = max(0, total_video_duration - fade_out_duration)
        video_filters.append(f"fade=t=out:st={fade_out_start_time}:d={fade_out_duration}")
    elif fade_out_duration > 0: # and total_video_duration <= fade_out_duration
        logger.warning(f"Fade-out duration ({fade_out_duration}s) is longer than or equal to total video duration ({total_video_duration:.2f}s). No fade-out applied.")

    command.extend(["-vf", ",".join(video_filters)])
    command.extend(["-c:v", "libx264", "-crf", "23", "-preset", "medium"])

    if audio_file_path:
        command.extend(["-map", "0:v:0", "-map", "1:a:0", "-shortest", "-c:a", "aac", "-b:a", "192k"])

    command.append("-y")
    command.append(file_name)

    logger.debug(f"Running ffmpeg command: {' '.join(command)}")
    try:
        sp.run(command, check=True, capture_output=True, text=True)
        logger.info(f"Video '{file_name}' created successfully.")
    except sp.CalledProcessError as e:
        logger.error(f"Error creating video: {e.cmd}")
        logger.error(f"ffmpeg stdout: {e.stdout}")
        logger.error(f"ffmpeg stderr: {e.stderr}")
        raise
    except FileNotFoundError:
        logger.error("Error: ffmpeg not found. Please ensure ffmpeg is installed and in your system's PATH.")
        raise FileNotFoundError("ffmpeg not found. Please install ffmpeg and ensure it's in your system's PATH.")


def _decompress_video(vid_path: str, image_dir: str):
    """
    Decompresses a video into a sequence of PNG image frames.

    Raises:
        subprocess.CalledProcessError: If the ffmpeg command fails.
        FileNotFoundError: If ffmpeg executable is not found.
    """
    logger.info(f"Decompressing video '{vid_path}' into frames in '{image_dir}'...")
    os.makedirs(image_dir, exist_ok=True)

    output_pattern = os.path.join(image_dir, "frame_%09d.png")

    command = [
        "ffmpeg",
        "-i", vid_path,
        "-r", "30", # Output frame rate
        output_pattern
    ]

    logger.debug(f"Running ffmpeg command: {' '.join(command)}")
    try:
        sp.run(command, check=True, capture_output=True, text=True)
        logger.info(f"Video '{vid_path}' decompressed to frames in '{image_dir}'.")
    except sp.CalledProcessError as e:
        logger.error(f"Error decompressing video: {e.cmd}")
        logger.error(f"ffmpeg stdout: {e.stdout}")
        logger.error(f"ffmpeg stderr: {e.stderr}")
        raise
    except FileNotFoundError:
        logger.error("Error: ffmpeg not found. Please ensure ffmpeg is installed and in your system's PATH.")
        raise FileNotFoundError("ffmpeg not found. Please install ffmpeg and ensure it's in your system's PATH.")


def _smart_resize_background(bg_image: Image.Image, overlay_size: tuple):
    """
    Resizes and potentially rotates the background image to intelligently fit or fill
    the overlay's dimensions.
    """
    fg_width, fg_height = overlay_size
    bg_width, bg_height = bg_image.size

    logger.debug(f"Overlay size: {overlay_size}")
    logger.debug(f"Original background size: {bg_image.size}")

    # 1. Check for rotation: if background's swapped dimensions match overlay's dimensions
    if (math.isclose(bg_height, fg_width, rel_tol=1e-5) and
        math.isclose(bg_width, fg_height, rel_tol=1e-5)):
        logger.info("Rotating background image by -90 degrees for orientation match.")
        bg_image = bg_image.rotate(-90, expand=True) # Rotate 90 degrees clockwise
        bg_width, bg_height = bg_image.size # Update dimensions after rotation
        logger.debug(f"Background size after rotation: {bg_image.size}")

    # 2. Calculate aspect ratios
    bg_aspect = bg_width / bg_height
    fg_aspect = fg_width / fg_height

    logger.debug(f"Background aspect ratio: {bg_aspect:.4f}")
    logger.debug(f"Foreground aspect ratio: {fg_aspect:.4f}")

    if bg_aspect > fg_aspect:
        # Background is proportionally wider/shorter than foreground. Use 'fit' (letterbox).
        logger.info("Using 'fit' (letterbox) strategy.")
        scale_factor = fg_height / bg_height
        new_width = int(bg_width * scale_factor)
        new_height = fg_height
        resized_img = bg_image.resize((new_width, new_height), Image.LANCZOS)

        new_background = Image.new("RGB", overlay_size, (0, 0, 0)) # Black background
        paste_x = (fg_width - new_width) // 2
        paste_y = (fg_height - new_height) // 2
        new_background.paste(resized_img, (paste_x, paste_y))
        return new_background
    else:
        # Background is proportionally taller/thinner or has the same aspect ratio as foreground. Use 'fill' (crop).
        logger.info("Using 'fill' (crop) strategy.")
        scale_factor = fg_width / bg_width
        new_width = fg_width
        new_height = int(bg_height * scale_factor)
        resized_img = bg_image.resize((new_width, new_height), Image.LANCZOS)

        left = (new_width - fg_width) // 2
        top = (new_height - fg_height) // 2
        right = left + fg_width
        bottom = top + fg_height
        cropped_img = resized_img.crop((left, top, right, bottom))
        return cropped_img

def _process_single_image(file_path: str, idx: int, overlay_image: Image.Image, output_dir: str):
    """
    Processes a single image frame: opens, smart-resizes, converts to B&W, blurs, and pastes overlay.
    """
    try:
        img: Image.Image = Image.open(file_path).convert("RGB")

        img = _smart_resize_background(img, overlay_image.size)
        img = img.convert("L") # Convert background to grayscale
        img = img.filter(ImageFilter.BoxBlur(10)) # Apply blur
        img = img.convert("RGB") # Convert back to RGB for correct overlay pasting

        img.paste(overlay_image, (0,0), mask=overlay_image)

        output_filepath = os.path.join(output_dir, f"final_image_{idx:09d}.png")
        img.save(output_filepath, "PNG")
        logger.debug(f"Successfully processed and saved: {os.path.basename(file_path)}")
        return True
    except Exception as e:
        logger.error(f"Error processing image '{os.path.basename(file_path)}' [{e.__class__.__name__}]: {e}")
        return False


# --- Global Function for Video Processing ---

def process_video_with_overlay(
    video_input_path: str,
    overlay_image_path: str,
    output_video_file: str = "output_video.mp4",
    temp_dir_base: str = "temp_video_processing",
    target_fps: int = 30,
    fade_in_duration: float = 1,
    fade_out_duration: float = 2,
    audio_source_path: str = None
):
    """
    Orchestrates the entire video processing workflow:
    1. Decompresses video into frames.
    2. Processes each frame (smart resize, B&W, blur, overlay).
    3. Combines processed frames into a new video with optional fades and audio.
    4. Cleans up temporary directories.

    Args:
        video_input_path (str): Path to the input video file.
        overlay_image_path (str): Path to the overlay image file.
        output_video_file (str): Name of the final output video file.
        temp_dir_base (str): Base directory for temporary image storage.
        target_fps (int): Desired frames per second for the output video.
        fade_in_duration (float): Duration of the fade-in effect in seconds.
        fade_out_duration (float): Duration of the fade-out effect in seconds.
        audio_source_path (str): Path to the audio file to use (can be the input video itself).

    Raises:
        FileNotFoundError: If input video, overlay image, or ffmpeg are not found.
        Exception: For any other unexpected errors during processing.
    """
    start_time = time.perf_counter()
    logger.info(f"Starting video processing for '{video_input_path}'...")

    output_images_dir = os.path.join(temp_dir_base, "decompressed_frames")
    final_images_dir = os.path.join(temp_dir_base, "processed_frames")

    # Step 1: Decompress the video into individual image frames
    try:
        _decompress_video(video_input_path, output_images_dir)
    except (FileNotFoundError, sp.CalledProcessError) as e:
        logger.error(f"Failed to decompress video: {e}")
        # Clean up partial temp directory if any
        if os.path.exists(temp_dir_base):
            shutil.rmtree(temp_dir_base)
        raise

    # Step 2: Load the overlay image
    try:
        overlay: Image.Image = Image.open(overlay_image_path)
    except FileNotFoundError:
        logger.error(f"Error: Overlay image not found at '{overlay_image_path}'.")
        if os.path.exists(temp_dir_base):
            shutil.rmtree(temp_dir_base)
        raise FileNotFoundError(f"Overlay image not found: {overlay_image_path}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while opening the overlay image: {e}")
        if os.path.exists(temp_dir_base):
            shutil.rmtree(temp_dir_base)
        raise

    os.makedirs(final_images_dir, exist_ok=True)
    logger.info(f"Processing frames and applying overlay using {os.cpu_count()} threads. Outputting to '{final_images_dir}'...")

    # Step 3: Process each decompressed image frame using ThreadPoolExecutor
    with Progress() as progress:
        all_files = os.listdir(output_images_dir)
        image_files = sorted(
            [f for f in all_files if os.path.splitext(f)[1].lower() in [".jpg", ".png", ".jpeg"]],
            key=lambda x: int("".join(re.findall(r"\d+", x) or ["0"]))
        )

        if not image_files:
            logger.error(f"No image files found in '{output_images_dir}'. Exiting.")
            if os.path.exists(temp_dir_base):
                shutil.rmtree(temp_dir_base)
            raise ValueError(f"No image files found in {output_images_dir}")

        task = progress.add_task("Image Processing", total=len(image_files))
        futures = []

        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            for idx, file in enumerate(image_files, start=1):
                fp = os.path.join(output_images_dir, file)
                futures.append(executor.submit(_process_single_image, fp, idx, overlay, final_images_dir))

            for future in as_completed(futures):
                if not future.result(): # Check if processing failed for any image
                    logger.warning("One or more images failed to process. Continuing with successful ones.")
                progress.update(task, advance=1)

    # Step 4: Combine the processed images into the final video
    try:
        _combine_image_dir_to_video(
            final_images_dir,
            output_video_file,
            vf="format=yuv420p",
            fps=target_fps,
            fade_in_duration=fade_in_duration,
            fade_out_duration=fade_out_duration,
            audio_file_path=audio_source_path
        )
    except (FileNotFoundError, sp.CalledProcessError) as e:
        logger.error(f"Failed to combine images into video: {e}")
        # Clean up before re-raising
        if os.path.exists(temp_dir_base):
            shutil.rmtree(temp_dir_base)
        raise

    # Step 5: Clean up temporary directories
    if os.path.exists(temp_dir_base):
        logger.info(f"Cleaning up temporary directory: {temp_dir_base}")
        shutil.rmtree(temp_dir_base)

    end_time = time.perf_counter()
    logger.info(f"Script execution finished. Look for '{output_video_file}' in the current directory.")
    logger.info(f"Total time taken: {end_time - start_time:.2f}s")

    return output_video_file


# This is my stupid code

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

    def save_clip(self, clip: mp.CompositeVideoClip, filename: str, codec: str = "h264", preset: str = "fast"):
        directory, file_name = os.path.split(filename)
        name, ext = os.path.splitext(file_name)

        os.makedirs(directory, exist_ok=True)
        if not ext:
            ext = ".mp4"
        elif not ext.startswith("."):
            ext = "." + ext

        # Sanitize the filename (remove spaces/symbols)
        name = re.sub(r"[\W]+", "_", name)
        cleaned_path = os.path.join(directory, name + ext)

        # Save video
        clip.write_videofile(filename=cleaned_path, codec=codec, preset=preset)

        return cleaned_path if os.path.exists(cleaned_path) else None

    def create_comp(self, *clips, vfx: list[mp.Effect | None] = None , fps: int = 60):
        clip = mp.CompositeVideoClip(list(clips))
        if vfx:
            clip = clip.with_effects([fx for fx in vfx if fx])
        clip.fps = fps
        return clip

    def convert_image(self, image_path: str, output_name=None):

        if not self.audio:
            raise Exception("Audio isn't set, consider doing .set_audio() first")

        if output_name:
            self.output_name = output_name

        if not os.path.exists(image_path) or not os.path.isfile(image_path):
            raise FileExistsError("Image File Doesn't Exist")

        image = mp.ImageClip(image_path, duration=self.duration).with_effects(self.vfx)
        clip = self.create_comp(image, fps=30)
        clip.audio = self.audio
        fp = self.save_clip(clip, os.path.join(self.output_path, self.output_name))
        if not fp:
            raise Exception("Unable to save Video")

        return os.path.join(self.output_path, self.output_name)

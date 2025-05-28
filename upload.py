from instagrapi import Client
from instagrapi.types import Usertag
from pathlib import Path
from PIL import Image
import os
import json

SESSION_FILE = "session.json"


def save_session(cl: Client):
    session_data = cl.get_settings()
    with open(SESSION_FILE, "w") as f:
        json.dump(session_data, f)


def load_session(cl: Client):
    if not os.path.exists(SESSION_FILE):
        return False
    with open(SESSION_FILE, "r") as f:
        session_data = json.load(f)
    cl.set_settings(session_data)
    return True


def login(username: str, password: str):
    cl = Client()
    if load_session(cl):
        try:
            cl.login(username, password)
            print("[INFO] Logged in using saved session.")
            save_session(cl)
            return cl
        except Exception as e:
            print(f"[WARN] Session failed: {e}")

    # Fallback to new login
    cl = Client()
    cl.login(username, password)
    save_session(cl)
    print("[INFO] Logged in freshly.")
    return cl


def upload_reel(cl: Client, video_path: str, thumbnail_path: str, caption: str):
    video_path = Path(video_path)
    thumbnail_path = Path(thumbnail_path)

    if not video_path.exists() or not thumbnail_path.exists():
        raise FileNotFoundError("Video or thumbnail file does not exist.")

    # Instagram reels are videos with aspect ratio 9:16, ensure thumbnail matches that
    thumb = Image.open(thumbnail_path)
    if thumb.size[0] / thumb.size[1] != 9 / 16:
        print("[WARN] Thumbnail might not match Instagram's aspect ratio (9:16).")

    result = cl.clip_upload(
        video_path,
        caption=caption,
        thumbnail=thumbnail_path,
    )
    print("[SUCCESS] Reel uploaded:", result.dict().get("pk"))


if __name__ == "__main__":
    import getpass

    USERNAME = input("Instagram Username: ")
    PASSWORD = getpass.getpass("Instagram Password: ")

    VIDEO_FILE = input("Enter the path to the video: ")
    THUMBNAIL_FILE = input("Enter the path to the custom thumbnail: ")
    CAPTION = input("Entet the video caption: ")

    client = login(USERNAME, PASSWORD)
    upload_reel(client, VIDEO_FILE, THUMBNAIL_FILE, CAPTION)

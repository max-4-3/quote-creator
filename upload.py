from instagrapi import Client
from pathlib import Path
from PIL import Image
import os
import json


class Uploader:

    def __init__(self) -> None:
        self.session_path = "session"
        self.session_name = "session.json"
        self.video_path = None
        self.custom_thumbnail_path = None
        self.caption = None
        self.client: Client | None = None

        self.login()

    def gather_info(self, prompt: str, type="text"):
        print(prompt, end="")
        if type == "password":
            import getpass

            return getpass.getpass("")
        return input("")

    def save_client(self):
        session_data = self.client.get_settings()
        with open(os.path.join(self.session_path, self.session_name), "w") as f:
            json.dump(session_data, f)

    def load_client(self):
        if not os.path.exists(os.path.join(self.session_path, self.session_name)):
            return False
        self.client.load_settings(os.path.join(self.session_path, self.session_name))
        return True

    def login(self):
        self.client = Client()

        if self.load_client():
            try:
                print("[INFO] Logged in using saved session.")
                self.save_client()
                return self.client
            except Exception as e:
                print(f"[WARN] Session failed: {e}")

        # Fallback to new login

        self.client.login(
            self.gather_info("Enter Your Instagram Username: "),
            self.gather_info("Enter Your Instagram Password: ", type="password"),
        )
        self.save_client()
        print("[INFO] Logged in freshly.")
        return self.client

    def upload_reel(self, **kwargs):
        video_path = Path(
            kwargs.get("video_path") or self.gather_info("Enter Video Path: ")
        )
        thumbnail_path = Path(
            kwargs.get("thumb_path") or self.gather_info("Enter Custom thumb path: ")
        )

        if not video_path.exists() or not thumbnail_path.exists():
            raise FileNotFoundError("Video or thumbnail file does not exist.")

        # Instagram reels are videos with aspect ratio 9:16, ensure thumbnail matches that
        thumb = Image.open(thumbnail_path)
        if thumb.size[0] / thumb.size[1] != 9 / 16:
            print("[WARN] Thumbnail might not match Instagram's aspect ratio (9:16).")

        if not self.caption or self.caption is None:
            self.caption = self.gather_info("Enter the video caption: \n")

        result = self.client.clip_upload(
            video_path,
            caption=self.caption,
            thumbnail=thumbnail_path,
        )
        return result

import os

FINAL_VIDEO_PATH = os.path.join(os.path.split(__file__)[0], "output", "videos")
FINAL_IMAGE_PATH = os.path.join(os.path.split(__file__)[0], "output", "images")
BASE_URL = "https://zenquotes.io"
END_POINTS = {
    "daily": "/api/today",
    "random": "/api/random",
    "random_image": "/api/image",
    "quotes": "/api/quotes",
}
TAGS = ["#instagram", "#reels", "#quotes", "#foryou", "#inspirational"]
BODY = (
    ["." for _ in range(7)]
    + ["Follow For More", "@alone_grl.x.x"]
    + ["." for _ in range(6)]
    + [" ".join(TAGS)]
)
OPEN_QUOTE = "“"
CLOSE_QUOTE = "”"
TEMPLATE_IMAGES = [
    "/home/max/Extras/Python/Quotes/resources/template/images/bro.png",
    "/home/max/Extras/Python/Quotes/resources/template/images/what the intrusive thoughts whispered.png",
    "/home/max/Extras/Python/Quotes/resources/template/images/how i hacked the simulation (accidentally).png",
    "/home/max/Extras/Python/Quotes/resources/template/images/3am.png",
    "/home/max/Extras/Python/Quotes/resources/template/images/how dudes in ancient rome were probably vibing.png",
    "/home/max/Extras/Python/Quotes/resources/template/images/quote_of_the_day.png",
    "/home/max/Extras/Python/Quotes/resources/template/images/group_chat.png",
    "/home/max/Extras/Python/Quotes/resources/template/images/what i texted my ex during a lunar eclipse.png",
    "/home/max/Extras/Python/Quotes/resources/template/images/deamon_in_wall.png",
    "/home/max/Extras/Python/Quotes/resources/template/images/what the 2007 YouTube tutorial taught me.png",
]
TEMPLATE_VIDEOS = [
    "/home/max/Extras/Python/Quotes/resources/template/videos/_ [_@Pinterest] [41939840273995334].mp4",
    "/home/max/Extras/Python/Quotes/resources/template/videos/Kurt_Angle_Meme [Yadro_Green_Screen@Pinterest] [1009861916436216402].mp4",
    "/home/max/Extras/Python/Quotes/resources/template/videos/Pinterest_video_681591724875502878 [Peaky_Blinders@Pinterest] [681591724875502878].mp4",
]
FONTS = [
    "/home/max/Extras/Python/Quotes/resources/fonts/EBGaramond-Italic-VariableFont_wght.ttf",
    "/home/max/Extras/Python/Quotes/resources/fonts/EBGaramond-VariableFont_wght.ttf",
    "/home/max/Extras/Python/Quotes/resources/fonts/LibreBaskerville-Bold.ttf",
    "/home/max/Extras/Python/Quotes/resources/fonts/LibreBaskerville-Italic.ttf",
    "/home/max/Extras/Python/Quotes/resources/fonts/LibreBaskerville-Regular.ttf",
    "/home/max/Extras/Python/Quotes/resources/fonts/Lora-Italic-VariableFont_wght.ttf",
    "/home/max/Extras/Python/Quotes/resources/fonts/Lora-VariableFont_wght.ttf",
    "/home/max/Extras/Python/Quotes/resources/fonts/MerriweatherSans-Italic-VariableFont_wght.ttf",
    "/home/max/Extras/Python/Quotes/resources/fonts/MerriweatherSans-VariableFont_wght.ttf"
]
AUDIO_DATA = [
    {
        "file": "/home/max/Extras/Python/Quotes/resources/audio/Damned_slowed_reverb [Wexy@youtube] [nEFXGMGrrao].mp3",
        "file_name": "Damned_slowed_reverb [Wexy@youtube] [nEFXGMGrrao].mp3",
        "sections": [[10, 30], [69, 80], [95, 115]],
    },
    {
        "file": "/home/max/Extras/Python/Quotes/resources/audio/HANS_ZIMMER-TIME_SLOWED+REVERBED [SLOWBERB@youtube] [Run3bAGAO4s].mp3",
        "file_name": "HANS_ZIMMER-TIME_SLOWED+REVERBED [SLOWBERB@youtube] [Run3bAGAO4s].mp3",
        "sections": [[126, 146], [172, 200]],
    },
    {
        "file": "/home/max/Extras/Python/Quotes/resources/audio/The_Toxic_Avenger_-_Angst_Two_From_the_Nissan_Qashqai_Movie [Roy_Music@youtube] [nWUlpJ7X0fI].mp3",
        "file_name": "The_Toxic_Avenger_-_Angst_Two_From_the_Nissan_Qashqai_Movie [Roy_Music@youtube] [nWUlpJ7X0fI].mp3",
        "sections": [[247, 257]],
    },
    {
        "file": "/home/max/Extras/Python/Quotes/resources/audio/scarlxrd_-_HXW_THEY_JUDGE._audio [scarlxrd@youtube] [U4weEcBbDnM].mp3",
        "file_name": "scarlxrd_-_HXW_THEY_JUDGE._audio [scarlxrd@youtube] [U4weEcBbDnM].mp3",
        "sections": [[0, 40]],
    },
    {
        "file": "/home/max/Extras/Python/Quotes/resources/audio/Night_Lovell_Type_beat_-_Patience_DARK_TRAP_BEAT_Prod._Broque [Broque_Beats@youtube] [HXPXHZP-ZgE].mp3",
        "file_name": "Night_Lovell_Type_beat_-_Patience_DARK_TRAP_BEAT_Prod._Broque [Broque_Beats@youtube] [HXPXHZP-ZgE].mp3",
        "sections": [[20, 40], [90, 120], [129, 149], [170, 190]],
    },
    {
        "file": "/home/max/Extras/Python/Quotes/resources/audio/trevor_something_-_fade_away_slowed_+_reverb [ero@youtube] [9Ptx1XtPRo4].mp3",
        "file_name": "trevor_something_-_fade_away_slowed_+_reverb [ero@youtube] [9Ptx1XtPRo4].mp3",
        "sections": [[20, 40], [120, 150], [190, 230]],
    },
    {
        "file": "/home/max/Extras/Python/Quotes/resources/audio/FREE_BONES_x_NIGHT_LOVELL_TYPE_BEAT_-_NOTHING [killmeblxxd@youtube] [Elegu-DE7xo].mp3",
        "file_name": "FREE_BONES_x_NIGHT_LOVELL_TYPE_BEAT_-_NOTHING [killmeblxxd@youtube] [Elegu-DE7xo].mp3",
        "sections": [[0, 40]],
    },
    {
        "file": "/home/max/Extras/Python/Quotes/resources/audio/gta_iv_-_soviet_connection_slowed_+_reverb [N@youtube] [5OdfIiILjRQ].mp3",
        "file_name": "gta_iv_-_soviet_connection_slowed_+_reverb [N@youtube] [5OdfIiILjRQ].mp3",
        "sections": [[10, 40], [128, 148], [160, 180], [322, 344]],
    },
    {
        "file": "/home/max/Extras/Python/Quotes/resources/audio/Audiomachine_-_Blood_And_Stone_Ivan_Torrent_Remix [Jennyni20_Epic_Music@youtube] [W8-ZodiL1TA].mp3",
        "file_name": "Audiomachine_-_Blood_And_Stone_Ivan_Torrent_Remix [Jennyni20_Epic_Music@youtube] [W8-ZodiL1TA].mp3",
        "sections": [[25, 55], [124, 144]],
    },
]

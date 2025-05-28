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

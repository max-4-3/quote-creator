import requests, os, json
from models import Quote
from consts import BASE_URL, END_POINTS
from datetime import datetime


class QuoteCreator:
    def __init__(self, **kwargs) -> None:
        self.session: requests.Session | None = kwargs.get("session")
        self.save_path = kwargs.get("save_path") or "quotes"
        self.file_name = kwargs.get("file_name") or "quotes.json"

        os.makedirs(self.save_path, exist_ok=True)
        self.quotes: list[Quote] = self.load_quotes()

    def add_headers(self, headers: dict[str, str]):
        self.session.headers.update(headers)
        return self.session

    def make_request(self, url: str, **kwargs) -> list[dict]:

        if self.session is None:
            self.session = requests.Session()

        resp = self.session.get(url, **kwargs)
        resp.raise_for_status()
        try:
            return resp.json()
        except:
            return [None]

    def get_quote_of_day(self) -> Quote:
        for quote in self.quotes:
            if quote.time == datetime.now().strftime("%Y-%m-%d"):
                return quote

        response = self.make_request(BASE_URL + END_POINTS["daily"])[0]
        if not response:
            raise ValueError("Not able to get quote!")

        q = Quote(
            quote=response.get("q"),
            author=response.get("a"),
            quote_html=response.get("h"),
        )
        self.quotes.append(q)
        self.save_quotes()
        return q

    def save_quotes(self):
        with open(
            os.path.join(self.save_path, self.file_name),
            "w",
            errors="ignore",
            encoding="utf-8",
        ) as file:
            json.dump(
                [m.model_dump() for m in self.quotes],
                file,
                indent=4,
                ensure_ascii=False,
            )
        return True

    def load_quotes(self) -> list[Quote]:
        if not os.path.exists(os.path.join(self.save_path, self.file_name)):
            return []

        with open(
            os.path.join(self.save_path, self.file_name),
            "r",
            errors="ignore",
            encoding="utf-8",
        ) as file:
            return [Quote(**m) for m in json.load(file) if isinstance(m, dict)]

    


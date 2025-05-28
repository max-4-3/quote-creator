from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from consts import OPEN_QUOTE, CLOSE_QUOTE


class Quote(BaseModel):
    quote: str = Field(..., description="The Quote")
    author: str = Field(..., description="The Author of this quote")
    quote_html: str = Field(..., description="The HTML version of the quote")
    time: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d"),
        description="The Fetch date of This Quote",
    )

    @field_validator("quote", mode="before")
    @classmethod
    def wrap_quote(cls, v: str) -> str:
        v = v.strip()
        if not (v.startswith(OPEN_QUOTE) and v.endswith(CLOSE_QUOTE)):
            return OPEN_QUOTE + v + CLOSE_QUOTE
        return v

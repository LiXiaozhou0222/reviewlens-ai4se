from typing import Literal

from pydantic import BaseModel


class AppSettings(BaseModel):
    mode: Literal["private", "demo"]

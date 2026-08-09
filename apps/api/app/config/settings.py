from typing import Literal, Mapping

from pydantic import BaseModel


class AppSettings(BaseModel):
    mode: Literal["private", "demo"]


def load_settings(env: Mapping[str, str]) -> AppSettings:
    return AppSettings.model_validate({"mode": env.get("APP_MODE")})

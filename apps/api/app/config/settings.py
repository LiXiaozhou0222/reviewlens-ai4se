from typing import Literal, Mapping

from pydantic import BaseModel


class AppSettings(BaseModel):
    mode: Literal["private", "demo"]


class StartupConfigurationError(ValueError):
    """Raised when a required startup setting is missing or invalid."""


def load_settings(env: Mapping[str, str]) -> AppSettings:
    mode = env.get("APP_MODE")
    if mode not in ("private", "demo"):
        raise StartupConfigurationError(
            "APP_MODE must be explicitly set to 'private' or 'demo'."
        )

    return AppSettings(mode=mode)

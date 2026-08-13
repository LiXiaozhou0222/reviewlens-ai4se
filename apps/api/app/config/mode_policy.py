from dataclasses import dataclass

from app.models.domain import ReviewMode


@dataclass(frozen=True)
class ModeCapabilities:
    report_persistence: bool
    report_history: bool
    ai_retry: bool
    persistent_export: bool
    credential_management: bool


def mode_capabilities(mode: ReviewMode) -> ModeCapabilities:
    if mode is ReviewMode.DEMO:
        return ModeCapabilities(False, False, False, False, False)

    if mode is ReviewMode.PRIVATE:
        return ModeCapabilities(True, True, True, True, True)

    raise ValueError(f"Unsupported review mode: {mode!r}")

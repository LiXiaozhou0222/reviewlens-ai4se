from enum import StrEnum


class ReviewMode(StrEnum):
    PRIVATE = "private"
    DEMO = "demo"


class Severity(StrEnum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    NONE = "None"


class FindingSource(StrEnum):
    GENERAL_RULE = "general_rule"
    LANGUAGE_RULE = "language_rule"
    AI = "ai"


class AIReviewStatus(StrEnum):
    NOT_CONFIGURED = "NOT_CONFIGURED"
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    AUTH_FAILED = "AUTH_FAILED"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    RATE_LIMITED = "RATE_LIMITED"
    TIMEOUT = "TIMEOUT"
    INPUT_TOO_LARGE = "INPUT_TOO_LARGE"
    INVALID_RESPONSE = "INVALID_RESPONSE"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"

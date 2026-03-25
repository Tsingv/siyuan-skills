class SiYuanSkillError(Exception):
    """Base exception for the SiYuan skill."""


class RuntimeDependencyError(SiYuanSkillError):
    """Raised when required runtime dependencies are unavailable."""


class SiYuanConfigError(SiYuanSkillError):
    """Raised when required configuration is missing or invalid."""


class SiYuanConnectionError(SiYuanSkillError):
    """Raised when the local SiYuan service cannot be reached."""


class SiYuanAuthError(SiYuanSkillError):
    """Raised when authentication fails."""


class SiYuanApiError(SiYuanSkillError):
    """Raised when the SiYuan API returns a non-zero code."""

    def __init__(self, endpoint: str, code: int | str, message: str, payload: object | None = None):
        self.endpoint = endpoint
        self.code = code
        self.message = message
        self.payload = payload
        super().__init__(f"SiYuan API Error ({endpoint}, code={code}): {message}")

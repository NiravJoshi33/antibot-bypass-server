import os
from pydantic import field_validator  # type: ignore[import-not-found]
from pydantic_settings import BaseSettings  # type: ignore[import-not-found]


class Settings(BaseSettings):
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_DEBUG: bool = False

    BRIGHTDATA_CDP_ENDPOINT: str = ""

    DEFAULT_TIMEOUT: int = 30000
    MAX_RETRIES: int = 3

    # auth
    API_KEY: str = ""
    ENABLE_AUTH: bool = os.getenv("ENABLE_AUTH", "false").lower() == "true"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @field_validator("BRIGHTDATA_CDP_ENDPOINT")
    def validate_brightdata_cdp_endpoint(cls, v: str) -> str:
        if not v or v == "":
            raise ValueError("BRIGHTDATA_CDP_ENDPOINT is required")
        if not (v.startswith("https://") or v.startswith("wss://")):
            raise ValueError(
                "BRIGHTDATA_CDP_ENDPOINT must start with https:// or wss://"
            )
        return v


settings = Settings()

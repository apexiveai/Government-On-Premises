from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "ApexiveAI Municipal OS"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = False

    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str

    KEYCLOAK_URL: str
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_ISSUER: str
    KEYCLOAK_AUDIENCE: str

    JWT_ALGORITHM: str = "RS256"

    CORS_ORIGINS: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def jwks_url(self) -> str:
        return (
            f"{self.KEYCLOAK_URL.rstrip('/')}"
            f"/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/certs"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
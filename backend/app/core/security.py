
from functools import lru_cache

import httpx
from jose import JWTError, jwt

from app.core.config import settings


@lru_cache(maxsize=1)
def get_jwks() -> dict:
    jwks_url = (
        f"{settings.KEYCLOAK_URL.rstrip('/')}"
        f"/realms/{settings.KEYCLOAK_REALM}"
        "/protocol/openid-connect/certs"
    )

    with httpx.Client(timeout=10.0) as client:
        response = client.get(jwks_url)
        response.raise_for_status()
        return response.json()


def verify_access_token(token: str) -> dict:
    try:
        jwks = get_jwks()

        unverified_header = jwt.get_unverified_header(token)
        key_id = unverified_header.get("kid")

        if not key_id:
            raise ValueError("Token header has no key ID")

        signing_key = next(
            (
                key
                for key in jwks.get("keys", [])
                if key.get("kid") == key_id
            ),
            None,
        )

        if signing_key is None:
            get_jwks.cache_clear()
            jwks = get_jwks()

            signing_key = next(
                (
                    key
                    for key in jwks.get("keys", [])
                    if key.get("kid") == key_id
                ),
                None,
            )

        if signing_key is None:
            raise ValueError("Signing key not found")

        claims = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=settings.KEYCLOAK_ISSUER,
            audience=settings.KEYCLOAK_AUDIENCE,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iss": True,
                "verify_aud": True,
                "require_exp": True,
                "require_sub": True,
            },
        )

        return claims

    except (JWTError, ValueError, httpx.HTTPError) as exc:
        raise ValueError("Token verification failed") from exc

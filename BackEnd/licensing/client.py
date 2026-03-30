import logging
from typing import Dict, Tuple
import requests


logger = logging.getLogger(__name__)


class LicenseServerError(Exception):
    pass


def post_license_validation(
    license_server_url: str,
    payload: Dict[str, str],
    token: str = "",
    timeout_seconds: int = 8,
) -> Tuple[bool, Dict]:
    if not license_server_url:
        raise LicenseServerError("LICENSE_SERVER_URL is not configured")

    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.post(
            license_server_url,
            json=payload,
            headers=headers,
            timeout=timeout_seconds,
        )
    except requests.RequestException as exc:
        raise LicenseServerError(f"License server request failed: {exc}") from exc

    if response.status_code >= 500:
        raise LicenseServerError(f"License server returned {response.status_code}")

    try:
        data = response.json()
    except ValueError as exc:
        raise LicenseServerError("License server returned non-JSON response") from exc

    # Normalize several response formats
    is_valid = bool(
        data.get("valid")
        or data.get("is_valid")
        or str(data.get("status", "")).lower() in {"active", "valid"}
    )
    return is_valid, data

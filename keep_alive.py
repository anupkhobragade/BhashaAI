import os
import sys
from datetime import datetime, timezone

import requests


DEFAULT_TIMEOUT_SECONDS = 30
VALID_STATUSES = {200, 301, 302, 307, 308}


def get_target_url() -> str:
    target_url = os.getenv("KEEP_ALIVE_URL", "").strip()
    if not target_url:
        raise ValueError(
            "KEEP_ALIVE_URL is not set. Configure it in Render with your live app URL, "
            "for example https://bhashaai.onrender.com/."
        )
    return target_url


def ping(url: str, timeout_seconds: int) -> requests.Response:
    headers = {
        "User-Agent": "BhashaAI-KeepAlive/1.0",
        "Cache-Control": "no-cache",
    }
    return requests.get(url, headers=headers, timeout=timeout_seconds)


def main() -> int:
    timestamp = datetime.now(timezone.utc).isoformat()
    timeout_seconds = int(os.getenv("KEEP_ALIVE_TIMEOUT", DEFAULT_TIMEOUT_SECONDS))

    try:
        target_url = get_target_url()
        response = ping(target_url, timeout_seconds)

        print(
            f"[{timestamp}] keep-alive ping -> {target_url} "
            f"status={response.status_code} elapsed={response.elapsed.total_seconds():.2f}s"
        )

        if response.status_code not in VALID_STATUSES:
            print(f"Unexpected status code: {response.status_code}", file=sys.stderr)
            return 1

        return 0
    except Exception as exc:
        print(f"[{timestamp}] keep-alive ping failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

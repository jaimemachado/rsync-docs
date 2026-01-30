from typing import Any
import time
import requests
from urllib.parse import urljoin


def _build_url(base: str) -> str:
    # use the process-pdf endpoint which returns a processed PDF
    base = base.rstrip("/")
    return urljoin(base + "/", "process-pdf")


def call_ocr(file_bytes: bytes, filename: str, base_url: str) -> bytes | Any:
    """Send file to OCR service `/process-pdf` and return raw bytes (PDF).

    Returns bytes when the service returns a PDF; if the service returns JSON
    for some reason, the parsed JSON will be returned instead.
    """
    url = _build_url(base_url)
    files = {"file": (filename, file_bytes)}

    for attempt in range(3):
        try:
            resp = requests.post(url, files=files, timeout=120)
            resp.raise_for_status()
            content_type = resp.headers.get("content-type", "")
            if "application/json" in content_type:
                return resp.json()
            return resp.content
        except requests.RequestException:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)

from typing import Any
import time
import logging
import requests
from urllib.parse import urljoin

logger = logging.getLogger("app.ocr_client")


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

    for attempt in range(1, 4):
        logger.debug("POST %s attempt=%d filename=%s", url, attempt, filename)
        start = time.monotonic()
        try:
            resp = requests.post(url, files=files, timeout=120)
            duration = time.monotonic() - start
            logger.info("OCR response: url=%s status=%d duration=%.2fs", url, getattr(resp, 'status_code', None), duration)
            resp.raise_for_status()
            content_type = resp.headers.get("content-type", "")
            content_len = len(resp.content) if resp.content is not None else 0
            logger.debug("Response content-type=%s content-length=%d", content_type, content_len)
            if "application/json" in content_type:
                try:
                    j = resp.json()
                except Exception:
                    logger.exception("Failed to parse JSON response from OCR service")
                    raise
                return j
            return resp.content
        except requests.RequestException as exc:
            logger.warning("Request to OCR failed (attempt=%d): %s", attempt, exc)
            if attempt >= 3:
                logger.exception("Final attempt failed, raising")
                raise
            backoff = 2 ** (attempt - 1)
            logger.debug("Sleeping %s seconds before retry", backoff)
            time.sleep(backoff)

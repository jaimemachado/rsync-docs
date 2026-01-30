from pathlib import Path
import os
import logging
import json
import time

from app.ocr_client import call_ocr


def _setup_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    logging.basicConfig(level=level, format=fmt)


def process_files(input_dir: str, output_dir: str, ocr_url: str) -> None:
    logger = logging.getLogger("app.main")
    p_in = Path(input_dir)
    p_out = Path(output_dir)
    p_out.mkdir(parents=True, exist_ok=True)

    if not p_in.exists():
        logger.warning("Input directory does not exist: %s", input_dir)
        return

    files = [f for f in sorted(p_in.iterdir()) if f.is_file()]
    logger.info("Found %d files in %s", len(files), input_dir)

    allowed_exts = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}

    for f in files:
        suffix = f.suffix.lower()
        if suffix not in allowed_exts:
            logger.debug("Skipping file with unsupported extension: %s (suffix=%s)", f.name, suffix)
            continue
        try:
            size = f.stat().st_size
            logger.info("Processing %s (size=%d bytes)", f.name, size)
            start = time.monotonic()
            with f.open("rb") as fh:
                data = fh.read()
                result = call_ocr(data, f.name, ocr_url)

            duration = time.monotonic() - start

            # If the OCR service returned bytes (processed PDF), write binary
            if isinstance(result, (bytes, bytearray)):
                out_file = p_out / (f.name + ".processed.pdf")
                with out_file.open("wb") as of:
                    of.write(result)
                logger.info("Wrote PDF output: %s (%.2fs, %d bytes)", out_file.name, duration, out_file.stat().st_size)
            else:
                out_file = p_out / (f.name + ".json")
                with out_file.open("w", encoding="utf-8") as of:
                    json.dump(result, of, ensure_ascii=False, indent=2)
                logger.info("Wrote JSON output: %s (%.2fs, %d bytes)", out_file.name, duration, out_file.stat().st_size)

            # Delete the original input file after successful processing
            try:
                f.unlink()
                logger.info("Deleted input file: %s", f.name)
            except Exception:
                logger.warning("Failed to delete input file: %s", f.name, exc_info=True)

        except Exception:
            logger.exception("Failed to process %s", f.name)


def main() -> None:
    _setup_logging()
    logger = logging.getLogger("app.main")
    input_dir = os.getenv("INPUT_DIR", "/data/in")
    output_dir = os.getenv("OUTPUT_DIR", "/data/out")
    ocr_url = os.getenv("OCR_SERVICE_URL", "http://ocr-service:8000")

    logger.info("Starting OCR worker. input=%s output=%s ocr_url=%s", input_dir, output_dir, ocr_url)
    process_files(input_dir, output_dir, ocr_url)
    logger.info("Finished processing run")


if __name__ == "__main__":
    main()

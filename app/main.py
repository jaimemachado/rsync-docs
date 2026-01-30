from pathlib import Path
import os
import logging
import json
from typing import Any

from app.ocr_client import call_ocr


def process_files(input_dir: str, output_dir: str, ocr_url: str) -> None:
    p_in = Path(input_dir)
    p_out = Path(output_dir)
    p_out.mkdir(parents=True, exist_ok=True)

    if not p_in.exists():
        logging.warning("Input directory does not exist: %s", input_dir)
        return

    for f in sorted(p_in.iterdir()):
        if not f.is_file():
            continue
        logging.info("Processing %s", f.name)
        try:
            with f.open("rb") as fh:
                result = call_ocr(fh.read(), f.name, ocr_url)

            # If the OCR service returned bytes (processed PDF), write binary
            if isinstance(result, (bytes, bytearray)):
                out_file = p_out / (f.name + ".processed.pdf")
                with out_file.open("wb") as of:
                    of.write(result)
            else:
                out_file = p_out / (f.name + ".json")
                with out_file.open("w", encoding="utf-8") as of:
                    json.dump(result, of, ensure_ascii=False, indent=2)

            logging.info("Wrote output: %s", out_file)
        except Exception:
            logging.exception("Failed to process %s", f.name)


def main() -> None:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    input_dir = os.getenv("INPUT_DIR", "/data/in")
    output_dir = os.getenv("OUTPUT_DIR", "/data/out")
    ocr_url = os.getenv("OCR_SERVICE_URL", "http://ocr-service:8000")

    process_files(input_dir, output_dir, ocr_url)


if __name__ == "__main__":
    main()

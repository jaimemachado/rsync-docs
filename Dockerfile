FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV INPUT_DIR=/data/in
ENV OUTPUT_DIR=/data/out
ENV OCR_SERVICE_URL=http://ocr-service

CMD ["python", "-u", "-m", "app.main"]

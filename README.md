# OCR CronJob Worker

This small app reads files from an input folder, calls an OCR service, and writes results as JSON into an output folder. It's intended to run as a CronJob in Kubernetes.

Instructions used: [clean-architecture.instructions.md, coding-style-python.instructions.md, domain-driven-design.instructions.md, follow-up-question.instructions.md, meta-instructions.instructions.md, object-calisthenics.instructions.md, security-and-owasp.instructions.md, unit-and-integration-tests.instructions.md, conventional-commits.instructions.md]

Usage

- Build image:

```sh
docker build -t your-registry/ocr-worker:latest .
```

- Run locally (bind mount folders):

```sh
docker run --rm -e OCR_SERVICE_URL=http://host.docker.internal:8000 -v $(pwd)/data/in:/data/in -v $(pwd)/data/out:/data/out your-registry/ocr-worker:latest
```

Environment

- `INPUT_DIR` — input directory (default `/data/in`)
- `OUTPUT_DIR` — output directory (default `/data/out`)
- `OCR_SERVICE_URL` — base URL of the OCR service (default `http://ocr-service`)

Kubernetes

- Edit `k8s/cronjob.yaml` and replace `REPLACE_WITH_IMAGE` with your image, and replace the `emptyDir` volumes with PVCs or other volume types suitable for your cluster.

Notes

- The worker posts files to the OCR service endpoint at `{{OCR_SERVICE_URL}}/process-pdf` and writes the returned PDF (saved as `<filename>.processed.pdf`). If the service returns JSON the worker will save it as `<filename>.json`.

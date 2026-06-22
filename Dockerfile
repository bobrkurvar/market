FROM python:3.11-slim AS base

WORKDIR /app
COPY req.txt .
RUN pip install --no-cache-dir -r req.txt
COPY core ./core

FROM base AS main
COPY main.py .
COPY api ./api
COPY db ./db
COPY domain ./domain
COPY infra ./infra
COPY adapters ./adapters
COPY services ./services
COPY tasks ./tasks
COPY shared.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS worker
COPY adapters ./adapters
COPY db ./db
COPY domain ./domain
COPY tasks ./tasks
COPY services ./services
COPY infra ./infra
CMD ["taskiq", "worker", "tasks.broker:broker"]

FROM worker AS scheduler
CMD ["taskiq", "scheduler", "tasks.broker:scheduler"]


FROM base AS image
COPY img_service.py .
COPY shared.py .
CMD ["sh", "-c", "uvicorn img_service:app --host 0.0.0.0 --port ${PORT}"]


FROM node:22-alpine AS builder
WORKDIR /app
COPY frontend/package*.json .
RUN npm install
COPY frontend .
#ENV NODE_OPTIONS="--max-old-space-size=4096"
RUN npx nuxt generate

FROM nginx:1.27-alpine AS frontend
COPY --from=builder /app/.output/public /var/www/frontend


FROM base AS migrate
COPY alembic.ini .
COPY migrations migrations
COPY db db
COPY domain domain
CMD ["alembic", "upgrade", "head"]


FROM base AS scripts
COPY infra/security.py ./infra/security.py
COPY adapters ./adapters
COPY infra ./infra
COPY domain ./domain
COPY services ./services
COPY db ./db
COPY scripts ./scripts
COPY shared.py ./shared.py
CMD ["python", "-m", "scripts"]










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

# FROM node:22-alpine AS frontend
# WORKDIR /app
# COPY --from=frontend_builder app/.output .output
# CMD ["node", ".output/server/index.mjs"]


FROM base AS migrate
COPY alembic.ini .
COPY migrations migrations
COPY db db
CMD ["alembic", "upgrade", "head"]

FROM base AS runner
COPY infra/security.py ./infra/security.py
COPY adapters ./adapters
COPY domain ./domain
COPY services ./services
COPY db ./db
COPY scripts/db_init.py ./db_init.py
COPY shared.py ./shared.py
CMD ["python", "-m", "db_init"]

FROM base AS init_test_data
COPY infra/security.py ./infra/security.py
COPY adapters ./adapters
COPY domain ./domain
COPY services ./services
COPY db ./db
COPY scripts/init_test_data.py .
COPY shared.py ./shared.py
CMD ["python", "-m", "init_test_data"]










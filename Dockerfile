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
COPY adapters adapters
COPY services ./services
COPY tasks ./tasks
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


FROM node:22-alpine AS frontend_builder
WORKDIR /app
COPY frontend/package*.json .
RUN npm install
COPY frontend .
ENV NODE_OPTIONS="--max-old-space-size=4096"
RUN npm run build

FROM node:22-alpine AS frontend
WORKDIR /app
COPY --from=frontend_builder app/.output .output
CMD ["node", ".output/server/index.mjs"]


FROM base AS migrate
COPY alembic.ini .
COPY migrations migrations
COPY db db
CMD ["alembic", "upgrade", "head"]

FROM base AS runner
COPY infra/security.py infra/security.py
COPY adapters/db.py adapters/db.py
COPY adapters/db_provider.py adapters/db_provider.py
COPY domain domain
COPY db db
COPY scripts/add_admins.py ./add_admins.py
CMD ["python", "-m", "db_init"]










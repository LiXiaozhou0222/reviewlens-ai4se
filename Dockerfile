FROM node:22-bookworm-slim AS web-build

WORKDIR /web

COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci
COPY apps/web ./
RUN npm run build

FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY apps/api/requirements.lock ./requirements.lock
RUN pip install --no-cache-dir -r requirements.lock
COPY apps/api/app ./app
COPY --from=web-build /web/dist /app/web

EXPOSE 8080

CMD ["uvicorn", "app.main:create_runtime_app", "--factory", "--host", "0.0.0.0", "--port", "8080"]

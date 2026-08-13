.PHONY: install test lint build

install:
	python -m pip install -r apps/api/requirements.lock
	cd apps/web && npm ci

test:
	cd apps/api && python -m pytest -q --basetemp=.pytest-make
	cd apps/web && npm run test -- --run

lint:
	cd apps/web && npm run typecheck

build:
	cd apps/web && npm run build
	docker buildx build --platform linux/amd64 --load -t reviewlens:test .

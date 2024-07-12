export PYTHONPATH := ${PYTHONPATH}:./create_llama/backend
export CREATE_LLAMA_VERSION=0.1.18
export NEXT_PUBLIC_API_URL=/api/chat

create-llama-app:
	mkdir -p create_llama
	cp -r ./create_llama_local/* create_llama/

patch-chat: create-llama-app
	cp -r ./patch/* ./create_llama/

build-chat: patch-chat
	@echo "\nBuilding Chat UI..."
	cd ./create_llama/frontend && pnpm install && pnpm run build
	@echo "\nCopying Chat UI to static folder..."
	mkdir -p ./static && cp -r ./create_llama/frontend/out/* ./static/
	@echo "\nDone!"

build-admin:
	@echo "\nBuilding Admin UI..."
	cd ./admin && pnpm install && pnpm run build
	@echo "\nCopying Admin UI to static folder..."
	mkdir -p ./static/admin && cp -r ./admin/out/* ./static/admin/
	@echo "\nDone!"

build-frontends: patch-chat

run:
	poetry run python main.py

dev:
# Start the backend and frontend servers
# Kill both servers if a stop signal is received
	@export ENVIRONMENT=dev; \
	trap 'kill 0' SIGINT; \
	poetry run python main.py & \
	pnpm --prefix ./admin run dev & \
	wait

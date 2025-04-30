.PHONY: up down deps curl


deps:
	poetry lock 
	docker build -t retail_main_server .

up:
	docker compose up -d --build

down:
	docker compose down

one-time:
	curl -sSL https://install.python-poetry.org | python3 -

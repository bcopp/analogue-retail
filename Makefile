.PHONY: up down deps curl


deps:
	poetry lock 
	docker build -t retail_main_server .

up:
	docker compose up -d --build

down:
	docker compose down

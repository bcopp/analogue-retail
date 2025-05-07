.PHONY: up down deps curl


deps:
	poetry lock 
	docker build -t retail_main_server .

up:
	GOOGLE_APPLICATION_CREDENTIALS="${HOME}/.config/gcloud/application_default_credentials.json" \
	docker compose up -d --build

down:
	GOOGLE_APPLICATION_CREDENTIALS="${HOME}/.config/gcloud/application_default_credentials.json" \
	docker compose down

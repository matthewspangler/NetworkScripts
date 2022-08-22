build:
	docker-compose build --pull

stack-up:
	docker-compose up -d

stack-purge:
	docker-compose stop
	docker-compose kill
	docker-compose rm

stack-full-refresh:
	docker-compose build --no-cache --pull

build:
	docker-compose build ms_selenium_jobs --pull

run:
	docker-compose run --rm ms_selenium_jobs python3 /home/ms_selenium_jobs/scripts/luxor_delete_machines.py

bash:
	docker-compose run --rm --entrypoint "/bin/bash -c" ms_selenium_jobs bash

launch:
	docker-compose -f docker-compose.yaml up 

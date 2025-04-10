all: up

up: 
#	mkdir -p data/db
#	mkdir -p data/web
	docker-compose -f srcs/docker-compose.yml up -d

down: 
	docker-compose -f srcs/docker-compose.yml down

start: 
	docker-compose -f srcs/docker-compose.yml start

stop: 
	docker-compose -f srcs/docker-compose.yml stop

fclean: 
	docker-compose -f srcs/docker-compose.yml down
	docker rmi django:42 postgres:42 nginx:42
	docker volume rm srcs_web_data
	docker volume rm srcs_db_data
#	docker run --rm -v $(pwd)/data:/data alpine rm -rf /data/db

populate_secrets:
	bash scripts/get_ip.sh | sed 's/$$/:4443/' > secrets/web_host.txt

clean_migrations:
	bash scripts/delete_cache.sh
	
re: fclean all

status: 
	docker ps

.PHONY: all, clean, fclean, re, up, down, start, stop, status
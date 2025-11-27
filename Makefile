up:
	docker compose -f docker-compose-local.yml ip -d 

down:
	docker compose -f docker-compose-local.yml down && docker network prune --force
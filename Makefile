# Task 1: Server container
SERVER_IMAGE=fastapi-server

# Task 3: Load balancer
LB_DIR=load_balancer
LB_IMAGE=loadbalancer
COMPOSE=docker-compose
PORT=5000

.PHONY: all build-server run-server stop-server build-lb up-lb down-lb rebuild clean

# Run both
all: build-server run-server

### Task 1: Server Commands ###

build-server:
	docker build -t $(SERVER_IMAGE) .

run-server:
	docker run --rm -e SERVER_ID=1 -p $(PORT):5000 --name server1 $(SERVER_IMAGE)

stop-server:
	docker stop server1 || true
	docker rm server1 || true

### Task 3: Load Balancer Commands ###

build-lb:
	$(COMPOSE) build

up-lb:
	$(COMPOSE) up -d

down-lb:
	$(COMPOSE) down

rebuild: down-lb build-lb up-lb

### Clean Docker artifacts ###
clean:
	docker image prune -f
	docker container prune -f


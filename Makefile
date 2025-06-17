IMAGE_NAME=fastapi-server
CONTAINER_NAME=server1
port=5000
SERVER_ID=1

.PHONY: all build run stop rebuild clean

# Default Target
all: build run

# Build the Docker image
build:
	docker build -t $(IMAGE_NAME) .

# Run the Docker Container
run:
	docker run --rm -e SERVER_ID=$(SERVER_ID) -p $(PORT):5000 --name $(CONTAINER_NAME) $(IMAGE_NAME)

# Stop the running container
stop:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

# Rebuild and rerun
rebuild: stop build run

# Clean up dangling images
clean:
	docker image prune -f

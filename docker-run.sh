#!/bin/bash

set -e

echo "========================================="
echo "Running AI Chat Bot Container"
echo "========================================="
echo ""

# Container settings
CONTAINER_NAME="ai-chatbot-app"
IMAGE_NAME="ai-chatbot:latest"
HOST_PORT=3012

# Check if container is already running
if [ "$(docker ps -q -f name=${CONTAINER_NAME})" ]; then
    echo "Container ${CONTAINER_NAME} is already running"
    echo "Stop it with: docker stop ${CONTAINER_NAME}"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "✗ .env file not found"
    echo "Please create .env file with your configuration"
    exit 1
fi

echo "Starting container..."
echo "Container name: ${CONTAINER_NAME}"
echo "Host port: ${HOST_PORT}"
echo ""

# Run the container
docker run -d \
  --name ${CONTAINER_NAME} \
  --env-file .env \
  -p ${HOST_PORT}:8000 \
  --restart unless-stopped \
  ${IMAGE_NAME}

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✓ Container started successfully!"
    echo "========================================="
    echo ""
    echo "Container name: ${CONTAINER_NAME}"
    echo "API endpoint: http://localhost:${HOST_PORT}"
    echo "API docs: http://localhost:${HOST_PORT}/docs"
    echo ""
    echo "Useful commands:"
    echo "  View logs:        docker logs -f ${CONTAINER_NAME}"
    echo "  Stop container:   docker stop ${CONTAINER_NAME}"
    echo "  Remove container: docker rm ${CONTAINER_NAME}"
    echo "  Container shell:  docker exec -it ${CONTAINER_NAME} /bin/bash"
    echo ""
    echo "Viewing logs (press Ctrl+C to exit)..."
    sleep 2
    docker logs -f ${CONTAINER_NAME}
else
    echo ""
    echo "✗ Failed to start container"
    exit 1
fi

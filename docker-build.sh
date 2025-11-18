#!/bin/bash

set -e

echo "========================================="
echo "Building AI Chat Bot Docker Image"
echo "========================================="
echo ""

# Image name
IMAGE_NAME="ai-chatbot"
IMAGE_TAG="latest"

# Build the image
echo "Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✓ Docker image built successfully!"
    echo "========================================="
    echo ""
    echo "Image: ${IMAGE_NAME}:${IMAGE_TAG}"
    echo ""
    echo "To run the container:"
    echo "  ./docker-run.sh"
    echo ""
else
    echo ""
    echo "✗ Failed to build Docker image"
    exit 1
fi

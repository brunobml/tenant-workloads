#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TAG="${1:-v1.0.0}"
REGISTRY_HOST="${REGISTRY_HOST:-localhost:5001}"
IMAGE_NAME="orders-processor"
FULL_IMAGE="${REGISTRY_HOST}/${IMAGE_NAME}:${TAG}"

echo "============================================================"
echo "  CI Build & Push Pipeline: ${FULL_IMAGE}"
echo "============================================================"

echo -e "\n🔨 [1/2] Building container image with Docker..."
docker build -t "${FULL_IMAGE}" "${SCRIPT_DIR}"

echo -e "\n🚀 [2/2] Pushing image to registry ${REGISTRY_HOST}..."
docker push "${FULL_IMAGE}"

echo -e "\n✔ Image published successfully: ${FULL_IMAGE}"
echo "  In-Cluster pull reference: k3d-cloud-registry:5000/${IMAGE_NAME}:${TAG}"

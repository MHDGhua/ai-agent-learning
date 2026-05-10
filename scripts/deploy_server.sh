#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/lerap-pro}"
DEPLOY_BRANCH="${DEPLOY_BRANCH:-main}"
REPO_URL="${REPO_URL:-}"

if [[ ! -d "${PROJECT_DIR}" ]]; then
  mkdir -p "${PROJECT_DIR}"
fi

if [[ ! -d "${PROJECT_DIR}/.git" ]]; then
  if [[ -z "${REPO_URL}" ]]; then
    echo "Missing git repository in ${PROJECT_DIR}"
    echo "Set REPO_URL to your project repository URL for the first deployment."
    exit 1
  fi

  rm -rf "${PROJECT_DIR}"
  git clone --branch "${DEPLOY_BRANCH}" "${REPO_URL}" "${PROJECT_DIR}"
fi

if [[ ! -f "${PROJECT_DIR}/.env.production" ]]; then
  echo "Missing ${PROJECT_DIR}/.env.production"
  echo "Copy .env.production.example to .env.production and fill in your real API key first."
  exit 1
fi

cd "${PROJECT_DIR}"

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "Missing git remote: origin"
  echo "Run: git remote add origin <your-repository-url>"
  exit 1
fi

git fetch --all --prune
git checkout "${DEPLOY_BRANCH}"
git pull --ff-only origin "${DEPLOY_BRANCH}"

docker compose up -d --build
docker compose ps

echo
echo "Deployment finished from git branch: ${DEPLOY_BRANCH}"
echo "Check logs with:"
echo "  docker compose logs -f app"
echo "  docker compose logs -f caddy"

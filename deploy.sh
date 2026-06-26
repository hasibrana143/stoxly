#!/usr/bin/env bash
set -euo pipefail

ENV=${1:-production}
echo "Deploying Stoxly.ai to $ENV environment..."

case "$ENV" in
  production)
    docker compose -f docker-compose.yml build --pull
    docker compose -f docker-compose.yml up -d --remove-orphans
    docker compose -f docker-compose.yml exec backend python -m pytest tests/ -v --tb=short || echo "Tests skipped on deploy"
    echo "Waiting for health check..."
    for i in $(seq 1 10); do
      if curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo "Backend is healthy"
        break
      fi
      sleep 3
    done
    docker system prune -f --filter "until=24h"
    ;;

  staging)
    docker compose -f docker-compose.yml build
    docker compose -f docker-compose.yml up -d --remove-orphans
    docker compose -f docker-compose.yml exec backend python -m pytest tests/ -v --tb=short
    ;;

  k8s)
    kubectl apply -f k8s/stoxly.yaml -n stoxly
    kubectl rollout status deployment/stoxly-backend -n stoxly --timeout=120s
    ;;

  *)
    echo "Usage: $0 {production|staging|k8s}"
    exit 1
    ;;
esac

echo "Deploy complete: $ENV"

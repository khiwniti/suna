#!/usr/bin/env bash
# ============================================================================
# Carbon BIM — Full Deploy Script
# Usage: ./deploy/deploy.sh [--build] [--down]
# ============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

BUILD_FLAG=""
if [[ "${1:-}" == "--build" ]]; then
  BUILD_FLAG="--build"
fi

if [[ "${1:-}" == "--down" ]]; then
  echo "[down] Stopping all services..."
  docker compose -f docker-compose.prod.yml down
  exit 0
fi

# ── Preflight checks ─────────────────────────────────────────────────────────
echo "============================================"
echo " Carbon BIM — Deploy to bim.ensim.space"
echo "============================================"

[ -f "backend/.env" ] || { echo "ERROR: backend/.env missing. Copy from backend/.env.example"; exit 1; }
[ -f "cloudflared/credentials.json" ] || {
  echo "ERROR: cloudflared/credentials.json missing."
  echo "Run: CF_API_TOKEN=<token> ./deploy/setup-cloudflare.sh"
  exit 1
}

# ── Ensure env vars are available for frontend build ─────────────────────────
export NEXT_PUBLIC_SUPABASE_URL=$(grep SUPABASE_URL backend/.env | head -1 | cut -d= -f2-)
export NEXT_PUBLIC_SUPABASE_ANON_KEY=$(grep SUPABASE_ANON_KEY backend/.env | head -1 | cut -d= -f2-)

# ── Pull latest images / build ───────────────────────────────────────────────
echo ""
echo "[1/3] Building images..."
docker compose -f docker-compose.prod.yml build $BUILD_FLAG

# ── Start services ────────────────────────────────────────────────────────────
echo "[2/3] Starting services..."
docker compose -f docker-compose.prod.yml up -d

# ── Health check ──────────────────────────────────────────────────────────────
echo "[3/3] Waiting for health checks..."
sleep 10

BACKEND_HEALTH=$(docker compose -f docker-compose.prod.yml exec -T backend \
  curl -sf http://localhost:8000/api/health 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status','?'))" 2>/dev/null || echo "pending")

echo ""
echo "============================================"
echo " Services:"
docker compose -f docker-compose.prod.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo " Backend health : $BACKEND_HEALTH"
echo " URL            : https://bim.ensim.space"
echo "============================================"

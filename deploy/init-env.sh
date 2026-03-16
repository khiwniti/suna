#!/usr/bin/env bash
# ============================================================================
# Carbon BIM — Environment Initializer
# Creates backend/.env from the production example template.
# Run this ONCE on your server before starting the stack.
#
# Usage:
#   chmod +x deploy/init-env.sh
#   ./deploy/init-env.sh
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_ENV="$ROOT_DIR/backend/.env"
TEMPLATE="$ROOT_DIR/backend/.env.production.example"

echo "============================================"
echo " Carbon BIM — Environment Setup"
echo "============================================"

if [ -f "$BACKEND_ENV" ]; then
  echo "[skip] backend/.env already exists. Remove it first if you want to regenerate."
  exit 0
fi

echo "[1/4] Copying template → backend/.env ..."
cp "$TEMPLATE" "$BACKEND_ENV"

echo "[2/4] Generating MCP_CREDENTIAL_ENCRYPTION_KEY ..."
ENCRYPT_KEY=$(openssl rand -hex 32)
sed -i "s|MCP_CREDENTIAL_ENCRYPTION_KEY=.*|MCP_CREDENTIAL_ENCRYPTION_KEY=$ENCRYPT_KEY|" "$BACKEND_ENV"

echo "[3/4] Generating KORTIX_ADMIN_API_KEY ..."
ADMIN_KEY=$(openssl rand -hex 32)
sed -i "s|KORTIX_ADMIN_API_KEY=.*|KORTIX_ADMIN_API_KEY=$ADMIN_KEY|" "$BACKEND_ENV"

echo "[4/4] Done."
echo ""
echo "  ✓  backend/.env created with auto-generated security keys."
echo ""
echo "  Next: fill in the REQUIRED values in backend/.env:"
echo ""
echo "    SUPABASE_URL                  — your Supabase project URL"
echo "    SUPABASE_ANON_KEY             — your Supabase anon key"
echo "    SUPABASE_SERVICE_ROLE_KEY     — your Supabase service-role key"
echo "    ANTHROPIC_API_KEY             — your Anthropic API key"
echo "    TAVILY_API_KEY                — your Tavily API key"
echo "    FIRECRAWL_API_KEY             — your Firecrawl API key"
echo ""
echo "  Then run the Cloudflare tunnel setup (needs CF_API_TOKEN):"
echo "    export CF_API_TOKEN=<your-cloudflare-api-token>"
echo "    ./deploy/setup-cloudflare.sh"
echo ""
echo "  Finally, start the stack:"
echo "    docker compose -f docker-compose.prod.yml up -d --build"
echo "============================================"

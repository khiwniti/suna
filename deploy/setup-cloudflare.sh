#!/usr/bin/env bash
# ============================================================================
# Carbon BIM — Cloudflare Tunnel Setup
# Run this ONCE on your server to create the tunnel for bim.ensim.space
#
# Usage:
#   chmod +x deploy/setup-cloudflare.sh
#   CF_API_TOKEN=<your-token> ZONE_NAME=ensim.space ./deploy/setup-cloudflare.sh
# ============================================================================
set -euo pipefail

CF_API_TOKEN="${CF_API_TOKEN:?ERROR: CF_API_TOKEN is required. Export it before running this script.}"
ZONE_NAME="${ZONE_NAME:-ensim.space}"
TUNNEL_NAME="carbon-bim-tunnel"
HOSTNAME="bim.ensim.space"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
CF_DIR="$ROOT_DIR/cloudflared"

echo "============================================"
echo " Carbon BIM — Cloudflare Tunnel Setup"
echo "============================================"
echo " Token   : ${CF_API_TOKEN:0:10}..."
echo " Zone    : $ZONE_NAME"
echo " Hostname: $HOSTNAME"
echo " Tunnel  : $TUNNEL_NAME"
echo "============================================"

# ── 1. Check prerequisites ──────────────────────────────────────────────────
command -v cloudflared >/dev/null 2>&1 || {
  echo "[install] Installing cloudflared..."
  curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg \
    | sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
  echo 'deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared bookworm main' \
    | sudo tee /etc/apt/sources.list.d/cloudflared.list
  sudo apt-get update -qq && sudo apt-get install -y cloudflared
}

command -v jq >/dev/null 2>&1 || sudo apt-get install -y jq -qq

# ── 2. Get Account ID ───────────────────────────────────────────────────────
echo ""
echo "[1/6] Fetching Cloudflare Account ID..."
ACCOUNT_ID=$(curl -s "https://api.cloudflare.com/client/v4/accounts" \
  -H "Authorization: Bearer $CF_API_TOKEN" | jq -r '.result[0].id')

if [ -z "$ACCOUNT_ID" ] || [ "$ACCOUNT_ID" = "null" ]; then
  echo "ERROR: Could not fetch account ID. Check your token permissions."
  exit 1
fi
echo "      Account ID: $ACCOUNT_ID"

# ── 3. Get Zone ID ──────────────────────────────────────────────────────────
echo "[2/6] Fetching Zone ID for $ZONE_NAME..."
ZONE_ID=$(curl -s "https://api.cloudflare.com/client/v4/zones?name=$ZONE_NAME" \
  -H "Authorization: Bearer $CF_API_TOKEN" | jq -r '.result[0].id')

if [ -z "$ZONE_ID" ] || [ "$ZONE_ID" = "null" ]; then
  echo "ERROR: Zone '$ZONE_NAME' not found in your Cloudflare account."
  exit 1
fi
echo "      Zone ID: $ZONE_ID"

# ── 4. Create / reuse tunnel ────────────────────────────────────────────────
echo "[3/6] Creating tunnel '$TUNNEL_NAME'..."
EXISTING=$(curl -s "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/cfd_tunnel?name=$TUNNEL_NAME" \
  -H "Authorization: Bearer $CF_API_TOKEN" | jq -r '.result[0].id // empty')

if [ -n "$EXISTING" ]; then
  echo "      Reusing existing tunnel: $EXISTING"
  TUNNEL_ID="$EXISTING"
else
  CREATE_RESP=$(curl -s -X POST \
    "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/cfd_tunnel" \
    -H "Authorization: Bearer $CF_API_TOKEN" \
    -H "Content-Type: application/json" \
    --data "{\"name\":\"$TUNNEL_NAME\",\"config_src\":\"local\"}")
  TUNNEL_ID=$(echo "$CREATE_RESP" | jq -r '.result.id')
  if [ -z "$TUNNEL_ID" ] || [ "$TUNNEL_ID" = "null" ]; then
    echo "ERROR creating tunnel: $CREATE_RESP"
    exit 1
  fi
  echo "      Created tunnel: $TUNNEL_ID"
fi

# ── 5. Write tunnel credentials ─────────────────────────────────────────────
echo "[4/6] Fetching tunnel token..."
TOKEN_RESP=$(curl -s \
  "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/cfd_tunnel/$TUNNEL_ID/token" \
  -H "Authorization: Bearer $CF_API_TOKEN")
TUNNEL_TOKEN=$(echo "$TOKEN_RESP" | jq -r '.result // empty')

if [ -z "$TUNNEL_TOKEN" ]; then
  echo "ERROR fetching token: $TOKEN_RESP"
  exit 1
fi

# Write credentials file for cloudflared
mkdir -p "$CF_DIR"
cat > "$CF_DIR/credentials.json" <<EOF
{
  "AccountTag":   "$ACCOUNT_ID",
  "TunnelID":     "$TUNNEL_ID",
  "TunnelName":   "$TUNNEL_NAME",
  "TunnelSecret": "$TUNNEL_TOKEN"
}
EOF

# Patch config.yml with real tunnel ID
sed -i "s/TUNNEL_ID_PLACEHOLDER/$TUNNEL_ID/g" "$CF_DIR/config.yml"
echo "      Credentials written to cloudflared/credentials.json"

# ── 6. Create DNS CNAME ──────────────────────────────────────────────────────
echo "[5/6] Creating DNS record $HOSTNAME → $TUNNEL_ID.cfargotunnel.com..."
DNS_RESP=$(curl -s -X POST \
  "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data "{
    \"type\":    \"CNAME\",
    \"name\":    \"$HOSTNAME\",
    \"content\": \"$TUNNEL_ID.cfargotunnel.com\",
    \"ttl\":     1,
    \"proxied\": true
  }")
DNS_OK=$(echo "$DNS_RESP" | jq -r '.success')
if [ "$DNS_OK" = "true" ]; then
  echo "      DNS record created ✓"
else
  # May already exist
  echo "      DNS note: $(echo "$DNS_RESP" | jq -r '.errors[0].message // "already exists"')"
fi

# ── 7. Configure tunnel routes via API ───────────────────────────────────────
echo "[6/6] Configuring tunnel ingress rules..."
curl -s -X PUT \
  "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/cfd_tunnel/$TUNNEL_ID/configurations" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data "{
    \"config\": {
      \"ingress\": [
        {
          \"hostname\": \"$HOSTNAME\",
          \"service\": \"http://nginx:80\"
        },
        {
          \"service\": \"http_status:404\"
        }
      ]
    }
  }" | jq -r 'if .success then "      Ingress rules set ✓" else "      Warning: \(.errors[0].message)" end'

echo ""
echo "============================================"
echo " Setup complete!"
echo " Tunnel ID : $TUNNEL_ID"
echo " URL       : https://$HOSTNAME"
echo ""
echo " Next step: run the stack"
echo "   cd $ROOT_DIR"
echo "   docker compose -f docker-compose.prod.yml up -d --build"
echo "============================================"

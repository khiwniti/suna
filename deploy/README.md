# Carbon BIM — Cloudflare Deployment Guide
## Target: https://bim.ensim.space

### Architecture

```
Internet
  └─► Cloudflare (bim.ensim.space)
        └─► cloudflared tunnel
              └─► nginx:80
                    ├─► /api/*  → backend:8000  (FastAPI)
                    └─► /*      → frontend:3000 (Next.js)
```

### Prerequisites (on your server)

```bash
# Docker + Compose
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# cloudflared (installed automatically by setup script)
```

---

### Step 1 — Configure backend environment

```bash
cp backend/.env.production.example backend/.env
nano backend/.env   # fill in Supabase, Anthropic, Tavily keys
```

---

### Step 2 — Run Cloudflare tunnel setup (once)

```bash
chmod +x deploy/setup-cloudflare.sh

CF_API_TOKEN=JGGCWtxKSJBCoAvjrcMMZq-ZW_ba_dApCurH \
ZONE_NAME=ensim.space \
./deploy/setup-cloudflare.sh
```

This will:
- Create a `carbon-bim-tunnel` in your Cloudflare account
- Write `cloudflared/credentials.json`
- Patch `cloudflared/config.yml` with the tunnel ID
- Create a DNS CNAME `bim.ensim.space → <tunnel-id>.cfargotunnel.com`

---

### Step 3 — Deploy

```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh --build
```

### Useful commands

```bash
# View logs
docker compose -f docker-compose.prod.yml logs -f

# Restart a service
docker compose -f docker-compose.prod.yml restart backend

# Update (rebuild images)
./deploy/deploy.sh --build

# Stop everything
./deploy/deploy.sh --down

# Check backend health
curl https://bim.ensim.space/api/health
```

---

### Services and ports (internal only)

| Service     | Internal port | Exposed? |
|-------------|--------------|----------|
| nginx       | 80           | Yes (→ cloudflared) |
| frontend    | 3000         | No       |
| backend     | 8000         | No       |
| redis       | 6379         | No       |
| cloudflared | —            | No       |

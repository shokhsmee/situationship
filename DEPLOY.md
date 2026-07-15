# Deploying Situationship to your VPS

The whole stack is Dockerized. Production adds a **Caddy** edge that terminates
TLS with an automatic Let's Encrypt certificate, so the Telegram Mini App gets a
real HTTPS domain (no ngrok, no interstitial).

> Replace `game.example.com` with your subdomain and `SERVER_IP` with your VPS IP
> throughout.

---

## 1. Point your domain at the server

Create a DNS **A record** (and AAAA if you have IPv6):

```
game.example.com.   A   SERVER_IP
```

Wait for it to resolve before deploying (Caddy needs it to issue the cert):

```bash
dig +short game.example.com     # should print SERVER_IP
```

---

## 2. Prepare the server (Ubuntu example)

SSH in, then install Docker + the compose plugin and open the web ports:

```bash
# Docker Engine + compose plugin
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER && newgrp docker   # run docker without sudo

# Firewall (if ufw is enabled)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

Ports **80 and 443 must be reachable from the internet** (80 is required for the
ACME HTTP challenge).

---

## 3. Get the code onto the server

From your Mac (the project isn't a git repo yet), rsync it up — excluding local
build artifacts and secrets:

```bash
rsync -avz \
  --exclude '.venv' --exclude 'node_modules' --exclude 'dist' \
  --exclude '.git' --exclude '.env' \
  /Users/macbook/situationship/  user@SERVER_IP:/opt/situationship/
```

(Or push to GitHub and `git clone` on the server — either works.)

---

## 4. Configure `.env` on the server

```bash
cd /opt/situationship
cp .env.example .env
nano .env
```

Set these (the rest can stay default):

| Key | Value |
| --- | --- |
| `POSTGRES_PASSWORD` | a strong password |
| `JWT_SECRET` | a long random string — `openssl rand -hex 32` |
| `TELEGRAM_BOT_TOKEN` | from @BotFather |
| `SITE_DOMAIN` | `game.example.com` |
| `ACME_EMAIL` | your email (Let's Encrypt notices) |

> You do **not** set `TELEGRAM_WEBAPP_URL` manually in production — the prod
> compose derives it as `https://$SITE_DOMAIN` for both the api and the bot.

---

## 5. Deploy

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

This builds all images, starts Postgres/Redis, runs DB migrations + seeds the
demo scenario, launches the API, bot, frontend, and Caddy. Caddy fetches the TLS
cert on first request (give it ~30s).

Check it:

```bash
curl https://game.example.com/health          # {"status":"ok",...}
docker compose -f docker-compose.prod.yml ps   # all Up; bot polling
docker compose -f docker-compose.prod.yml logs -f caddy   # watch cert issuance
```

Open `https://game.example.com` in a browser — the app should load over HTTPS.

---

## 6. Wire up Telegram

1. **@BotFather → /mybots → your bot → Bot Settings → Menu Button → Edit Menu
   Button URL** → `https://game.example.com`
2. That's it — the bot's `/new` lobby buttons and the Menu Button now open the
   Mini App at your domain. Test from your phone: `/new` → pick a case → **Open
   Game**.

---

## 7. Day-2 operations

```bash
# Logs
docker compose -f docker-compose.prod.yml logs -f api bot

# Update after code changes (re-rsync or git pull first)
docker compose -f docker-compose.prod.yml up -d --build

# Restart one service
docker compose -f docker-compose.prod.yml restart bot

# Stop everything
docker compose -f docker-compose.prod.yml down

# Back up the database
docker compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U situationship situationship > backup_$(date +%F).sql
```

---

## Security checklist

- [ ] `JWT_SECRET` is a strong random value (not `1234`).
- [ ] `POSTGRES_PASSWORD` changed from the default.
- [ ] `.env` is never committed (it's in `.gitignore`).
- [ ] Change the seeded admin password (`admin`/`admin`) or delete that user
      after creating your own admin.
- [ ] `DEBUG=false` in production (disables API docs; it's the default).
- [ ] Postgres/Redis are **not** published to the host — only Caddy exposes
      80/443. (Confirm with `docker compose -f docker-compose.prod.yml ps`.)
```

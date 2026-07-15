# 🔍 Situationship

A real-time multiplayer **social-deduction investigation** game. A team of players
is dealt secret roles (Mayor, Doctor, Police, Citizen, Ill Person…), each holding
private **evidence fragments**. Under a timer they share and combine clues to find
the true cause of a hidden event — a crime, a pollution cover-up, an epidemic.

One player is secretly the **Insider**: their evidence is real, but they lie, twist
and steer the team toward the wrong answer.

- **Investigators win** if the team picks the correct final answer.
- **The Insider wins** on a wrong answer or a timeout.
- **Bonus** if the team also unmasks the Insider.

---

## Architecture

```
                         ┌───────────────┐
        Telegram  ─────► │   bot         │  aiogram 3 (long-polling)
        users           │  (aiogram)    │  · lobby create/join
                         └──────┬────────┘  · DM role cards
                                │ REST (/auth/bot, /games)
                                ▼
   Browser / Telegram    ┌───────────────┐   REST + WS    ┌───────────────┐
   Mini App  ──────────► │    nginx      │ ─────────────► │     api       │
                         │ reverse proxy │                │  (FastAPI)    │
                         │  :80          │ ◄───────────── │  async        │
                         └──────┬────────┘                └───┬───────┬───┘
                                │ static                      │       │
                                ▼                             ▼       ▼
                         ┌───────────────┐            ┌──────────┐ ┌────────┐
                         │   frontend    │            │ postgres │ │ redis  │
                         │ (Vue 3 SPA)   │            │  (data)  │ │ state+ │
                         └───────────────┘            └──────────┘ │ pubsub │
                                                                   └────────┘
```

- **api** — FastAPI (async SQLAlchemy 2.0, Pydantic v2, JWT). Owns the
  authoritative game state. The game engine is a phase state machine built from
  pure, unit-tested rule modules.
- **redis** — volatile game state (phase, deadlines, board) for reconnect, plus
  pub/sub so WebSocket workers and the background phase-timer fan events out.
- **frontend** — Vue 3 + Vite + Pinia + Tailwind, served as static files and as a
  Telegram Mini App. Native WebSocket for real-time play.
- **bot** — aiogram 3 for lobby creation, invites and private role delivery; heavy
  UI lives in the Mini App.
- **nginx** — single public entrypoint; serves the SPA and proxies `/api` + `/ws`.

### The game engine (backend/app/services/game_engine)

The rule modules are **pure** (no DB/Redis/clock) so they are trivially testable:

| Module | Responsibility |
| --- | --- |
| `phases.py` | Phase state machine: `LOBBY → INTRO → (EVIDENCE → DISCUSSION)×N → VOTE → INSIDER_GUESS → RESULT` |
| `role_assigner.py` | Random role dealing + insider selection (seedable RNG) |
| `evidence_dealer.py` | Which cards a player owns / may reveal this round |
| `event_processor.py` | Conditional events: `IF trigger THEN effect + narration` |
| `scoring.py` | Outcome resolution + per-player scoring |
| `timer.py` | Redis-backed, server-authoritative phase timers |
| `engine.py` | The only IO module: maps ORM → dataclasses, persists, broadcasts |

Secret state (roles, private cards, the insider flag) is **never broadcast** — it
is delivered only to the owning player via a per-player snapshot.

---

## Quick start (Docker)

```bash
cp .env.example .env
# edit .env: set JWT_SECRET, and TELEGRAM_BOT_TOKEN if you want the bot
docker compose up --build
```

Then open **http://localhost**. The API runs migrations and seeds the demo
scenario automatically on first boot.

Services:

| Service | URL / port |
| --- | --- |
| App (via nginx) | http://localhost |
| API docs | http://localhost/api/v1/docs *(when `DEBUG=true`)* |
| Postgres | internal `postgres:5432` |
| Redis | internal `redis:6379` |

> To run without the bot, leave `TELEGRAM_BOT_TOKEN` blank — the `bot` container
> will exit; every other service runs fine.

### Demo login

The seed creates an admin: **`admin` / `admin`** (change in production). Use it to
reach the Scenario Studio at `/admin`.

---

## Local development (without Docker)

**Backend** (needs Postgres + Redis reachable):

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+asyncpg://situationship:situationship@localhost:5432/situationship
export REDIS_URL=redis://localhost:6379/0
alembic upgrade head
python -m app.scripts.seed
uvicorn app.main:app --reload
```

**Frontend** (proxies `/api` and `/ws` to `localhost:8000`):

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

**Bot**:

```bash
cd bot
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN=... API_BASE_URL=http://localhost:8000/api/v1
python -m bot.main
```

---

## Game flow

1. **Lobby** — join via room code or Telegram deep link; host picks a scenario.
2. **Intro** — cinematic briefing + secret role reveal (3D flip card; insider gets
   a hidden objective).
3. **Evidence** — reveal private cards to the shared board. Combining the right
   clues fires **conditional events** (dramatic popups that unlock evidence, add
   time, drop hints…).
4. **Discussion** — debate; pin string threads between cards on the corkboard.
5. Repeat evidence/discussion for N rounds.
6. **Final answer** — the team votes for a location on the interactive city map.
7. **Insider guess** — optionally vote on who the Insider was.
8. **Result** — truth reconstruction, insider unmasking, scoreboard.

All phase transitions and timers are server-authoritative and pushed over
WebSocket; clients only render.

---

## Scenario Studio (`/admin`)

A writer's studio (admin/writer roles) with tabs for General, Locations
(click-to-place map pins), Roles, Evidence (with a role×evidence coverage matrix),
Events (visual IF/THEN builder), Final Answer, Timers, and one-click **Validate**
(every role ≥2 evidence, a correct answer, ≥1 insider-capable role, no orphan
events). Publish is blocked until validation passes.

---

## Telegram setup

1. Create a bot with [@BotFather](https://t.me/BotFather); put the token in `.env`
   (`TELEGRAM_BOT_TOKEN`).
2. Set `TELEGRAM_WEBAPP_URL` to your public **HTTPS** URL (Telegram requires TLS
   for Mini Apps — use a tunnel like ngrok/cloudflared in dev).
3. In BotFather, set the Menu Button / Mini App URL to the same URL.
4. Bot commands: `/new` (create lobby), `/join CODE`, `/play` (open Mini App),
   `/myrole <game_id>`.

Auth: the Mini App validates Telegram `initData` HMAC (`/auth/telegram`); the bot
authenticates server-to-server with the shared bot token (`/auth/bot`).

---

## Testing

```bash
cd backend
pytest                      # pure engine unit tests (no services needed)
# full suite incl. the end-to-end engine integration test:
DATABASE_URL=... REDIS_URL=... pytest
```

The suite covers the phase machine, role assignment, evidence dealing, event
triggers, scoring, and a full seeded-game integration run (event unlock → vote →
insider catch → scoring), plus per-player secrecy.

---

## Project layout

```
situationship/
├── docker-compose.yml      # api · bot · frontend · postgres · redis · nginx
├── .env.example
├── nginx/nginx.conf        # reverse proxy
├── backend/                # FastAPI + game engine + Alembic + seed
│   └── app/{core,models,schemas,api,ws,services,scripts,tests}
├── bot/                    # aiogram 3 bot
│   └── bot/{handlers,keyboards,middlewares,services}
└── frontend/               # Vue 3 + Vite + Pinia + Tailwind (Mini App)
    └── src/{stores,composables,views,components,i18n,router,api}
```

Everything is strictly modular — one file per model, schema domain, router,
store, and component.

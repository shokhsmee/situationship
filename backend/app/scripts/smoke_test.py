"""Live HTTP smoke test against a running server. Not part of the pytest suite.

Usage: BASE=http://localhost:8009 python -m app.scripts.smoke_test
"""
import os
import sys
import time

import httpx

BASE = os.environ.get("BASE", "http://localhost:8009")


def _wait_for_health(client: httpx.Client) -> None:
    for _ in range(40):
        try:
            if client.get(f"{BASE}/health").status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(0.25)
    raise SystemExit("server never became healthy")


def main() -> None:
    with httpx.Client(timeout=10) as client:
        _wait_for_health(client)

        # Admin login (seeded).
        r = client.post(f"{BASE}/api/v1/auth/login", json={"username": "admin", "password": "admin"})
        assert r.status_code == 200, r.text
        admin_tok = r.json()["access_token"]
        admin_h = {"Authorization": f"Bearer {admin_tok}"}

        # Published scenarios.
        r = client.get(f"{BASE}/api/v1/games/scenarios")
        assert r.status_code == 200, r.text
        scenarios = r.json()
        assert scenarios, "no published scenarios"
        sid = scenarios[0]["id"]

        # Validation + dashboard (admin).
        r = client.get(f"{BASE}/api/v1/admin/scenarios/{sid}/validate", headers=admin_h)
        assert r.status_code == 200, r.text
        assert r.json()["valid"] is True, r.json()
        r = client.get(f"{BASE}/api/v1/admin/scenarios/dashboard", headers=admin_h)
        assert r.status_code == 200, r.text

        # Create a game as admin (becomes host/player 1).
        r = client.post(
            f"{BASE}/api/v1/games",
            headers=admin_h,
            json={"scenario_id": sid, "settings": {"timers": {"intro": 0}}},
        )
        assert r.status_code == 201, r.text
        game = r.json()
        code = game["code"]

        # Two more players register and join.
        stamp = str(int(time.time()))
        tokens = [admin_tok]
        for i in range(2):
            r = client.post(
                f"{BASE}/api/v1/auth/register",
                json={
                    "username": f"smoke_{stamp}_{i}",
                    "password": "pw",
                    "display_name": f"Smoke {i}",
                },
            )
            assert r.status_code == 200, r.text
            tok = r.json()["access_token"]
            tokens.append(tok)
            r = client.post(
                f"{BASE}/api/v1/games/join",
                headers={"Authorization": f"Bearer {tok}"},
                json={"code": code},
            )
            assert r.status_code == 200, r.text

        # Host starts the game.
        r = client.post(f"{BASE}/api/v1/games/{game['id']}/start", headers=admin_h)
        assert r.status_code == 200, r.text
        snap = r.json()
        assert snap["phase"] == "intro", snap
        assert snap["me"]["role"] is not None, "host should have a role"
        assert len(snap["players"]) == 3

        # Unauthorized admin access is rejected.
        r = client.get(
            f"{BASE}/api/v1/admin/scenarios/dashboard",
            headers={"Authorization": f"Bearer {tokens[1]}"},
        )
        assert r.status_code == 403, r.status_code

        print("SMOKE_OK: auth, scenarios, validate, dashboard, create/join/start, RBAC all pass")


if __name__ == "__main__":
    sys.exit(main())

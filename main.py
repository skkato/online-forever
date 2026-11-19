import asyncio
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests
import websockets

# --- Config from environment variables (set these in Render) ---
TOKEN = os.environ.get("DISCORD_TOKEN", "")
STATUS = os.environ.get("DISCORD_STATUS", "online")  # online / dnd / idle
CUSTOM_STATUS = os.environ.get("CUSTOM_STATUS", "Hey!")


# --- Tiny HTTP server so Render (web service) + UptimeRobot see it as alive ---
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"online")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        pass


def start_health_server():
    port = int(os.environ.get("PORT", "10000"))
    HTTPServer(("0.0.0.0", port), HealthHandler).serve_forever()


def check_token():
    if not TOKEN:
        print("DISCORD_TOKEN is not set! Set it in Render > Environment.")
        return False
    r = requests.get(
        "https://discord.com/api/v10/users/@me",
        headers={"Authorization": TOKEN},
        timeout=15,
    )
    if r.status_code != 200:
        print(f"Invalid token (HTTP {r.status_code}). Retrying in 60s...")
        return False
    user = r.json()
    print(f"Logged in as {user['username']} ({user['id']})!")
    return True


def build_activity():
    if not CUSTOM_STATUS:
        return []
    return [
        {
            "name": "Custom Status",
            "type": 4,
            "state": CUSTOM_STATUS,
            "id": "custom",
        }
    ]


async def discord_gateway():
    uri = "wss://gateway.discord.gg/?v=10&encoding=json"
    async with websockets.connect(uri) as ws:
        hello = json.loads(await ws.recv())
        heartbeat_interval = hello["d"]["heartbeat_interval"]

        async def heartbeat():
            while True:
                await asyncio.sleep(heartbeat_interval / 1000)
                await ws.send(json.dumps({"op": 1, "d": None}))

        asyncio.create_task(heartbeat())

        identify = {
            "op": 2,
            "d": {
                "token": TOKEN,
                "properties": {
                    "$os": "windows",
                    "$browser": "chrome",
                    "$device": "pc",
                },
                "presence": {
                    "status": STATUS,
                    "afk": False,
                    "activities": build_activity(),
                },
            },
        }
        await ws.send(json.dumps(identify))

        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            if data.get("op") == 7:  # server asks us to reconnect
                print("Server requested reconnect")
                break


def main():
    threading.Thread(target=start_health_server, daemon=True).start()
    print("Health server started")
    while True:
        try:
            if check_token():
                asyncio.run(discord_gateway())
                print("Connection lost, reconnecting in 5s...")
            else:
                time.sleep(60)
        except Exception as e:
            print("Error, reconnecting in 10s...", e)
            time.sleep(10)


if __name__ == "__main__":
    main()

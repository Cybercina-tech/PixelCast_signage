"""
Simple dashboard WebSocket load probe.

Usage:
  python scripts/loadtest_dashboard_ws.py --url ws://localhost:8000/ws/dashboard/ --token <ACCESS_JWT> --clients 20 --seconds 30
"""

import argparse
import asyncio
import time

try:
    import websockets
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency 'websockets'. Install with: pip install websockets"
    ) from exc


async def run_client(url, token, duration_seconds, result):
    started = time.time()
    ws_url = f"{url}?token={token}"
    try:
        async with websockets.connect(ws_url, ping_interval=20, ping_timeout=20) as ws:
            result["connected"] += 1
            while time.time() - started < duration_seconds:
                try:
                    await asyncio.wait_for(ws.recv(), timeout=1.0)
                    result["messages"] += 1
                except asyncio.TimeoutError:
                    # Keep connection alive with lightweight ping message.
                    await ws.send('{"type":"ping"}')
            result["completed"] += 1
    except Exception:
        result["failed"] += 1


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Base websocket URL without query params.")
    parser.add_argument("--token", required=True, help="JWT access token used for all clients.")
    parser.add_argument("--clients", type=int, default=10, help="Concurrent websocket clients.")
    parser.add_argument("--seconds", type=int, default=20, help="Duration of load probe.")
    args = parser.parse_args()

    result = {"connected": 0, "completed": 0, "failed": 0, "messages": 0}
    tasks = [
        asyncio.create_task(run_client(args.url, args.token, args.seconds, result))
        for _ in range(args.clients)
    ]
    await asyncio.gather(*tasks)

    print("Load probe summary")
    print(f"  connected: {result['connected']}")
    print(f"  completed: {result['completed']}")
    print(f"  failed: {result['failed']}")
    print(f"  messages: {result['messages']}")


if __name__ == "__main__":
    asyncio.run(main())

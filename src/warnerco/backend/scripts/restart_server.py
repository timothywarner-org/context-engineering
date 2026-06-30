"""Force-kill anything on the WARNERCO port, then restart the HTTP server.

Designed for in-class demos where Uvicorn sometimes lingers after Ctrl+C
(common on Windows when the autoreloader is on). Use this when you know
you want a fresh process and don't want to chase down PIDs.

Usage:
    uv run warnerco-restart                # kill port 8000, then start
    uv run warnerco-restart --port 9000    # different port
    uv run warnerco-restart --kill-only    # just free the port, don't start
    uv run warnerco-restart --no-start     # alias for --kill-only

Exits 0 if the port was free or was successfully freed.
Exits 1 if processes on the port could not be killed.
"""

from __future__ import annotations

import argparse
import os
import signal
import socket
import subprocess
import sys
import time


def _port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Return True if something is already listening on (host, port)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        try:
            sock.connect((host, port))
            return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            return False


def _pids_on_port_windows(port: int) -> list[int]:
    """Return PIDs holding `port` according to `netstat -ano`."""
    try:
        out = subprocess.check_output(
            ["netstat", "-ano", "-p", "TCP"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []

    pids: set[int] = set()
    needle = f":{port}"
    for line in out.splitlines():
        if needle not in line or "LISTENING" not in line:
            continue
        parts = line.split()
        if not parts:
            continue
        try:
            pids.add(int(parts[-1]))
        except ValueError:
            continue
    # Never try to kill ourselves
    pids.discard(os.getpid())
    return sorted(pids)


def _pids_on_port_posix(port: int) -> list[int]:
    """Return PIDs holding `port` via lsof (best-effort)."""
    try:
        out = subprocess.check_output(
            ["lsof", "-t", f"-iTCP:{port}", "-sTCP:LISTEN"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []
    pids = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            pid = int(line)
        except ValueError:
            continue
        if pid != os.getpid():
            pids.append(pid)
    return pids


def _kill_pid(pid: int) -> bool:
    """Force-kill `pid`. Returns True if the kill command succeeded."""
    if os.name == "nt":
        # /F = force, /T = also kill child processes (uvicorn reload spawns workers)
        result = subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    try:
        os.kill(pid, signal.SIGKILL)
        return True
    except (ProcessLookupError, PermissionError):
        return False


def free_port(port: int) -> bool:
    """Force-kill anything listening on `port`. Returns True if the port is free after."""
    if not _port_in_use(port):
        print(f"Port {port} is already free.")
        return True

    pids = (
        _pids_on_port_windows(port)
        if os.name == "nt"
        else _pids_on_port_posix(port)
    )

    if not pids:
        # Port shows as in use but we couldn't find a PID. Wait briefly in case
        # it's mid-shutdown, then re-check.
        print(f"Port {port} is in use but no owning PID found. Waiting 2s...")
        time.sleep(2)
        return not _port_in_use(port)

    print(f"Killing {len(pids)} process(es) on port {port}: {pids}")
    all_killed = True
    for pid in pids:
        ok = _kill_pid(pid)
        print(f"  PID {pid}: {'killed' if ok else 'FAILED'}")
        all_killed = all_killed and ok

    # Give the OS a moment to release the socket (TIME_WAIT is short on loopback)
    for _ in range(10):
        if not _port_in_use(port):
            return True
        time.sleep(0.2)

    return not _port_in_use(port)


def start_server(port: int, host: str = "127.0.0.1") -> int:
    """Exec uvicorn with the given host/port. Returns the process exit code."""
    env = os.environ.copy()
    env["PORT"] = str(port)
    print(f"Starting WARNERCO HTTP server on port {port}...")
    # Browse line uses the bind host directly when it's loopback; for 0.0.0.0
    # (all interfaces) point the human at localhost since 0.0.0.0 isn't browsable.
    browse_host = "localhost" if host == "0.0.0.0" else host
    print(f"Dashboard: http://{browse_host}:{port}/dash/")
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", host, "--port", str(port)]
    return subprocess.call(cmd, env=env)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")))
    parser.add_argument(
        "--host",
        default=os.environ.get("HOST", "127.0.0.1"),
        help="Bind host (default 127.0.0.1; use 0.0.0.0 for LAN access).",
    )
    parser.add_argument(
        "--kill-only",
        "--no-start",
        dest="kill_only",
        action="store_true",
        help="Free the port and exit without starting the server.",
    )
    args = parser.parse_args()

    freed = free_port(args.port)
    if not freed:
        print(f"ERROR: could not free port {args.port}.", file=sys.stderr)
        return 1

    if args.kill_only:
        return 0

    return start_server(args.port, args.host)


if __name__ == "__main__":
    sys.exit(main())

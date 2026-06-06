"""WellNest AI Desktop App Launcher"""
import os
import sys
import threading
import webbrowser
import time
import subprocess
import socket


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def open_browser(port, delay=3):
    time.sleep(delay)
    webbrowser.open(f"http://localhost:{port}")


def main():
    port = find_free_port()
    app_dir = os.path.dirname(os.path.abspath(__file__))

    # Start browser after a short delay
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    # Launch Streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        os.path.join(app_dir, "web_v1.py"),
        "--server.port", str(port),
        "--server.headless", "true",
        "--server.address", "127.0.0.1",
        "--browser.gatherUsageStats", "false",
    ]

    proc = subprocess.run(cmd, cwd=app_dir)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())

"""WellNest AI - Desktop App Launcher"""
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


def open_browser(port, delay=2.5):
    time.sleep(delay)
    webbrowser.open(f"http://localhost:{port}")


def main():
    port = find_free_port()
    app_dir = os.path.dirname(os.path.abspath(__file__))

    print("")
    print("========================================")
    print("      WellNest AI  v3.0")
    print("      Personal Wellness Platform")
    print("========================================")
    print("")
    print(f"  >> Open browser: http://localhost:{port}")
    print("  >> Starting server, please wait...")
    print("")

    # Open browser after server is ready
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    # Resolve streamlit path
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        web_path = os.path.join(base_path, "web_v1.py")
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            web_path,
            "--server.port", str(port),
            "--server.headless", "true",
            "--server.address", "127.0.0.1",
            "--browser.gatherUsageStats", "false",
        ]
    else:
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            os.path.join(app_dir, "web_v1.py"),
            "--server.port", str(port),
            "--server.headless", "true",
            "--server.address", "127.0.0.1",
            "--browser.gatherUsageStats", "false",
        ]

    proc = subprocess.run(cmd, cwd=app_dir)
    if proc.returncode != 0:
        print(f"\n  App exited with code: {proc.returncode}")
        input("  Press Enter to close...")
    return proc.returncode


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n  Goodbye!")
        sys.exit(0)

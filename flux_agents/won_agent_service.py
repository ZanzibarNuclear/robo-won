#!/usr/bin/env python3
"""
Controller script for running flux_agents as a Linux service.
This script provides functionality to start, stop, restart, and check the status
of the flux_agents service.
"""

import os
import sys
import signal
import subprocess
import time
from pathlib import Path
from config.settings import PID_FILE, LOG_FILE

# Get the absolute path to the directory containing this script
SCRIPT_DIR = Path(__file__).resolve().parent


def get_pid():
    """Read the PID from the PID file if it exists."""
    try:
        with open(PID_FILE, 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None


def is_running(pid):
    """Check if the process with the given PID is running."""
    if pid is None:
        return False
    try:
        # Sending signal 0 to a process doesn't do anything, but checks if the process exists
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def start():
    """Start the flux_agents service."""
    pid = get_pid()
    if pid and is_running(pid):
        print(f"Flux agents service is already running with PID {pid}")
        return

    # Start the process
    log_path = os.path.abspath(LOG_FILE)
    log_dir = os.path.dirname(log_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Change to the script directory before running
    os.chdir(SCRIPT_DIR)

    # Start the process and redirect output to the log file
    with open(log_path, 'a') as log_file:
        process = subprocess.Popen(
            [sys.executable, 'main.py'],
            stdout=log_file,
            stderr=log_file,
            start_new_session=True
        )

    # Write the PID to the PID file
    with open(PID_FILE, 'w') as f:
        f.write(str(process.pid))

    print(f"Flux agents service started with PID {process.pid}")
    print(f"Logs are being written to {log_path}")


def stop():
    """Stop the flux_agents service."""
    pid = get_pid()
    if not pid:
        print("Flux agents service is not running")
        return

    if not is_running(pid):
        print(
            f"Process with PID {pid} is not running, removing stale PID file")
        os.remove(PID_FILE)
        return

    # Try to terminate gracefully first
    try:
        os.kill(pid, signal.SIGTERM)
        # Wait for the process to terminate
        for _ in range(10):  # Wait up to 10 seconds
            if not is_running(pid):
                break
            time.sleep(1)
        else:
            # If it's still running after 10 seconds, force kill
            os.kill(pid, signal.SIGKILL)
            print(f"Force killed process with PID {pid}")
    except OSError as e:
        print(f"Error stopping process: {e}")
        return

    # Remove the PID file
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

    print("Flux agents service stopped")


def restart():
    """Restart the flux_agents service."""
    stop()
    time.sleep(2)  # Give it a moment to fully stop
    start()


def status():
    """Check the status of the flux_agents service."""
    pid = get_pid()
    if pid and is_running(pid):
        print(f"Flux agents service is running with PID {pid}")
    else:
        print("Flux agents service is not running")


def usage():
    """Print usage information."""
    print(f"Usage: {sys.argv[0]} {{start|stop|restart|status}}")
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        usage()

    command = sys.argv[1].lower()
    if command == "start":
        start()
    elif command == "stop":
        stop()
    elif command == "restart":
        restart()
    elif command == "status":
        status()
    else:
        usage()

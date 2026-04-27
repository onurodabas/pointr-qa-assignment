"""
Behave environment hooks: starts the Flask API before the test run
and shuts it down afterwards.
"""

import subprocess
import time
import requests
import sys
import os

flask_process = None


def before_all(context):
    """Start the Flask API and wait until it's accepting requests."""
    global flask_process

    print("\nStarting Flask API...")

    flask_process = subprocess.Popen(
        [sys.executable, 'app.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.path.dirname(os.path.abspath(__file__)) + '/..'
    )

    context.base_url = 'http://localhost:5000'
    max_attempts = 10

    for attempt in range(max_attempts):
        try:
            # 404 is fine here; we just need a response from the server
            requests.get(f"{context.base_url}/api/sites/test-connection", timeout=1)
            print("API is ready")
            break
        except requests.exceptions.RequestException:
            if attempt == max_attempts - 1:
                print("Failed to start API")
                flask_process.terminate()
                sys.exit(1)
            time.sleep(0.5)


def after_all(context):
    """Shut down the Flask API."""
    global flask_process

    if flask_process:
        print("\nStopping Flask API...")
        flask_process.terminate()
        flask_process.wait()
        print("API stopped")

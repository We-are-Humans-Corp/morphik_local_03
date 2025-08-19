#!/usr/bin/env python3
import subprocess
import os
import time

# Change to project directory
os.chdir('/Users/fedor/PycharmProjects/PythonProject/Morphik_local/Test/Morphik_local')

print("Starting Morphik containers...")

# Try different docker commands
commands = [
    'docker compose -f docker-compose.local.yml up -d',
    'docker-compose -f docker-compose.local.yml up -d',
    '/usr/local/bin/docker compose -f docker-compose.local.yml up -d',
    '/usr/local/bin/docker-compose -f docker-compose.local.yml up -d',
]

for cmd in commands:
    print(f"Trying: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("Success!")
            print(result.stdout)
            break
        else:
            print(f"Failed: {result.stderr}")
    except Exception as e:
        print(f"Error: {e}")
        continue

time.sleep(3)
print("\nChecking running containers:")
subprocess.run("docker ps | grep morphik", shell=True)

print("\nDone! Check:")
print("API: http://localhost:8000/docs")
print("UI: http://localhost:3001")
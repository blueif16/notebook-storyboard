#!/usr/bin/env python3
"""Migrate GEMINI_API_KEY to GOOGLE_API_KEY in .env file"""
from pathlib import Path
import re

def migrate_key():
    env_path = Path(__file__).parent / ".env"
    backup_path = Path(__file__).parent / ".env.backup"

    # Read backup to find GEMINI_API_KEY
    gemini_value = None
    if backup_path.exists():
        with open(backup_path, 'r') as f:
            for line in f:
                match = re.match(r'^GEMINI_API_KEY=(.*)$', line.strip())
                if match:
                    gemini_value = match.group(1)
                    print(f"Found GEMINI_API_KEY in backup")
                    break

    if not gemini_value:
        print("No GEMINI_API_KEY found in backup, nothing to migrate")
        return

    # Read current .env
    with open(env_path, 'r') as f:
        lines = f.readlines()

    # Replace GOOGLE_API_KEY value
    new_lines = []
    updated = False
    for line in lines:
        match = re.match(r'^(GOOGLE_API_KEY=)(.*)$', line.strip())
        if match:
            indent = len(line) - len(line.lstrip())
            new_lines.append(' ' * indent + f"GOOGLE_API_KEY={gemini_value}\n")
            updated = True
            print(f"✓ Updated GOOGLE_API_KEY with value from GEMINI_API_KEY")
        else:
            new_lines.append(line)

    if updated:
        with open(env_path, 'w') as f:
            f.writelines(new_lines)
        print("✓ Migration complete!")
    else:
        print("⚠ GOOGLE_API_KEY not found in .env")

if __name__ == "__main__":
    migrate_key()

#!/usr/bin/env python3
"""
Sync .env file with .env.example structure while preserving existing values.
This script reads your current .env values and merges them with the .env.example structure.
"""

import re
from pathlib import Path


def parse_env_file(file_path):
    """Parse an env file and return a dict of key-value pairs."""
    env_vars = {}
    if not file_path.exists():
        return env_vars

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            # Parse KEY=value
            match = re.match(r'^([A-Z_][A-Z0-9_]*)=(.*)$', line)
            if match:
                key, value = match.groups()
                env_vars[key] = value

    return env_vars


def sync_env_files(example_path, env_path, output_path):
    """Sync .env with .env.example structure, preserving existing values."""
    # Read existing values from .env
    existing_values = parse_env_file(env_path)

    print(f"Found {len(existing_values)} existing values in {env_path.name}")

    # Read .env.example and replace values
    with open(example_path, 'r') as f:
        example_lines = f.readlines()

    new_lines = []
    updated_count = 0

    for line in example_lines:
        stripped = line.strip()

        # Check if this is a key=value line (not commented out)
        match = re.match(r'^([A-Z_][A-Z0-9_]*)=(.*)$', stripped)

        if match:
            key, example_value = match.groups()

            # If we have an existing value for this key, use it
            if key in existing_values:
                # Preserve the indentation from the original line
                indent = len(line) - len(line.lstrip())
                new_lines.append(' ' * indent + f"{key}={existing_values[key]}\n")
                updated_count += 1
                print(f"  ✓ Preserved: {key}")
            else:
                # Keep the example value
                new_lines.append(line)
                print(f"  + New key: {key} (using example value)")
        else:
            # Keep comments and empty lines as-is
            new_lines.append(line)

    # Write the synced file
    with open(output_path, 'w') as f:
        f.writelines(new_lines)

    print(f"\n✓ Synced {updated_count} values to {output_path.name}")
    print(f"✓ Total lines: {len(new_lines)}")


if __name__ == "__main__":
    base_dir = Path(__file__).parent
    example_file = base_dir / ".env.example"
    env_file = base_dir / ".env"
    output_file = base_dir / ".env"

    # Backup existing .env
    if env_file.exists():
        backup_file = base_dir / ".env.backup"
        import shutil
        shutil.copy(env_file, backup_file)
        print(f"✓ Backed up existing .env to .env.backup\n")

    # Sync the files
    sync_env_files(example_file, env_file, output_file)

    print("\n✓ Done! Your .env has been synced with .env.example structure.")
    print("  All your existing values have been preserved.")

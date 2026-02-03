#!/usr/bin/env python3
"""
OBSOLETE: This script is no longer needed.

The AG-UI streaming endpoint has been merged into the main server.
Use run_server.py instead, which now handles both REST API and AG-UI streaming.
"""
import sys

print("="*80)
print("⚠️  WARNING: This script is OBSOLETE")
print("="*80)
print()
print("The AG-UI streaming endpoint has been merged into the main server.")
print("Please use run_server.py instead:")
print()
print("  python run_server.py")
print()
print("The unified server on port 8000 now handles:")
print("  • REST API endpoints (/api/*)")
print("  • AG-UI streaming endpoint (/storybook)")
print()
print("="*80)
sys.exit(1)

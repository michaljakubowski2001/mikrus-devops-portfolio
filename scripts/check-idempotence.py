"""Fail when the production recap does not show a clean, unchanged run."""
import re
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text()
match = re.search(r"^mikrus\s+:\s+ok=(\d+)\s+changed=(\d+)\s+unreachable=(\d+)\s+failed=(\d+)", text, re.M)
if not match or int(match[1]) == 0 or any(int(match[i]) for i in (2, 3, 4)):
    raise SystemExit("Idempotence check failed: expected changed=0, unreachable=0, failed=0")
print("Idempotence verified: changed=0, unreachable=0, failed=0")

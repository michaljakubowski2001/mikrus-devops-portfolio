#!/usr/bin/env bash
set -euo pipefail
response_dir=$(mktemp -d)
trap 'rm -rf "$response_dir"' EXIT
check() {
  local name=$1 url=$2
  local code
  code=$(curl --fail --silent --show-error --max-time 30 --retry 3 --output "$response_dir/$name.json" --write-out '%{http_code}' "$url")
  test "$code" = 200
  printf '%s %s\n' "$code" "$url"
}
# Never follow redirects: unavailable backends can lead to a provider error page returning 200.
check vaultwarden https://srv70-20157.wykr.es/alive
check kuma https://srv70-30157.wykr.es/api/status-page/portfolio
check grafana https://amy157-20158.mikrus.cloud/api/health
check heartbeats https://srv70-30157.wykr.es/api/status-page/heartbeat/portfolio
python3 - "$response_dir" <<'PY'
import json
import sys
from datetime import datetime
from pathlib import Path
root = Path(sys.argv[1])
def read(name):
    return json.loads((root / f'{name}.json').read_text())
assert isinstance(read('vaultwarden'), str)
datetime.fromisoformat(read('vaultwarden').replace('Z', '+00:00'))
assert read('grafana')['database'] == 'ok'
assert read('kuma')['config']['slug'] == 'portfolio'
assert len(read('kuma')['publicGroupList'][0]['monitorList']) == 4
heartbeats = read('heartbeats')['heartbeatList']
assert len(heartbeats) == 4
assert all(entries and entries[-1]['status'] == 1 for entries in heartbeats.values())
print('Application response bodies verified; provider error pages are rejected.')
PY

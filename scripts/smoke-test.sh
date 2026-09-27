#!/usr/bin/env bash
set -euo pipefail
for url in \
  https://srv70-20157.wykr.es/alive \
  https://srv70-30157.wykr.es/status/portfolio \
  https://amy157-20158.mikrus.cloud/api/health; do
  code=$(curl --fail --silent --show-error --location --max-time 30 --retry 3 --output /dev/null --write-out '%{http_code}' "$url")
  test "$code" = 200
  printf '%s %s\n' "$code" "$url"
done

# Verification record

Status: **implementation prepared; deployment is blocked on host-change authorization**.

## Observed on 2026-09-27

- SSH over IPv4 to `amy157.mikrus.xyz:10157` succeeds.
- Ubuntu 24.04.4 LTS, 2,048 MiB RAM, 25 GB root filesystem, approximately 22 GB available.
- Docker is not installed. Ubuntu offers `docker.io=29.1.3-0ubuntu3~24.04.2`.
- Forwarded TCP/UDP ports: 20157 and 30157 (confirmed from the server MOTD).
- IPv6: `2a01:4f9:3070:1984::157`.
- Existing provider services listen on 40455 and 40456; they are outside project scope.
- UFW was already inactive; nftables contains accept policies. Neither was changed.
- Local `ansible-lint --offline`: production profile, zero failures and warnings.
- Deploy key and Vault password have been created locally and stored as GitHub Actions secrets.

## Pending evidence

Do not treat these as passed until results are recorded:

- Docker installation and deployment-key authorization.
- Initial Ansible deployment, container readiness and memory measurements.
- Second deployment with `changed=0`, `unreachable=0`, `failed=0`.
- External HTTPS checks with certificate validation enabled.
- A successful GitHub Actions **deploy** job (lint alone is insufficient).
- Screenshots of the actual Grafana dashboard and Kuma status page.

The workflow keeps deployment disabled until repository variable `DEPLOY_ENABLED` is set to `true`.

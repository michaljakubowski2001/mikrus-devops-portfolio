# Verification record

Verified on **2026-09-27** against the actual Mikrus VPS.

## Server and scope

- Ubuntu 24.04.4 LTS, 2,048 MiB RAM, 25 GB root filesystem.
- SSH over IPv4: `amy157.mikrus.xyz:10157`.
- Forwarded TCP/UDP ports: 20157 and 30157, confirmed from the server MOTD.
- IPv6: `2a01:4f9:3070:1984::157`.
- With explicit owner authorization, installed `docker.io=29.1.3-0ubuntu3~24.04.2` and added a restricted dedicated Ed25519 deployment key to root's authorized keys.
- Application configuration and data: `/opt/devops-portfolio`.
- Existing provider services on 40455 and 40456 remain unchanged. Port 40455 is scraped read-only for correct LXC VPS metrics.
- UFW was already inactive before deployment and remains unchanged. No firewall was disabled.

## Functional checks

- All six project containers run; Vaultwarden and Kuma report Docker health status `healthy`.
- All five private application endpoints and all three Nginx routes pass Ansible readiness checks.
- Public HTTPS checks use curl with normal certificate validation and no redirect following:
  - Vaultwarden `/alive`: HTTP 200, valid timestamp JSON.
  - Grafana `/api/health`: HTTP 200, `database=ok`.
  - Kuma `/api/status-page/portfolio`: HTTP 200, expected status page and four monitors.
  - Kuma `/api/status-page/heartbeat/portfolio`: all four latest statuses equal 1 (UP).
- Public Vaultwarden `/admin` returns HTTP 403.
- Prometheus scrapes four targets: VPS exporter, project exporter, Prometheus and Grafana. All must report UP for deployment to pass.
- The host memory metric must match Ansible's host memory fact within 64 MiB, detecting the LXCFS container-metric pitfall.
- Browser screenshots show the real Grafana dashboard, Kuma status page and Vaultwarden login.

## Automation checks

- Local ansible-lint: production profile, zero violations.
- Ansible syntax checks passed for both playbooks.
- Second application deployment: `changed=0`, `unreachable=0`, `failed=0`.
- Deployment CI runs the playbook twice and checks the second recap automatically.
- Plaintext generated credentials and private keys were checked against tracked files; none were found. The committed Vault file contains encrypted ciphertext only.
- Full GitHub Actions deployment run: [36336997376](https://github.com/michaljakubowski2001/mikrus-devops-portfolio/actions/runs/36336997376). The linked logs include both Ansible recaps and the public HTTPS checks.

## Resource sample

A point-in-time Docker snapshot after startup (usage varies):

| Container | Used memory | Limit |
| --- | ---: | ---: |
| Nginx | 2 MiB | 64 MiB |
| Kuma | 221 MiB | 384 MiB |
| Grafana | 335 MiB | 512 MiB |
| Vaultwarden | 30 MiB | 256 MiB |
| Prometheus | 42 MiB | 256 MiB |
| node_exporter | 11 MiB | 64 MiB |

Approximately 17 GB of disk remained free. Prometheus has 7-day retention with a 2 GB block-storage ceiling. WAL/head data and temporary compaction need additional space. Logs rotate at 3 × 10 MB per container.

## Failures found and fixed

1. Grafana startup exceeded the initial readiness budget: increased its memory ceiling, disabled automatic plugin installation and allowed longer initialization. The overall container budget stayed at 1,536 MiB.
2. Kuma 2 requires explicit database selection: configured SQLite and waited for the asynchronous Socket.IO handshake before bootstrap requests.
3. Read-only Nginx could not create FastCGI/uWSGI/SCGI temporary directories: moved all temporary paths to its bounded `/tmp` tmpfs.
4. Provider error redirects ended in HTTP 200: removed redirect following and added semantic JSON checks to prevent false positives.
5. Containerized node_exporter reported 64 MiB rather than the VPS's 2 GiB because of LXCFS: separated container and VPS scrape jobs and validated the VPS memory metric.

## Operational limits

- HTTPS terminates at the provider; the provider-to-origin hop uses HTTP. This is a portfolio demo, not a production password vault.
- One host, no HA, no configured off-host backup or external alert destination.
- Kuma checks originate on the same host; GitHub Actions additionally checks public endpoints during deployment.
- Docker limits are ceilings, not reservations. The resource sample does not establish a production capacity guarantee.
- The deploy key runs Ansible as root; `restrict` disables forwarding and PTY but does not sandbox commands.

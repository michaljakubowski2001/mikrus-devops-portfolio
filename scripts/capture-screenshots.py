"""Capture real, public service pages with a locally installed Chrome browser."""
from pathlib import Path
from playwright.sync_api import sync_playwright

output = Path('docs/screenshots')
output.mkdir(parents=True, exist_ok=True)
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 1000}, device_scale_factor=1)
    for name, url in [
        ('grafana', 'https://amy157-20158.mikrus.cloud/d/mikrus-infrastructure?orgId=1&from=now-30m&to=now&timezone=browser'),
        ('uptime-kuma', 'https://srv70-30157.wykr.es/status/portfolio'),
        ('vaultwarden', 'https://srv70-20157.wykr.es/'),
    ]:
        response = page.goto(url, wait_until='networkidle', timeout=60000)
        if not response or response.status != 200:
            raise RuntimeError(f'{name}: unexpected response')
        page.wait_for_timeout(8000)
        if 'error-wykres' in page.url or 'error-mikrus' in page.url:
            raise RuntimeError(f'{name}: provider error page')
        page.screenshot(path=str(output / f'{name}.png'), full_page=True)
        print(f'{name}: {page.title()}')
    browser.close()

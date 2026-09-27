"""Resolve explicitly versioned Docker Hub images to immutable manifest digests."""
import json
import urllib.request
from pathlib import Path
import yaml

class IndentedDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


path = Path('inventories/production/group_vars/all/main.yml')
data = yaml.safe_load(path.read_text())
for name, reference in data['images'].items():
    version = reference.split('@')[0]
    repository, tag = version.rsplit(':', 1)
    if '/' not in repository:
        repository = 'library/' + repository
    url = f'https://auth.docker.io/token?service=registry.docker.io&scope=repository:{repository}:pull'
    with urllib.request.urlopen(url, timeout=30) as response:
        token = json.load(response)['token']
    request = urllib.request.Request(
        f'https://registry-1.docker.io/v2/{repository}/manifests/{tag}',
        headers={'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.list.v2+json'},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        digest = response.headers['Docker-Content-Digest']
    data['images'][name] = f'{version}@{digest}'
    print(f'{name}: {version}@{digest}')
path.write_text('---\n' + yaml.dump(data, Dumper=IndentedDumper, sort_keys=False, width=180))

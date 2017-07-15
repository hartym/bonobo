import os
from base64 import b64decode

import requests
from appdirs import user_cache_dir

from bonobo.util.iterators import tuplize

path = user_cache_dir('bonobo/examples/datasets')
GITHUB_REF_URL = '/repos/{owner}/{repo}/git/refs/{ref}'


def _extract_files():
    resp = requests.get(GITHUB_REF_URL.format(owner='python-bonobo', repo='bonobo', ref='master'))
    print(resp)


def _findtree(tree, name):
    for entry in tree.get('tree'):
        if entry['path'] == name:
            return entry
    raise ValueError('not found')


@tuplize
def _filtertree(tree):
    for entry in tree.get('tree'):
        if not entry['path'].endswith('.py') and entry['type'] == 'blob':
            yield entry


if __name__ == '__main__':
    os.makedirs(path, exist_ok=True)

    resp = requests.get('https://api.github.com/repos/python-bonobo/bonobo/git/refs/heads/master').json()
    resp = requests.get(resp['object']['url']).json()
    resp = requests.get(resp['tree']['url']).json()
    resp = requests.get(_findtree(resp, 'bonobo')['url']).json()
    resp = requests.get(_findtree(resp, 'examples')['url']).json()
    resp = requests.get(_findtree(resp, 'datasets')['url']).json()

    for blob in _filtertree(resp):
        resp = requests.get(blob['url']).json()
        blob_path = os.path.join(path, blob['path'])
        with open(blob_path, 'wb+') as f:
            f.write(b64decode(resp['content']))
            print('Wrote ' + blob_path)
